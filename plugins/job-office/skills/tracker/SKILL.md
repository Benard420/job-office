---
name: tracker
description: "This skill should be used when a Job Office user asks 'where are my applications', 'show my job tracker', 'update my application statuses', 'which applications are waiting', 'did anyone reply', 'show the dashboard', 'weekly report', or 'what deadlines are coming up'. It keeps a live application spreadsheet and a dashboard in sync with the office records, scans email for employer replies, flags deadlines and follow ups, and writes a weekly progress report."
metadata:
  version: "0.1.0"
---

# Tracker Desk

The office records (`jobs.csv`, `applications.csv`, `outreach.csv`) are the source of truth. The tracker turns them into two views the user can open anytime: a live spreadsheet and a dashboard. Status definitions are in `${CLAUDE_PLUGIN_ROOT}/references/office-folder.md`.

## Sync (run after every desk action and at the end of every session)

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py sync --office job-office
```
This applies automatic rules (Applied over 7 days becomes Waiting feedback; Found or Shortlisted past closing date becomes Missed), then writes:
- `job-office/tracker.xlsx`: the spreadsheet (Applications sheet with filters and status colours, plus Outreach and Summary sheets)
- `job-office/dashboard.html`: a self contained dashboard (status counts, applications per week, response rate, upcoming deadlines and interviews, follow ups due)
- `job-office/tracker_rows.json`: the same rows as JSON for artifact types

## The two views

**Spreadsheet (source of truth for the user)**
- If the Artifact tool lists a Sheets type, create the tracker from it on first run (title "Job Tracker") and fill it from `tracker_rows.json`, following that type's own instructions. On later syncs update the same artifact by its URL. Record the URL in profile.md under Tools.
- Otherwise send `tracker.xlsx` to the user.
- If the user edits the sheet (for example marks an interview), read it back before the next sync and apply their changes to the CSVs first.

**Dashboard**
- If the Artifact tool lists a Dashboard type, create it from that type (title "Job Office Dashboard") using `tracker_rows.json`.
- Otherwise publish `dashboard.html` as an artifact (or send the file if artifacts are unavailable). Record the URL in profile.md.
- Republish to the same URL on each sync so the user's link never changes.

## Status updates

Statuses change from three sources:
1. The office's own actions (search, submit, outreach) through tracker.py commands.
2. The user telling the office ("I got an interview for 413385"): run `tracker.py status --office job-office --job <id> --status "Interview requested" --note "<detail>"`.
3. Email replies, when Gmail or Outlook is connected: search the inbox for messages from employer domains, portal notification addresses, and outreach contacts since the last scan. Summarise each in one line with the proposed status. Apply only after the user confirms. Never open unrelated personal mail.

For portals with a "My Applications" page, offer to read it through Claude in Chrome and compare statuses (for example "Under review", "Not selected", "Position closed").

## Alerts to surface (in the return greeting and on request)

- Shortlisted jobs closing in the next 3 days
- Follow ups due today
- Interviews in the next 7 days, with preparation status
- Applications waiting more than 21 days with no reply (suggest a follow up or letting go)

## Weekly progress report

Once a week (or on request) write `job-office/notes/weekly_<date>.md` and send a short version to the user:
- Applications sent this week and total; responses; interviews; offers
- Response rate by board and by job type, so the user sees what is working
- Closing dates and interviews coming up
- Two or three focused recommendations for next week (for example "home care roles respond faster; prioritise them", "add 2 measurable achievements to the CV")

When a scheduling tool is present, offer a scheduled task for the report each week at a time the user chooses. It reads and reports only.
