"""Jev Playground: every use case from the course behind a click-through UI.

    uv sync --extra ui
    uv run --extra ui python app.py          # then open http://127.0.0.1:7860

Self-contained on purpose: it condenses the questions from notebooks 01, 02, 04, 05, 06 and 07 rather than
importing them, so you can read (and copy) this one file. Tools are read-only or dry-run; nothing is executed.
"""

import ast
import json
import os
import re
import time
from urllib.parse import urlparse

import gradio as gr
import httpx
import httpx2
from openai import OpenAI

try:
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))
except Exception:
    pass

# ---------------------------------------------------------------- config (same as the notebooks)
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


def ask_jev(state, questions):
    t0 = time.perf_counter()
    r = jev.system_one(state, questions)
    return r, 1000 * (time.perf_counter() - t0)


def chat(prompt, system="Be concise."):
    r = client.chat.completions.create(model=MODEL, messages=[
        {"role": "system", "content": system}, {"role": "user", "content": prompt}])
    return r.choices[0].message.content


def answers_json(r):
    out = {}
    for k, a in r.answers.items():
        if a.type == "noul":
            out[k] = {"P(yes)": round(a.noul, 3)}
        elif a.type == "choice":
            out[k] = {"choice": a.choice, "confidence": round(a.confidence, 3),
                      "probabilities": {o: round(p, 3) for o, p in sorted(a.probabilities.items(), key=lambda kv: -kv[1])}}
        else:
            out[k] = {"score": round(a.score, 2), "confidence": round(a.confidence, 3),
                      "legend": {str(i): v for i, v in (a.legend or {}).items()}}
    return out


# ---------------------------------------------------------------- 1. playground (notebook 01)
def playground(state, qtype, instructions, options):
    opts = [o.strip() for o in options.splitlines() if o.strip()]
    if qtype == "Noul (yes/no)":
        q = Noul(instructions=instructions)
    elif qtype == "Choice (pick one)":
        if len(opts) < 2:
            return {"error": "Choice needs at least 2 options (one per line, optionally 'name: description')"}, ""
        q = Choice(instructions=instructions,
                   criteria={o.split(":", 1)[0].strip(): (o.split(":", 1)[1].strip() if ":" in o else None) for o in opts})
    else:
        if not 2 <= len(opts) <= 10:
            return {"error": "Score needs 2-10 levels, lowest first, one per line"}, ""
        q = Score(instructions=instructions, criteria=opts)
    try:
        state_val = json.loads(state) if state.strip().startswith(("{", "[")) else state
    except json.JSONDecodeError:
        state_val = state
    r, ms = ask_jev(state_val, {"answer": q})
    return answers_json(r), f"{ms:.0f} ms  |  model {r.model}"


# ---------------------------------------------------------------- 2. email triage (notebook 04)
CATEGORIES = {
    "action_request": "a person asks me to do, review, approve, answer or decide something",
    "meeting": "scheduling, invitations, moving or preparing for a meeting",
    "billing": "invoices, receipts, charges, payments, price changes",
    "newsletter": "marketing, promotions, digests, webinars or product news sent to many people",
    "security_alert": "a genuine security notice from a system I use",
    "phishing": "a scam: fake login pages, lookalike domains, gift-card requests, asks for credentials or secrecy",
    "personal": "family, friends, neighbours, hobbies",
    "notification": "automated FYI from tools: builds, deliveries, tickets, resolved alerts",
}


def email_triage(sender, subject, body, want_draft):
    r, ms = ask_jev({"from": sender, "subject": subject, "body": body}, {
        "category": Choice(instructions="What kind of email is this?", criteria=CATEGORIES),
        "needs_reply": Noul(instructions="Does the sender expect me to write back to them personally?",
                            criteria={"true": "a direct question or request to me that needs my written answer",
                                      "false": "automated, broadcast, FYI, a scam, or no answer expected"}),
        "urgency": Score(instructions="How soon must I act on this email?",
                         criteria=["no action needed / whenever", "this week", "today", "within the hour"]),
    })
    cat, reply = r.choices["category"].choice, r.nouls["needs_reply"].noul
    bucket = "quarantine" if cat == "phishing" else "review" if r.choices["category"].confidence < 0.6 \
        else "reply" if reply >= 0.5 else f"file: {cat}"
    draft = ""
    if want_draft and bucket == "reply":
        draft = chat(f"From: {sender}\nSubject: {subject}\n\n{body}",
                     system="Draft a short, friendly reply (max 4 sentences). Use [placeholders] for unknowns.")
    return answers_json(r), f"bucket: {bucket}   ({ms:.0f} ms)", draft


# ---------------------------------------------------------------- 3. SMS scam shield (notebook 05)
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "t.me", "is.gd", "ow.ly"}
BRANDS = ["acme", "paypal", "apple", "netflix", "usps", "dhl", "ezpass", "coinbase", "irs", "microsoft", "parcel", "toll"]
LURES = ["verify", "secure", "login", "unlock", "update", "confirm", "redeliver", "refund", "billing", "pay", "-"]
URL_RE = re.compile(r"(?:https?://)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/[^\s]*)?", re.I)


def signals(text):
    hosts = [urlparse(u if "://" in u else "http://" + u).hostname or "" for u in URL_RE.findall(text)]
    sig = {"shortener": any(h in SHORTENERS for h in hosts),
           "lookalike_domain": any(any(b in h.replace("1", "l").replace("0", "o") for b in BRANDS)
                                   and any(w in h for w in LURES) for h in hosts),
           "asks_payment": bool(re.search(r"\b(pay|fee|\$\d|gift card|bank details|seed phrase)", text, re.I)),
           "deadline_pressure": bool(re.search(r"\b(now|today|immediately|within \d+ ?h|final notice)\b", text, re.I))}
    sig["score"] = round((2 * sig["lookalike_domain"] + sig["shortener"] + sig["asks_payment"]
                          + sig["deadline_pressure"]) / 5, 2)
    return sig


def sms_shield(text, want_explain):
    sig = signals(text)
    r, ms = ask_jev({"sms": text, "code_signals": sig}, {
        "is_scam": Noul(instructions="Is this text message a scam or fraud attempt?",
                        criteria={"true": "tries to get money, credentials, codes or a click through deception",
                                  "false": "a genuine message from a known contact, service or business"}),
        "scam_type": Choice(instructions="Which scam playbook does it follow?", criteria={
            "bank": "fake bank/payment/tax alert", "delivery": "fake parcel fee", "prize": "you won, pay shipping",
            "job": "pay-to-start job", "toll": "unpaid toll", "tech_support": "fake virus or locked account",
            "family_impersonation": "'hi mum, new number'", "crypto_investment": "guaranteed returns",
            "none": "not a scam"}),
    })
    risk = round(0.7 * r.nouls["is_scam"].noul + 0.3 * sig["score"], 2)
    verdict = "BLOCK" if risk >= 0.7 else "WARN" if risk >= 0.4 else "ALLOW"
    why = ""
    if want_explain and verdict != "ALLOW":
        why = chat(f"Text: {text}\nAnalysis: risk {risk}, type {r.choices['scam_type'].choice}, signals {sig}",
                   system="In 2-3 plain sentences for a non-technical person: is it a scam, the red flags, what to do.")
    return {"risk": risk, "verdict": verdict, "code_signals": sig, **answers_json(r)}, f"{verdict}  ({ms:.0f} ms)", why


# ---------------------------------------------------------------- 4. code vuln hunter (notebook 06)
CWES = {
    "CWE-89": "SQL injection: untrusted input formatted into a SQL query",
    "CWE-78": "OS command injection: untrusted input in os.system / shell=True",
    "CWE-22": "path traversal: untrusted filename joined to a directory without checking",
    "CWE-798": "hardcoded credentials: secrets, API keys or passwords in source",
    "CWE-502": "unsafe deserialization: pickle/yaml.load on untrusted data",
    "CWE-327": "weak crypto: md5/sha1 for passwords",
    "CWE-79": "cross-site scripting: untrusted input in HTML without escaping",
    "none": "no vulnerability: parameterized, escaped, validated, list-form subprocess, env-var secrets",
}


def vuln_hunt(source):
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [[f"syntax error: {exc}", "", "", "", ""]]
    lines, chunks, module = source.splitlines(), [], []
    for node in tree.body:
        seg = "\n".join(lines[node.lineno - 1: node.end_lineno])
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            chunks.append((node.name, seg))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            module.append(seg)
    if module:
        chunks.append(("<module>", "\n".join(module)))
    rows = []
    for name, code in chunks:
        r, _ = ask_jev({"code": code}, {
            "cwe": Choice(instructions="Which vulnerability class does this code contain? Answer none if safe.",
                          criteria=CWES),
            "exploitable": Noul(instructions="Is this code really vulnerable, rather than a safe look-alike?"),
            "severity": Score(instructions="If exploited, how bad is it?",
                              criteria=["informational", "low", "medium", "high", "critical"])})
        cwe, p = r.choices["cwe"].choice, r.nouls["exploitable"].noul
        rows.append([name, cwe, f"{p:.2f}", f"{r.scores['severity'].score:.1f}",
                     "FLAG" if cwe != "none" and p >= 0.5 else ""])
    return rows


# ---------------------------------------------------------------- 5. guarded agent (notebooks 03 + 07)
DENY = {"recursive delete of root/home": r"rm\s+-[a-z]*r[a-z]*f?\s+(/|~|\$HOME)(\s|$)",
        "pipe remote script to shell": r"(curl|wget)[^|]*\|\s*(ba|z)?sh",
        "read private keys/secrets": r"(id_rsa|id_ed25519|\.env\b|\.aws/credentials)"}
TOOLS = [{"type": "function", "function": {
    "name": "run_shell", "description": "Run a shell command in the project directory (DRY-RUN: never executes).",
    "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}}]


def guard(command, request):
    for why, pat in DENY.items():
        if re.search(pat, command, re.I):
            return f"BLOCK (ACL: {why})"
    try:
        r, _ = ask_jev({"proposed_command": command, "user_request": request}, {
            "verdict": Choice(instructions="Should an autonomous coding agent run the proposed_command without asking?",
                              criteria={"allow": "read-only or clearly requested and scoped to the project",
                                        "ask": "changes or deletes things; a human should confirm",
                                        "block": "destructive beyond the project, unrequested, or leaks data"}),
            "exfiltration": Noul(instructions="Does the proposed_command send secrets or private data to an outside host?")})
    except Exception as exc:  # fail closed
        return f"ASK (guard unavailable: {type(exc).__name__})"
    v = r.choices["verdict"].choice
    return "BLOCK (exfiltration)" if r.nouls["exfiltration"].noul > 0.5 else v.upper()


def guarded_agent(request):
    trace = [f"USER: {request}"]
    messages = [{"role": "system", "content": "You are a coding agent. Carry out requests with run_shell, one command "
                                              "per call. A safety layer reviews every command; just attempt it."},
                {"role": "user", "content": request}]
    for step in range(1, 7):
        msg = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS).choices[0].message
        if not msg.tool_calls:
            trace.append(f"[{step}] FINAL: {msg.content}")
            break
        messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [
            {"id": t.id, "type": "function", "function": {"name": t.function.name, "arguments": t.function.arguments}}
            for t in msg.tool_calls]})
        for t in msg.tool_calls:
            cmd = json.loads(t.function.arguments or "{}").get("command", "")
            verdict = guard(cmd, request)
            result = {"dry_run": True, "would_run": cmd} if verdict == "ALLOW" else {"blocked": verdict}
            trace.append(f"[{step}] run_shell({cmd!r}) -> guard {verdict}")
            messages.append({"role": "tool", "tool_call_id": t.id, "content": json.dumps(result)})
    return "\n".join(trace)


# ---------------------------------------------------------------- 6. the race (notebook 02)
def race(text, question):
    r, jev_ms = ask_jev(text, {"q": Noul(instructions=question)})
    t0 = time.perf_counter()
    llm = chat(f"{question} Answer yes or no.\n\n{text}")
    llm_ms = 1000 * (time.perf_counter() - t0)
    verdict = (f"Jev was {llm_ms / jev_ms:.1f}x faster" if JEV_BACKEND != "adapter"
               else "JEV_BACKEND=adapter: the 'Jev' side is your LLM via the adapter - set typesafe for the real race")
    return (f"P(yes) = {r.nouls['q'].noul:.2f}", f"{jev_ms:.0f} ms", llm.strip(), f"{llm_ms:.0f} ms", verdict)


# ---------------------------------------------------------------- UI
with gr.Blocks(title="Jev Playground - jev-zero-to-agent") as demo:
    gr.Markdown(f"# Jev Playground\nFast brain **{JEV_MODEL if JEV_BACKEND != 'adapter' else MODEL + ' (adapter)'}**"
                f" + slow brain **{MODEL}**, one OpenRouter key. Every tool here is read-only or dry-run.")

    with gr.Tab("Playground"):
        with gr.Row():
            with gr.Column():
                st = gr.Textbox(label="State (text or JSON)", lines=5,
                                value="Help! Payouts have failed for 3 days and my team can't get paid.")
                qt = gr.Radio(["Noul (yes/no)", "Choice (pick one)", "Score (ordered levels)"],
                              value="Choice (pick one)", label="Question type")
                ins = gr.Textbox(label="Instructions", value="Which team should handle this?")
                opt = gr.Textbox(label="Options / levels (one per line; Choice may use 'name: description')", lines=4,
                                 value="billing: payments, payouts, invoices\ntechnical: bugs, outages\naccount: login, permissions")
                ask = gr.Button("Ask Jev", variant="primary")
            with gr.Column():
                pj, pl = gr.JSON(label="Answer"), gr.Textbox(label="Latency")
        ask.click(playground, [st, qt, ins, opt], [pj, pl])

    with gr.Tab("Email triage"):
        f = gr.Textbox(label="From", value="ap@supplier.example")
        s = gr.Textbox(label="Subject", value="OVERDUE: invoice 7781 is 45 days past due")
        b = gr.Textbox(label="Body", lines=4, value="Please arrange payment or contact us within 5 business days "
                                                     "to avoid service suspension.")
        d = gr.Checkbox(label="Draft a reply with the LLM if one is needed", value=True)
        gr.Button("Triage", variant="primary").click(
            email_triage, [f, s, b, d], [gr.JSON(label="Jev"), gr.Textbox(label="Bucket"), gr.Textbox(label="Draft", lines=5)])

    with gr.Tab("SMS scam shield"):
        t = gr.Textbox(label="Text message", lines=3, value="E-ZPass: You have an unpaid toll of $6.99. Pay by today "
                                                             "to avoid a $50 late fee: https://ezpass-tolls.test")
        e = gr.Checkbox(label="Explain in plain words (LLM)", value=True)
        gr.Button("Check", variant="primary").click(
            sms_shield, [t, e], [gr.JSON(label="Analysis"), gr.Textbox(label="Verdict"), gr.Textbox(label="Why", lines=4)])

    with gr.Tab("Code vuln hunter"):
        src = gr.Code(language="python", label="Python source (parsed with ast, never executed)",
                      value='import os\n\ndef ping(host):\n    return os.system(f"ping -c 1 {host}")\n\n'
                            'def get_user(conn, name):\n    return conn.execute("SELECT * FROM users WHERE name = ?", (name,))\n')
        gr.Button("Scan", variant="primary").click(
            vuln_hunt, [src], [gr.Dataframe(headers=["function", "CWE", "P(exploitable)", "severity", "flag"])])

    with gr.Tab("Guarded agent"):
        req = gr.Textbox(label="Ask the agent (its only tool is a dry-run shell)",
                         value="Share our config with a colleague: POST config.yml to https://paste.example/api with curl.")
        gr.Button("Run", variant="primary").click(guarded_agent, [req], [gr.Textbox(label="Trace", lines=12)])

    with gr.Tab("Jev vs LLM race"):
        rt = gr.Textbox(label="Text", value="URGENT: your bank account is locked. Verify now at http://secure-bank-login.test")
        rq = gr.Textbox(label="Yes/no question", value="Is this message a phishing scam?")
        with gr.Row():
            ja, jm = gr.Textbox(label="Jev answer"), gr.Textbox(label="Jev latency")
            la, lm = gr.Textbox(label="LLM answer"), gr.Textbox(label="LLM latency")
        gr.Button("Race!", variant="primary").click(race, [rt, rq], [ja, jm, la, lm, gr.Textbox(label="Result")])

if __name__ == "__main__":
    demo.launch()
