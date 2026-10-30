# The Office Folder

Every desk reads and writes the same folder so work survives between sessions. Create it during setup inside the user's working directory (or their connected project folder when one exists). Name: `job-office/`.

```
job-office/
  profile.md            candidate profile and standard form answers
  cv/
    master.<ext>        the CV the user gave (never edited in place)
    cv_<variant>.docx   tailored CV versions
  templates/
    cover_letter.json   letter layout settings (font, colours, header, sign off)
    sample_letter.*     the user's own letter, if they gave one
  letters/              <req>_<Employer>_<Role>_Cover_Letter.pdf and .docx
  jobs.csv              every job seen
  applications.csv      every submission and the exact answers given
  outreach.csv          every message drafted or sent
  notes/                interview prep, offer notes, 30/60/90 plans, weekly reports
  log.md                short dated log of each session: what was done, what is next
```

## profile.md layout

```
# Candidate Profile
Updated: <date>

## Contact
Name, preferred name, email, phone (with country code), city and country now, mailing address (only if the user wants it on forms), LinkedIn, portfolio.

## Targets
Roles (with synonyms), seniority, countries and cities, remote or onsite, contract type, full or part time, minimum pay and currency, shifts, start date, notice period, willingness to relocate.

## Standard form answers  (reuse exactly; change only when the user says so)
- Legally authorized to work in <country>: <answer>
- Requires sponsorship: <answer>
- Driver's licence and vehicle: <answer>
- How did you hear about this job: default to the board name
- Diversity and self identification: leave blank unless the user chose answers
- Previously employed by <employer>: <answer>
- Relevant certificates held: <list>

## Experience summary
One line per job: title, employer, city, start to end, three strongest duties.

## Education and certificates

## Strengths to lead with
Short list of themes that every letter can draw on.

## Boards
Board name, URL, needs login (yes/no), automation allowed (yes/no), notes.

## Tools
Claude in Chrome: on/off. Email connector: Gmail/Outlook/none. Scheduled tasks: available/not.

## Letter preferences
Format source, tone, sign off, words to avoid, spelling (UK/US).
```

## CSV columns

jobs.csv
`job_id,board,req,title,employer,site,unit,city,country,contract,fte_or_hours,shifts,salary,posted,closes,url,fit_score,fit_notes,scam_flag,status,first_seen,last_checked`

applications.csv
`date,job_id,req,title,employer,letter_file,cv_file,answers,confirmation,submitted_by,notes`

outreach.csv
`date,job_id,contact_name,contact_role,channel,address,subject,status,follow_up_due,reply`

Use `scripts/tracker.py` to create these with headers, add rows, and rebuild the dashboard. Never hand edit a CSV by retyping it; append or update rows with the script or a short read-modify-write.

## Status values (jobs.csv `status`)

| Status | Meaning |
|---|---|
| Found | Seen in a search, not yet reviewed |
| Shortlisted | User wants to apply |
| Skipped | User chose not to apply, or requirements not met |
| Applied | Submitted, confirmation seen |
| Waiting feedback | Applied more than 7 days ago with no reply |
| Interview requested | Employer asked for an interview or test |
| Interview done | Interview completed, awaiting outcome |
| Offer | Offer received |
| Hired | Offer accepted |
| Rejected | Employer declined |
| Closed | Posting removed or closed before the user applied, or the employer closed it |
| Missed | Closing date passed while the job was Found or Shortlisted |
| Withdrawn | User withdrew |

Move to Waiting feedback automatically after 7 days in Applied. Move to Missed automatically when the closing date has passed and the status is Found or Shortlisted.

## log.md

Append one short entry per session:
```
## 2026-10-29
Did: searched 3 boards, 40 new matches; applied to 4 (413385, 413443, 413381, 413383).
Next: user to choose which of the 40 to apply for.
```
Read the last entry at the start of every return visit.
