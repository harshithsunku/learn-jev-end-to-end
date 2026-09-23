# Run the email job

`jobs/email_triage.py` is [notebook 04](../course/04_email_triage_job.ipynb) packaged as a script you can
schedule. Jev decides every email, and the LLM drafts replies only for the emails that need one.

## Try it on the sample inbox

```bash
uv run python jobs/email_triage.py --draft-replies
```

```text
triaged 40 emails in 2.8 s -> {'reply': 11, 'quarantine': 5, 'review': 1, 'file:notification': 7,
                                'file:newsletter': 5, 'file:billing': 4, 'file:security_alert': 4, ...}
report: reports/triage-2026-09-23-0343.md
```

The report groups emails into **quarantine** (phishing), **review** (Jev wasn't sure), **reply** (with a
draft for each) and **filed**. A JSON copy sits next to it for other tools and agents to use.

## Run it on your real mailbox

Add these to `.env`. Use an **app password**, never your main password.
For Gmail: *Google Account → Security → 2-Step Verification → App passwords*.

```bash title=".env"
IMAP_HOST=imap.gmail.com
IMAP_USER=you@gmail.com
IMAP_PASSWORD=your-app-password
```

```bash
uv run python jobs/email_triage.py --source imap --limit 50 --draft-replies
```

!!! success "Read-only by design"
    The mailbox is opened with `readonly=True` and messages are fetched with `BODY.PEEK[]`, so nothing is
    marked as read, moved or deleted. The job **never sends email**. Drafts go into the report for you to
    use or ignore.

## Schedule it

=== "cron (Linux / macOS)"

    ```bash
    # every 30 minutes, 8:00-18:00, Monday to Friday
    */30 8-18 * * 1-5  cd /path/to/learn-jev-end-to-end && uv run python jobs/email_triage.py --source imap --draft-replies
    ```

=== "Task Scheduler (Windows)"

    Create a task that runs `uv` with the arguments
    `run python jobs/email_triage.py --source imap --draft-replies`, and set *Start in* to the repository folder.

## Options

| Flag | Default | What it does |
|---|---|---|
| `--source` | `sample` | `sample` (data/inbox.jsonl) or `imap` |
| `--limit` | `100` | how many of the newest emails to triage |
| `--draft-replies` | off | LLM drafts for the "reply" bucket |
| `--out` | `reports` | where the Markdown and JSON reports go |
| `--workers` | `8` | parallel Jev calls (Jev allows 1,200 requests per minute) |

## Make it yours

Edit `CATEGORIES` and `QUESTIONS` at the top of the script. Add a category for your newsletters, a
`Noul` for "is this from a customer?", or a `Score` for "how angry is the sender?". See
[Use your own data](your-own-data.md).
