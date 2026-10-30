---
name: interview-coach
description: "This skill should be used when a Job Office user says 'I got an interview', 'prepare me for my interview', 'mock interview', 'what questions will they ask', 'help me answer interview questions', 'I have an assessment', or 'write a thank you note after my interview'. It researches the employer, predicts likely questions, builds answers from the user's real experience, runs a mock interview, prepares logistics, and drafts the follow up thank you note."
metadata:
  version: "0.1.0"
---

# Interview Coach Desk

Get the user ready to walk in confident and specific. Use only their real experience.

## Step 1. Gather the details

From the invite (email or what the user pastes) and jobs.csv: employer, role, unit, date and time with time zone, format (phone, video platform, in person, panel, assessment, skills test), interviewer names if given, anything to bring or prepare. Set the job status to `Interview requested` and add the date to the tracker.

If the time zone differs from the user's, convert it and state both times clearly.

## Step 2. Research

From public sources: the employer's mission and values, recent news, the unit or team, patient or customer group, services, size, the job posting's top requirements, and any published interview format (many public employers use behavioural or values based interviews). Save to `job-office/notes/interview_<req>.md`.

## Step 3. Likely questions

Write 12 to 18 questions in four groups:
- Opening ("Tell us about yourself", "Why this role and this organisation?")
- Role specific and technical (for example safe transfers, infection control, documentation, a coding problem, a design critique, depending on field)
- Behavioural ("Tell us about a time when...") tied to the posting's requirements and the employer's values
- Situational ("What would you do if...")

Include two or three questions about any visible gaps (relocation, authorization, career change, employment gap), with honest, positive framing.

## Step 4. Build answers from real stories

Work with the user to pick five to seven stories from their experience. Structure each as Situation, Task, Action, Result, and keep each spoken answer to about 90 seconds. Ask the user for details only they know (numbers, outcomes). Write the answer outlines in the notes file, not full scripts, so the user sounds natural.

Prepare three or four thoughtful questions for the user to ask the panel.

## Step 5. Mock interview

Offer a mock interview in chat:
- Ask one question at a time and wait for the user's answer (typed or dictated).
- After each answer give short feedback: what worked, one improvement, and a tighter version if helpful.
- Finish with an overall note and the two things to practise most.

## Step 6. Logistics checklist

- Time and time zone confirmed; calendar entry (offer to create it if a calendar connector exists)
- Platform test (camera, microphone, link, quiet space, stable internet, backup phone number)
- Documents (ID as requested by the employer, certificates, references list, portfolio)
- What to wear and when to arrive or log in
- For overseas candidates: a one line, confident explanation of relocation timeline and work authorization status, consistent with profile.md

## Step 7. After the interview

- Ask how it went and note any commitments made.
- Draft a thank you email within 24 hours (style in `${CLAUDE_PLUGIN_ROOT}/references/writing-style.md`); send through the email connector only with approval.
- Set status to `Interview done` and plan a follow up if there is no word by the date the panel mentioned (or 7 to 10 days).
- If an offer comes, hand off to `new-role-guide`. If a rejection comes, record it kindly, ask if the user wants to request feedback, and note any lessons for the next interview.
