---
name: setup
description: "This skill should be used when a Job Office user shares their CV or resume for the first time, says 'update my profile', 'change my job preferences', 'add a job board', 'check my CV', 'review my resume', or when the front desk finds no job-office folder. It builds the candidate profile, records standard application answers, runs a CV health check, checks tools, and creates the office folder."
metadata:
  version: "0.1.0"
---

# Setup Desk

Build everything the other desks rely on: the office folder, the candidate profile, standard form answers, the board list, and a healthy CV. Read `${CLAUDE_PLUGIN_ROOT}/references/office-folder.md` for the folder layout and file formats, and `${CLAUDE_PLUGIN_ROOT}/references/safety-and-consent.md` for what must never be stored.

## Step 1. Create the office

Run:
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py init --office job-office
```
This creates the folders and the three CSV files with headers. Copy the user's CV into `job-office/cv/` as `master.<ext>` without changing it. If they gave a sample cover letter, copy it into `job-office/templates/`.

## Step 2. Read the CV

Read the CV fully (PDF, Word, image, or pasted text). Extract: contact details, every role (title, employer, city, country, dates, duties), education, certificates and licences with expiry dates, languages, skills, links.

Write the draft profile to `job-office/profile.md` using the layout in office-folder.md.

## Step 3. Ask only what cannot be inferred

Ask in small groups (use AskUserQuestion when available, three or four questions at a time). Skip anything the user already said.

Group A, targets:
- Roles they want, and acceptable alternatives
- Countries and cities; remote, hybrid, or onsite
- Contract type (permanent, contract, any) and full or part time

Group B, eligibility (record answers exactly; these go on legal forms):
- For each target country: legally authorized to work there? Will they need sponsorship?
- Driver's licence and access to a vehicle (only if roles may need it)
- Willing to relocate, earliest start date, notice period

Group C, preferences:
- Minimum pay and currency, shifts they can or cannot work
- Phone number to use on applications (international format) and preferred contact method
- How to handle diversity and self identification questions (default: leave blank)

Group D, boards:
- Which job boards to search. If none, suggest four to six from `${CLAUDE_PLUGIN_ROOT}/references/job-boards.md` matched to their field and countries, and let them choose.

Group E, letter style:
- Do they have a cover letter format they like? Spelling (UK or US)? Any words to avoid?

Save every answer to profile.md. Show the "Standard form answers" section back to the user and ask them to confirm it, because these answers will be reused on every application.

## Step 4. CV health check

Review the CV and report in a short list:
- Missing or unclear dates, gaps longer than six months without a note
- Contact details: phone in international format, professional email, city and country
- Achievements versus duties: suggest two or three measurable lines where the user can supply numbers
- Keywords: compare against three typical postings for the target role and list missing core terms the user genuinely has
- Applicant tracking system safety: no tables for core content, no text in images, standard section headings, simple fonts, file under 2 MB
- Length: one to two pages for most roles; academic CVs may be longer

Offer a cleaned master CV in Word (and PDF) built only from the user's facts. Save to `job-office/cv/cv_master_clean.docx`. Never overwrite the original.

## Step 5. Visa and relocation flags

For each target country where the user said they are not authorized to work:
- Note in profile.md that roles stating "must be eligible to work in <country>" or "no sponsorship" should be scored lower and flagged.
- Search the official government immigration site for the main work permit routes relevant to their occupation, and summarise in two or three lines with the link. State that this is general information, not immigration advice.

## Step 6. Tools check

Check what is available and tell the user plainly what each one unlocks:

| Tool | How to check | What it unlocks | If missing |
|---|---|---|---|
| Claude in Chrome | browser tools with `chrome` in their name are present | searching logged in boards, filling and submitting forms | ask the user to install or open the Claude in Chrome extension side panel |
| Email connector | Gmail or Outlook tools present | sending approved emails, scanning for employer replies | office drafts emails for copy and paste; suggest connecting |
| Scheduled tasks | a scheduling tool is present | daily job scan, follow up reminders, weekly report | user asks manually ("any new postings?") |

Record results in the Tools section of profile.md.

## Step 7. Letter template

If the user gave a sample letter, read it and record in profile.md: header layout, font, colour, greeting, paragraph count, sign off, tone. Write `job-office/templates/cover_letter.json` for `scripts/make_letter.js` (see the script header for fields). Otherwise write the default template from `${CLAUDE_PLUGIN_ROOT}/templates/cover_letter.default.json` with the user's name, title, email, and phone filled in. Use US Letter page size (12240 x 15840) for the United States and Canada; switch `page.width` and `page.height` to A4 (11906 x 16838) for everywhere else, based on the countries applied to.

## Step 8. Finish

- Append a log entry.
- Tell the user setup is done in two or three lines, show any CV fixes that need their input, and offer the next step: "Shall I search your boards now?" Then hand off to `job-hunt`.

## Updating later

When the user changes something ("I now have a work permit", "add Seek", "I moved to Toronto"), update profile.md, confirm the changed standard answers, and note the change in the log. Future applications use the new answers; past ones are not changed.
