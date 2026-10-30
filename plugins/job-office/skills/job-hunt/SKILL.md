---
name: job-hunt
description: "This skill should be used when a Job Office user asks to 'find jobs', 'search for jobs', 'any new postings?', 'check a job board for jobs', 'look for roles', 'set up a daily job scan', or 'what jobs match me'. It searches the user's chosen boards, scores each job against the candidate profile, removes duplicates, runs a scam check, and presents a shortlist for approval."
metadata:
  version: "0.1.0"
---

# Job Hunt Desk

Find jobs that genuinely fit, never show the same job twice, and let the user choose what to apply for.

Inputs: `job-office/profile.md` (targets, boards, eligibility) and `job-office/jobs.csv` (everything seen before). If profile.md is missing, run the `setup` desk first.

## Step 1. Plan the search

From profile.md list: boards, role names plus synonyms, locations, contract type, date window (default: since `last_checked` for that board, or the last 14 days on a first run).

Tell the user in one line which boards and terms will be searched.

## Step 2. Search each board

- **Boards needing login, or employer portals**: use Claude in Chrome. Follow `${CLAUDE_PLUGIN_ROOT}/references/browser-playbook.md` (reading listings section). Ask the user to sign in if needed.
- **Public boards**: use the browser if available, otherwise web search and web fetch.
- **LinkedIn, Indeed, Glassdoor and similar**: read at a human pace, a page or two at a time. Do not scrape at scale.
- Sort by newest. Stop when results fall outside the date window.
- For every candidate posting open the detail page and capture: requisition or job number, title, employer, site, unit or team, city, country, contract type, hours or FTE, shifts, salary, posted date, closing date, requirements, apply URL.

## Step 3. Remove duplicates

Run:
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py known --office job-office
```
It prints every known job_id and req. Drop any posting already known. Mark reposts (same employer, title, and unit with a new number) as reposts and note the old status.

## Step 4. Score fit (0 to 100)

| Factor | Points |
|---|---|
| Role title matches a target role or synonym | 25 |
| Must have requirements met (certificate, licence, degree, years) | 25 (0 if a hard requirement is missing) |
| Location matches targets or user will relocate there | 15 |
| Contract type matches (for example permanent) | 10 |
| Hours, FTE, and shifts suit preferences | 10 |
| Salary at or above the minimum (or not stated) | 5 |
| Work authorization: no barrier stated, or sponsorship offered | 10 (0 if posting says no sponsorship and the user needs it) |

Rules:
- A missing hard requirement caps the score at 40 and is listed in `fit_notes`.
- If the user set a hard filter (for example "permanent only"), drop non matching jobs entirely and say how many were dropped.

## Step 5. Scam check

Apply `${CLAUDE_PLUGIN_ROOT}/references/scam-signs.md`. Set `scam_flag`. Never shortlist a `high` flag job; mention it to the user in one line.

## Step 6. Record

Add every new job with status `Found`:
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py add-jobs --office job-office --file <new_jobs.json>
```
The JSON is a list of objects using the jobs.csv column names. Update `last_checked` per board.

## Step 7. Present the shortlist

Show a compact table sorted by fit score, grouped sensibly (for example by employer or region). Columns: req, site, unit, hours or FTE, shifts, closes, fit score. Then a short "Left out" list with reasons (temporary, missing requirement, scam risk).

Ask which to apply for, offering simple choices:
1. All shortlisted
2. A filter (for example "fit 70 and above", "full time only", "only <city>")
3. A pick list

Set chosen jobs to `Shortlisted` and others to `Skipped` only when the user says so. Then hand off to `application-pack`.

## Daily job scan

When the user wants automatic checks and a scheduling tool is present:
- Create a scheduled task (call it a "scheduled task" with the user) that runs each morning in the user's time zone with a standalone prompt: open the job office in this project, run the job-hunt desk for new postings since last check, add them to the tracker, and send the user a short list of new matches with fit 60 and above. It must not apply or send anything.
- Tell the user the time it will run and how to stop it.
If no scheduling tool exists, say so and suggest asking "any new postings?" each day.

## Missed and closed jobs

On each run, also re-check `Shortlisted` jobs: if the posting is gone set `Closed`; if the closing date passed set `Missed`. Report both in one line so the user learns which deadlines slipped.
