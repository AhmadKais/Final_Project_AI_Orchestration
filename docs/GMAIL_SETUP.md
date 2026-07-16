# Gmail API / OAuth 2.0 Setup (Appendix A)

> This is a web signup + consent flow through the Google Cloud Console -- it genuinely cannot be done autonomously; there's no CLI or file-download equivalent (unlike Stage 5's tunneling, where the ngrok *binary* could be fetched but the *account* still couldn't). The code side (`infra/email_sender.py`) is already implemented and tested against a mock -- this doc is the five-step checklist for the one part that has to be you.

## The five steps (spec Appendix A Sec. 1), in order

Skipping a step -- especially the consent screen -- makes the failure show up later and more confusingly, not immediately.

### A. Open a project and enable the Gmail API

Go to [Google Cloud Console](https://console.cloud.google.com/), create a new project (or pick an existing one), then in the API Library explicitly enable the **Gmail API**.

### B. Configure the OAuth consent screen

Choose **External** (unless you have a Google Workspace org, then Internal). Add your own email (and your teammate's) to the **Test users** list -- while the app is in Testing mode, only listed users can complete the auth flow.

### C. Restrict the scope to the minimum

Request only:

```
https://www.googleapis.com/auth/gmail.send
```

Never `gmail.modify` or `mail.google.com` -- least privilege means a leaked token can only send, never read or delete. `infra/email_sender.py`'s `SCOPES` constant already matches this exactly; nothing to change in code.

### D. Create credentials

On the Credentials page: **Create Credentials → OAuth Client ID → Application type: Desktop app**. Download the resulting file and save it as `credentials.json` **at the project root** (same directory as `pyproject.toml`) -- that's the default path `infra/email_sender.get_service()` looks for.

**Before anything else, confirm `.gitignore` covers it** (it already does — `credentials.json` and `token.json` are both listed):

```bash
git check-ignore -v credentials.json token.json
```

### E. First run creates `token.json`

The first time `get_service()` runs with no `token.json` present, it opens a browser for you to approve the consent screen, then writes `token.json` next to `credentials.json`. After that, every future run reuses and auto-refreshes it -- no repeated manual login.

```python
from pathlib import Path
from police_thief.infra.email_sender import get_service, send_report

service = get_service()  # first call: opens a browser, writes token.json
send_report(service, "rmisegal+uoh26finalgame@gmail.com", "Test", Path("docs/sample_reports/result_demo-001.json"))
```

## Required files (Table 5)

| File | Source | Sensitivity |
|---|---|---|
| `credentials.json` | Downloaded in Step D | Secret -- gitignored |
| `token.json` | Auto-created in Step E | Secret -- gitignored |

**If either is ever committed, deleting it in a later commit is not enough** -- it's still in the git history. Rotate the credentials in the Cloud Console instead.

## What's already done vs. what needs you

| Already done | Needs you |
|---|---|
| `get_service()`/`send_report()` implemented exactly per Appendix A's reference flow | Steps A-D: create the Cloud project, consent screen, scope, and `credentials.json` (a personal Google account signup + console flow, not something I can do) |
| `send_report()` fully tested against a mocked Gmail service (`tests/test_email_sender.py`) | Step E: the one-time browser consent approval |
| `.gitignore` already excludes both secret files | Nothing -- already correct |
| `Gatekeeper` (quota/rate-limit/DOS protection) wraps every real send | Nothing -- already correct |

## Status

Blocked on user action (Google account + Cloud Console signup). Not marked complete in `docs/TODO.md`.
