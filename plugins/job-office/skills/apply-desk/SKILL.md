---
name: apply-desk
description: "This skill should be used when a Job Office user says 'apply', 'submit the applications', 'apply to all of them', 'fill in the application form', 'continue applying', or after the application pack is ready. It fills and submits online application forms in the user's own Chrome browser through Claude in Chrome, using the Ready handoff for file uploads and a review check before every submission, then logs each application."
metadata:
  version: "0.1.0"
---

# Apply Desk

Submit approved applications accurately, one at a time, in the user's own browser. Read `${CLAUDE_PLUGIN_ROOT}/references/browser-playbook.md` and `${CLAUDE_PLUGIN_ROOT}/references/safety-and-consent.md` before starting.

## Preconditions

- The user approved the list of jobs to apply for (by name, number, or a clear filter). Approval covers only those jobs.
- Each job has its letter (and CV variant if any) in `job-office/letters/` and the user has saved the files locally.
- Claude in Chrome tools are present. If not, explain how to turn on the extension and stop.
- profile.md has confirmed standard form answers.

## Start of run

1. Tell the user how many applications are in this run and how the handoff works:
   "I will fill each form. When a file is needed I will send **Ready: <filename>**. Click Browse on the form and pick that file. I will check everything and submit."
2. Ask the user to sign in to the portal in the tab with the side panel, if not already signed in.
3. Create a task list with one item per job so progress is visible.

## Per job loop

Follow the application loop in browser-playbook.md:

1. Open the posting. Confirm number, title, employment type, and that it is still open. If closed or removed, set status `Closed`, tell the user in one line, move on.
2. Start the application. Inject `${CLAUDE_PLUGIN_ROOT}/scripts/portal_helpers.js` with the JavaScript tool after each page load (read the file and pass its contents).
3. Fill each step from profile.md. Re-read values; fix empties.
4. New question not covered by profile.md:
   - Factual and harmless (for example "How did you hear about us?"): answer sensibly and record the answer.
   - Eligibility, legal, or declaration: pause and ask the user. Save the answer to profile.md for reuse.
5. Remove any leftover attachment from a previous application.
6. Send **Ready: <filename>** (starts with **<req>**) using the message tool so the user sees it immediately. Poll for the upload to finish and save. If nothing arrives after about 90 seconds, send one gentle reminder and keep waiting; never skip ahead.
7. Review step check (all must pass): requisition number, correct file name, phone, email, authorization answer, certificate answer, work history count, no blank required fields, no duplicate attachments.
8. Submit. On sites that forbid automation, ask the user to click Submit and confirm.
9. Confirm success (dialog or "My Applications"). Then log:
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tracker.py applied --office job-office --job <job_id> --letter <file> --answers "<key answers>" --confirmation "<text seen>"
```
10. Send a one line progress note every job or two ("413385 submitted, 3 to go"), not a paragraph.

If the user picks a file before the Ready message (they sometimes run ahead), verify the file name matches the job and continue. If it does not match, remove it and send the Ready line again.

## Errors

- Session expired: stop, ask the user to sign in again, resume the same job.
- Field will not accept a value after two attempts: screenshot, explain briefly, skip to the next job, and list it at the end.
- Unsure whether a submit went through: check "My Applications" before trying again. Never double submit.

## End of run

- Run `tracker.py sync` to refresh the sheet and dashboard.
- Append a log entry with the numbers submitted and anything skipped with reasons.
- Close with one short summary: how many submitted, which were skipped and why, closest closing dates still ahead, and the offer to draft outreach for the top matches.
