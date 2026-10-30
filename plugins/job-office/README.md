# Job Office

A personal job search office inside Claude, for anyone, in any country and any field.

Say **"set up my job office"** in a new project and Claude welcomes you, explains what the office can and cannot do, and asks for your CV. From there it:

- checks and cleans up your CV
- searches the job boards you choose and scores each role against your profile
- warns you about listings that look like scams
- writes a tailored, one page cover letter for every job (PDF and Word)
- fills in and submits application forms in your own Chrome browser
- drafts cold emails, texts and LinkedIn notes, and sends emails you approve
- tracks every application in a live spreadsheet and a dashboard
- prepares you for interviews with research, likely questions and a mock interview
- helps you weigh an offer, plan your first 90 days, and build the skills to grow

## The desks

| Skill | Use it for |
|---|---|
| front-desk | Welcome, status on return, and routing everything else |
| setup | CV intake, profile, standard form answers, boards, tools, CV health check |
| job-hunt | Searching boards, fit scoring, duplicates, scam check, daily scan |
| application-pack | Cover letters, CV variants, screening answers, extras |
| apply-desk | Filling and submitting forms in Chrome |
| outreach | Cold emails, texts, LinkedIn notes, follow ups |
| tracker | Spreadsheet, dashboard, inbox status updates, weekly report |
| interview-coach | Research, likely questions, answers, mock interview, thank you note |
| new-role-guide | Offer review, negotiation, onboarding, 30/60/90 plan, skills roadmap |

## What you need

- **Claude in Chrome** (the browser extension) for searching sites you are signed in to and for submitting applications. You sign in to each job site yourself.
- **Gmail or Outlook connected** (optional) to send approved emails and spot replies from employers.
- **Scheduled tasks** (optional) for the daily job scan, follow up reminders and the weekly report.

## How file uploads work

Claude cannot pick files from your computer. When a form needs a file, Claude sends a line like **Ready: 413385_Employer_Cover_Letter.pdf**. You click Browse on the form and choose that file; Claude checks it and continues. Every file name starts with the job number so it is easy to find.

## Your records

Everything lives in a `job-office/` folder in your project: your profile, CVs, letters, the job list, every application with the exact answers given, outreach, notes, and a session log. Nothing sensitive (passwords, ID numbers, bank details) is ever stored.

## Ground rules

- Claude never types your passwords, creates accounts, or solves "I'm not a robot" checks.
- Nothing is sent or submitted in your name without your approval.
- Claude never invents experience, qualifications or references.
- On sites that do not allow automated applying (such as LinkedIn and Indeed), Claude prepares everything and you click submit.
- Salary, contract and immigration notes are general information, not legal or financial advice.

## Scripts

- `scripts/tracker.py`: records, status rules, spreadsheet and dashboard
- `scripts/make_letter.js`: builds letters from a template (needs the `docx` npm package; LibreOffice for PDF)
- `scripts/check_letters.py`: checks letters for page count, dashes, cliches and job numbers
- `scripts/portal_helpers.js`: browser helpers for multi step portals

Built by Sandra Benard (Ice) from a real application campaign.
