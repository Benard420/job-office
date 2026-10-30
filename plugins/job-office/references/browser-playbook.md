# Browser Playbook (Claude in Chrome)

How to work inside the user's own browser on job portals. Learned from real applications on SAP SuccessFactors, applies to most portals.

## Before starting

1. Confirm Claude in Chrome tools are available (tools with `chrome` in the name). If not, ask the user to install or open the Claude in Chrome extension and open its side panel, then try again.
2. Work in the tab the user has open with the panel. Open new tabs only when needed and say so.
3. Ask the user to sign in to the portal. Never type their password. Wait for "signed in". If a session expires mid run (a sign in page appears), stop and ask again.

## Reading listings

- Prefer reading the site's own search results with JavaScript `fetch` of the search page plus DOMParser when the site allows it. It is faster than clicking and keeps the user's tab stable.
- Sort by newest. Stop scanning when results pass the date window.
- Read the table columns (facility, employment type, posted date) instead of guessing from page text.
- Build a stable job_id from the site's numeric id in the URL, plus the requisition number shown on the posting.

## The application loop

Run one job at a time.

1. Open the posting, confirm requisition number, title, employment type, and closing date match jobs.csv.
2. Click "Apply" with a real mouse click (scroll the button into view, read its position, click it). Script clicks and direct navigation to the apply URL sometimes bounce back to the careers home page. Wait for the form to load fully before running scripts; portals often pass through a blank redirect page for several seconds. Poll for the step header rather than sleeping blindly.
3. Fill each step from profile.md and the standard answers. After filling, read back the values and confirm none of the required fields are empty.
4. Dropdowns built from web components often ignore scripted values. Use real clicks: scroll the field to the centre of the screen, click it, wait one second, type enough of the option to leave a single match, wait two or three seconds for the suggestion list, take a small screenshot, then **click the suggestion itself** (usually about 30 pixels below the field). Pressing Enter often leaves the text in the box without really selecting it, which looks filled but blocks the Next button.
   After filling a step, check that Next is enabled (`window._blocked()` returns false). If it is still blocked, find the field that shows text but is not committed and reselect it by clicking the suggestion.
5. New questions appear per employer (for example "Are you currently employed at <site>?", "Employee ID if you work for <region>"). Answer from profile.md; if it is a new eligibility question, ask the user.
6. Attachments: remove any file left from a previous application (portals often prefill the last cover letter). Confirm the dialog. Then send the user exactly one line:
   **Ready: <filename>** (starts with **<req>**)
   Users often run ahead and pick the file before the Ready line, sometimes even before you remove the old one. Always read the current file name before clicking delete, and never delete a file that already matches the current job number.
   Poll until the new file name appears and the portal shows it as saved (for example "Uploaded On"). Never move to the next step while an upload is still in progress, or it is lost.
7. Go to the Review step. Check: requisition number, file name matches the req, phone, email, work authorization answer, certificate answer, number of employers listed, no duplicate letters.
8. Submit only if every check passes and the user approved this job. Confirm the success message or the redirect to "My Applications". Then log it.
9. If the site forbids automated submission, stop at Review and ask the user to click Submit, then confirm.

## Helper script pattern

Shadow DOM portals need a walker. Re-define helpers after every page load (they are lost on navigation):

```js
window._wait = ms => new Promise(r => setTimeout(r, ms));
window._walk = (root, f, o = []) => { root.querySelectorAll('*').forEach(el => { if (f(el)) o.push(el); if (el.shadowRoot) window._walk(el.shadowRoot, f, o); }); return o; };
window._inputs = () => window._walk(document, el => el.tagName === 'INPUT' && el.getAttribute('aria-label'));
window._center = async re => { const r = new RegExp(re, 'i'); const e = window._inputs().find(x => r.test(x.getAttribute('aria-label'))); if (!e) return 'not found'; e.scrollIntoView({ block: 'center' }); await window._wait(700); const b = e.getBoundingClientRect(); return Math.round(b.x + b.width / 2) + ',' + Math.round(b.y + b.height / 2); };
window._req = () => window._inputs().filter(x => x.offsetParent !== null && x.type !== 'radio' && x.type !== 'file').map(x => x.getAttribute('aria-label').slice(0, 20) + '=' + (x.value || '')).join(' | ');
```

The full helper set, including step navigation and the review check, is in `scripts/portal_helpers.js`. Paste its contents into the page with the JavaScript tool after each load.

## Platform notes

| Platform | Notes |
|---|---|
| SAP SuccessFactors (career*.sapsf.com) | 7 steps. Sessions expire after a few hours; after signing in, the site may land on My Applications instead of the job, so reopen the posting. Step 2 heading is "Profile Information". UI5 web components in shadow DOM. Dropdowns need click, type, Enter. Last cover letter is prefilled; delete it first. Upload must show "Uploaded On" before Next. Region specific questions appear in step 5 and 6. Success shows a dialog or redirects to My Applications. |
| Workday (myworkdayjobs.com) | Account per employer. "Autofill with resume" parses the CV; always re-check dates and titles after. Multi page; "Save and Continue" per page. Voluntary disclosures page: leave blank unless the user chose answers. |
| Taleo (taleo.net) | Older forms, frequent session timeouts. Save often. Some fields reject special characters in addresses. |
| Greenhouse (boards.greenhouse.io) | Single page, no account. File inputs are standard; still ask the user to click Browse. Custom questions at the bottom. |
| Lever (jobs.lever.co) | Single page. "Additional information" box is a good place for a short tailored note. |
| iCIMS | Multi step with account. Watch for a separate "Submit" after the review page. |
| LinkedIn Easy Apply, Indeed Apply | Automation not allowed. Prepare answers and the letter, user submits. |

Add a line here whenever a new platform quirk is learned during use.

## When things go wrong

- A tool call fails right after navigation: the page is still loading. Wait and retry once.
- The page is blank for more than 20 seconds: navigate to the posting again and click Apply again.
- A value will not stick after two tries: take a screenshot, describe the problem to the user, and continue with the next job.
- Never retry a submit if it is unclear whether the first one went through. Check "My Applications" first.
