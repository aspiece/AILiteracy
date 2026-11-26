# Student experience validation — November 2026 pilot release

## Purpose and boundaries

Validate the published website on a school-managed student Chromebook before labeling the revised activities student-validated. This checklist is a proposed test protocol, not a record of completed student testing. Use fictional practice records and a test LMS course; do not change a real grade or collect names, screenshots of private records, student work or student IDs in the test log.

Release entry points:
- Course: https://ai.geneseelearninglab.com/
- Simulation: https://geneseelearninglab.com/Model_Rescue_Simulation.html
- Source release: https://github.com/aspiece/AILiteracy/pull/11
- Model Rescue source: https://github.com/aspiece/GCI/pull/64

## A. First-pass release checks (teacher/test account)

| ID | Test | Acceptance evidence |
|---|---|---|
| A1 | Open course in the normal school browser, then a fresh profile if allowed. Open all eight lessons. | Each lesson loads, six steps are present, next/previous work, new practice resume panel appears. |
| A2 | Check worksheet links in 2.5, 5.5, 6.5, 7.5 and 8.5 using an authorized student account. | Google copy works, or text fallback opens and can be used in a school-managed document. No request-access dead end. |
| A3 | Open 8.5 and its simulation; choose HVAC. | HVAC Equipment Review Model is available. Revised records and validation-versus-independent-test explanation appear. |
| A4 | Change a practice selection after checking, then return/reload. | Feedback does not show stale completion. The choice returns and can be checked again. |
| A5 | Open a direct step link from the LMS after saving a different step. | Requested step opens, and the resume option offers the previously saved step. |
| A6 | Save selections in lesson 1 or 3, download resume file, load in the same lesson on another authorized device/profile. Try a wrong-lesson file. | Correct choices and step restore; wrong file is rejected; no written responses, names, grades or LMS records are in the file. |
| A7 | After saving required work outside the site, clear local practice in a test browser. | Only that lesson's local state clears. Other lessons and submitted work remain unchanged. |
| A8 | Open the simulator with a test profile containing an earlier saved comparison if available. | Old rescue results are invalidated; earlier practice and written notes remain. A notice explains why retesting is required. |
| A9 | Run the simulation with a targeted rescue and with a weaker rescue. Copy report or use manual fallback. | Actual scores and three record IDs match the display; no improvement is acceptable when explained; fresh independent testing and human review are required. |
| A10 | Test on a narrow screen, 200% browser zoom, keyboard only and a supported screen reader. | Visible focus, usable choices/tables, readable text, image descriptions, feedback and dialogs. No essential content unreachable. |

## B. Lesson-by-lesson instructional checks

| Lesson | Task | Evidence of understanding |
|---|---|---|
| 1 | Complete one Human Decisions Map, including HVAC or another pathway. | Identifies risk, private details, qualified reviewer and a reasoned human decision. Try an empty reflection followed by a valid one; exemplar still appears. |
| 2 | Complete one AI Editor Challenge using the fictional draft. | Original prompt, evidence-based audit, source check, follow-up prompt and justified decision; no external chatbot needed. |
| 3 | Compare one image pair. Include a new HVAC example in the test. | Four choices checked with feedback; student can explain why visual polish is not proof of accuracy. No separate submission unless instructor assigns it. |
| 4 | Investigate one case. | Five short responses including justified verdict; separates observed pattern from possible cause and suggests further evidence. |
| 5 | Try an incorrect selection and retry 5.3; complete one Privacy Scanner case. | Feedback helps identify safe information handling, permission, risk and safer approach. |
| 6 | Try both valid sequences in 6.4 and complete one PAUSE case. | Both valid orders accepted; rights, source credit, AI disclosure and qualified review are distinct. |
| 7 | Compare AI and non-AI methods; choose non-AI in one test. | Both methods considered fairly; human skill, privacy, benefit/risk and verification addressed. |
| 8 | Complete one Model Rescue mission and certification workflow in a test course. | Report matches actual comparison evidence, includes limits, and transfers to career; assessment access and score handling verified without changing actual student grades. |

## C. Small timing pilot (recommended, not yet scheduled)

Invite two volunteers per lesson where feasible (16 lesson attempts, not necessarily 16 unique students). Include varied career programs, reading needs and devices; include learners using the available transcript or caption alternatives. Assign one lesson at a time rather than the whole course. Obtain applicable school permission and avoid using this as a graded test. Do not rush a student to meet a time target.

Record elapsed minutes for opening, watch/reading/checks, application, assessment and navigation/support. Note only lesson, broad device category, accessibility route, minutes, completion, help needed and a brief non-identifying issue. Collect student feedback through the existing approved channel; do not add a new public form or collect personal data.

Planning estimates: L1 53, L2 55, L3 54, L4 53, L5 52, L6 55–58, L7 54–57, L8 58–63 minutes. These are not observations. L8 is an unresolved pacing risk. If required work exceeds 60 minutes, locate the cause and reduce duplication or simplify an interaction without removing the essential objective. Do not shorten a student's assessment time as a remedy.

## D. Record and close

For each test record Pass, Fail, or Not tested; note expected versus observed behavior and the relevant revision ID. Mark student validation only when actual evidence supports it. Retest defects before closing. Keep teacher plans and existing Canvas/Google Classroom copies separate from the website release until synchronized. Do not overwrite existing submissions. The source course generator remains blocked against the older archive until its inputs are reconciled.

Do not claim production deployment, browser accessibility, or student timing solely from passing source tests.
