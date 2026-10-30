---
name: application-pack
description: "This skill should be used when a Job Office user asks to 'write the cover letters', 'draft a cover letter for this job', 'tailor my CV', 'answer the screening questions', 'prepare my application', or after jobs are shortlisted. It produces a tailored one page cover letter per job (PDF and Word), CV variants tuned to the posting, answers to screening questions, and extras that strengthen the application, using only facts from the user's CV."
metadata:
  version: "0.1.0"
---

# Application Pack Desk

Produce everything a shortlisted job needs before applying. Read `${CLAUDE_PLUGIN_ROOT}/references/writing-style.md` before writing anything.

Inputs: `job-office/profile.md`, the master CV, `job-office/templates/cover_letter.json`, and the shortlisted rows in `job-office/jobs.csv`.

## Step 1. Group the jobs

Group shortlisted jobs by kind (for example hospital, long term care, home care, rural centre; or for tech: product company, agency, startup). Each group gets a tailored base story; each job then gets its own specifics (employer, unit, hours, shifts, requisition, local link). This keeps quality high when there are dozens of jobs.

Read each posting's requirements again (from the saved URL) before writing its letter.

## Step 2. Write the letters

For each job, write the letter body following the shape in writing-style.md. Use only facts from profile.md and the CV. Tie the opening to something real between the user and this employer, unit, or community.

Then build files with the letter script:
```
node ${CLAUDE_PLUGIN_ROOT}/scripts/make_letter.js --template job-office/templates/cover_letter.json --letters <letters.json> --out job-office/letters
```
`letters.json` is a list of objects: `req`, `file_stem` (for example `413385_St_Boniface_Hospital_Psychiatry`), `recipient` (list of lines), `subject`, `paragraphs` (list of strings), `date`. The script writes `<file_stem>_Cover_Letter.docx` and, when LibreOffice is available, the PDF. It also checks for dashes and banned phrases and prints warnings.

If the `docx` package is missing, install it (`npm install -g docx`) before running.

## Step 3. Check every letter

Run the tailoring checklist in writing-style.md for each file. Confirm each PDF is one page:
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_letters.py job-office/letters
```
Fix anything flagged and rebuild.

Read at least the first letter of each group in full, as rendered text, before sending files to the user.

## Step 4. CV variants (when useful)

If a posting's core keywords differ strongly from the master CV, build a tailored variant: reorder bullets, mirror honest terminology, surface relevant certificates. Never add experience. Save as `job-office/cv/cv_<req>.docx` and PDF. Most jobs in the same field can share one or two variants; avoid making a CV per job without reason.

## Step 5. Screening answers and extras

- Draft answers to posted screening questions or short essays, each traceable to the CV.
- Extras when they help: portfolio or work sample links, a references list (only with the user's permission and their referees' consent), a certificate checklist with expiry dates, a short LinkedIn headline or summary refresh.

## Step 6. Hand the files to the user

The user must have the files on their own computer to pick them with Browse.
- Send all letters (PDFs) to the user in one batch with a one line caption asking them to save them to an easy folder (for example Downloads).
- For large batches, also offer a single zip.
- Mention the naming rule once: every file starts with the job's requisition number.

Record the letter file name for each job in jobs.csv notes or applications.csv when it is submitted. Then hand off to `apply-desk`.

## Regenerating

If the user edits a letter, keep their version and do not overwrite it. If they change style preferences, update the template and rebuild only letters not yet submitted.
