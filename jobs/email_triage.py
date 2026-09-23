"""Email triage job: Jev decides every email, the LLM drafts replies only where needed.

The same logic as notebook 04, packaged as a script you can schedule.

    uv run python jobs/email_triage.py                          # sample inbox (data/inbox.jsonl)
    uv run python jobs/email_triage.py --draft-replies          # + LLM reply drafts for the "reply" bucket
    uv run python jobs/email_triage.py --source imap --limit 50 # your real mailbox, READ-ONLY

cron (weekdays, every 30 minutes, 8:00-18:00):
    */30 8-18 * * 1-5  cd /path/to/jev-zero-to-agent && uv run python jobs/email_triage.py --source imap --draft-replies

Safety: IMAP is opened read-only (select readonly=True, BODY.PEEK[]), so nothing is marked read, moved
or deleted. The job never sends email. Drafts go into the report for a human to use.
"""

import argparse
import email as emaillib
import imaplib
import json
import os
import sys
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from email.header import decode_header, make_header
from pathlib import Path

try:
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))
except Exception:
    pass

import httpx
import httpx2
from openai import OpenAI

BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "set-me")
MODEL = os.environ.get("MODEL", "openai/gpt-6-luna")
JEV_BACKEND = os.environ.get("JEV_BACKEND", "typesafe").strip().lower()
JEV_MODEL = os.environ.get("JEV_MODEL", "~typesafe/jev-latest")
JEV_BASE_URL = os.environ.get("TYPESAFE_BASE_URL", "https://openrouter.ai/api")
JEV_API_KEY = os.environ.get("TYPESAFE_API_KEY") or API_KEY
VERIFY_SSL = os.environ.get("VERIFY_SSL", "true").strip().lower() not in ("false", "0", "no")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY, http_client=httpx.Client(verify=VERIFY_SSL))
if JEV_BACKEND == "adapter":
    from system_one_adapter import Choice, Noul, Score, SystemOneAdapterClient
    from system_one_adapter.providers.openai import OpenAIProvider

    jev = SystemOneAdapterClient(
        structured_outputs=True, llm_answer_mode="probabilities", normalize_probabilities=True,
        n_retry_malformed_structure=2,
        model=OpenAIProvider(MODEL, base_url=BASE_URL, api_key=API_KEY, api="chat_completions"))
else:
    from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

    jev = TypeSafeClient(api_key=JEV_API_KEY, base_url=JEV_BASE_URL, model=JEV_MODEL,
                         http_client=httpx2.Client(verify=VERIFY_SSL))

CATEGORIES = {
    "action_request": "a person asks me to do, review, approve, answer or decide something",
    "meeting": "scheduling, invitations, moving or preparing for a meeting",
    "billing": "invoices, receipts, charges, payments, price changes",
    "newsletter": "marketing, promotions, digests, webinars or product news sent to many people",
    "security_alert": "a genuine security notice from a system I use: sign-ins, MFA, vulnerabilities, "
                      "certificates, endpoint compliance",
    "phishing": "a scam: fake login pages, lookalike domains, gift-card requests, asks for credentials or secrecy",
    "personal": "family, friends, neighbours, hobbies",
    "notification": "automated FYI from tools: builds, deliveries, tickets, resolved alerts",
}
QUESTIONS = {
    "category": Choice(instructions="What kind of email is this?", criteria=CATEGORIES),
    "needs_reply": Noul(
        instructions="Does the sender expect me to write back to them personally?",
        criteria={"true": "a direct question or request to me that needs my written answer",
                  "false": "automated, broadcast, FYI, a scam, or no answer expected"}),
    "urgency": Score(instructions="How soon must I act on this email?",
                     criteria=["no action needed / whenever", "this week", "today", "within the hour"]),
}
REVIEW_BELOW = 0.6


def load_sample(limit):
    rows = [json.loads(line) for line in Path("data/inbox.jsonl").read_text().splitlines() if line.strip()]
    return rows[:limit]


def load_imap(limit, folder="INBOX"):
    """Newest `limit` messages, read-only. Needs IMAP_HOST, IMAP_USER, IMAP_PASSWORD (an app password)."""
    box = imaplib.IMAP4_SSL(os.environ["IMAP_HOST"])
    box.login(os.environ["IMAP_USER"], os.environ["IMAP_PASSWORD"])
    box.select(folder, readonly=True)
    _, data = box.search(None, "ALL")
    out = []
    for num in data[0].split()[-limit:][::-1]:
        _, msg_data = box.fetch(num, "(BODY.PEEK[])")
        msg = emaillib.message_from_bytes(msg_data[0][1])
        body = ""
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True) or b""
                body = payload.decode(part.get_content_charset() or "utf-8", "replace")
                break
        out.append({"id": num.decode(), "from": str(make_header(decode_header(msg.get("From", "")))),
                    "subject": str(make_header(decode_header(msg.get("Subject", "")))), "body": body[:4000]})
    box.logout()
    return out


def triage(e):
    r = jev.system_one({"from": e["from"], "subject": e["subject"], "body": e["body"]}, QUESTIONS)
    out = {"id": e["id"], "from": e["from"], "subject": e["subject"],
           "category": r.choices["category"].choice, "category_conf": round(r.choices["category"].confidence, 2),
           "needs_reply": round(r.nouls["needs_reply"].noul, 2), "urgency": round(r.scores["urgency"].score, 2)}
    if out["category"] == "phishing":
        out["bucket"] = "quarantine"
    elif out["category_conf"] < REVIEW_BELOW:
        out["bucket"] = "review"
    elif out["needs_reply"] >= 0.5:
        out["bucket"] = "reply"
    else:
        out["bucket"] = "file:" + out["category"]
    return out


def draft(e):
    resp = client.chat.completions.create(model=MODEL, messages=[
        {"role": "system", "content": "Draft a short, friendly reply (max 4 sentences) on my behalf. Don't invent "
                                      "facts; use [placeholders] for anything you don't know. No subject line."},
        {"role": "user", "content": f"From: {e['from']}\nSubject: {e['subject']}\n\n{e['body']}"}])
    return resp.choices[0].message.content


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--source", choices=["sample", "imap"], default="sample")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--draft-replies", action="store_true", help="LLM drafts for emails that need a reply")
    ap.add_argument("--out", default="reports")
    ap.add_argument("--workers", type=int, default=8, help="parallel Jev calls (limit: 1,200 requests/min)")
    args = ap.parse_args()

    if args.source == "imap" and not os.environ.get("IMAP_HOST"):
        sys.exit("--source imap needs IMAP_HOST, IMAP_USER and IMAP_PASSWORD in .env")
    emails = load_imap(args.limit) if args.source == "imap" else load_sample(args.limit)
    by_id = {e["id"]: e for e in emails}

    t0 = time.perf_counter()
    with ThreadPoolExecutor(args.workers) as pool:
        results = list(pool.map(triage, emails))
    decided = time.perf_counter() - t0

    drafts = {}
    if args.draft_replies:
        to_reply = [r for r in results if r["bucket"] == "reply"]
        with ThreadPoolExecutor(4) as pool:
            drafts = dict(zip([r["id"] for r in to_reply], pool.map(lambda r: draft(by_id[r["id"]]), to_reply)))
    for r in results:
        if r["id"] in drafts:
            r["draft"] = drafts[r["id"]]

    stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    out = Path(args.out)
    out.mkdir(exist_ok=True)
    counts = Counter(r["bucket"] for r in results)
    lines = [f"# Inbox triage - {stamp}", "",
             f"{len(results)} emails decided by Jev in {decided:.1f} s; {len(drafts)} reply drafts by {MODEL}.", ""]
    for bucket in ["quarantine", "review", "reply"]:
        rows = sorted([r for r in results if r["bucket"] == bucket], key=lambda r: -r["urgency"])
        lines += [f"## {bucket} ({len(rows)})", ""]
        for r in rows:
            lines.append(f"- **{r['subject']}** - {r['from']} - urgency {r['urgency']:.1f}")
            if "draft" in r:
                lines.append("  > " + r["draft"].replace("\n", "\n  > "))
        lines.append("")
    lines += ["## filed", ""] + [f"- {b[5:]}: {n}" for b, n in sorted(counts.items()) if b.startswith("file:")]
    (out / f"triage-{stamp}.md").write_text("\n".join(lines) + "\n")
    (out / f"triage-{stamp}.json").write_text(json.dumps(results, indent=2))

    print(f"triaged {len(results)} emails in {decided:.1f} s -> {dict(counts)}")
    print(f"report: {out / f'triage-{stamp}.md'}")


if __name__ == "__main__":
    main()
