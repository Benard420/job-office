---
name: outreach
description: "This skill should be used when a Job Office user asks to 'email the recruiter', 'send a cold email', 'message the hiring manager', 'write a LinkedIn note', 'draft a WhatsApp or text to the recruiter', 'follow up on my application', or 'who should I contact about this job'. It finds public hiring contacts, drafts tailored cold emails, texts and notes, sends emails only through a connected Gmail or Outlook after explicit approval, and schedules follow ups."
metadata:
  version: "0.1.0"
---

# Outreach Desk

Reach a real person about a real application, politely and sparingly. Read `${CLAUDE_PLUGIN_ROOT}/references/writing-style.md` (cold email, text, follow up sections) and `${CLAUDE_PLUGIN_ROOT}/references/safety-and-consent.md`.

## When outreach helps

Offer outreach for the top fit jobs, roles at smaller employers, roles where the posting names a contact, and roles where the user has a genuine connection. Large public employers with central HR portals often do not respond to cold emails; say so and suggest focusing on the application itself there.

## Step 1. Find the contact

Use only public business sources:
- The posting itself (named recruiter, HR email)
- The employer's careers page, team page, or contact page
- Public LinkedIn profiles (read only; do not scrape)
- Professional directories the employer publishes

Record the contact in outreach.csv with the source. If no contact is found, draft to the general HR or careers address, or skip and tell the user. Never guess personal email addresses.

## Step 2. Draft

For each contact draft up to three versions, as the user prefers:
- **Cold email**: subject plus 90 to 140 words.
- **Text or WhatsApp**: under 450 characters, only if the contact published that number for recruitment.
- **LinkedIn note**: under 300 characters.

Show drafts to the user for approval. Use the message composer widget when available so the user can copy or open in their mail app.

## Step 3. Send (email only, with approval)

- If Gmail or Outlook tools are connected and the user approved this exact message, send it from their account. Report "Sent to <name> at <address>" afterwards.
- If not connected, give the draft ready to copy and offer to connect their email.
- Texts and LinkedIn notes are always for the user to send.
- Log every message: `tracker.py outreach --office job-office --job <id> --contact "<name>" --channel email --status sent --follow-up <date>`.

## Step 4. Follow ups

- Plan follow ups at about day 6 and day 13 after applying or first contact, and record `follow_up_due`.
- When a scheduling tool is present, offer one scheduled task that checks due follow ups each weekday morning and drafts them for approval (it must not send on its own).
- Stop after two follow ups without a reply.

## Step 5. Replies

If the email connector is available, search for replies from the contact's address or the employer's domain. Summarise each reply in one line and propose the tracker status change (for example Interview requested). Change it only after the user confirms. Hand off to `interview-coach` when an interview is requested.
