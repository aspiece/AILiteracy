# AI Literacy Lesson Graphics Audit

**Audit date:** August 7, 2026  
**Scope:** Lessons 1–8, including existing graphics, repeated graphics, image-based activities, and major instructional gaps  
**Standard used:** A graphic should clarify a relationship, process, decision, comparison, or practice task that would be harder to understand from text alone. Decorative images are not recommended.

> **Implementation status:** Phases 1–3 and the post-audit refinements were completed on August 8, 2026. The findings below preserve the original baseline; completed work is marked in the production plan.

## Executive summary

The course has several strong instructional infographics and an unusually useful image-comparison activity in Lesson 3. The main weakness is uneven distribution. Lessons 3–5 contain most of the visual support, while Lessons 2, 6, 7, and 8 include long or abstract explanations with few visuals. Lesson 7 is the highest-priority gap: Step 7.4 contains roughly 1,250 words and a video but no graphic to organize benefits, access, workforce, and environmental impacts.

Three completed graphics are already stored in `assets/media` but are not currently used:

- `M01_5TipPromptFormula_v1.png`
- `M01_3StepAuditProcess_v1.png`
- `M01_AIReviewBoard_v1.png`

Using these assets would immediately improve Lessons 2 and 4 without creating new artwork.

### Highest-priority actions

1. Add the existing **5-Tip Prompting Formula** to Step 2.3.
2. Add the existing **3-Step Audit Process** to Step 2.4.
3. Use the existing **Five-Step AI Review Board Investigation** in Step 4.5 instead of the more general Responsible AI Routine graphic.
4. Add two new organizing graphics to Lesson 7: an **AI Task Change Continuum** and a **Career Impact Balance Map**.
5. Replace the five-step model-improvement image in Step 8.3 with a graphic that matches the stated **six-step model-building cycle**.
6. Add image enlargement to all text-heavy infographics and all Step 3.5 comparison images.
7. Replace or retire the older `M01_ResponsibleAIRoutine_v1.png` so the course uses one consistent Responsible AI Routine design.

## Course-wide findings

### What is working

- Most images have meaningful alternative text.
- The strongest graphics explain a decision or process rather than decorate the page.
- Lesson 3.5 uses images as evidence in an authentic comparison task.
- Lesson 4 uses a coherent sequence: risk level, bias warning signs, and human oversight.
- The new Responsible AI Routine graphic is readable, mobile-friendly, enlargeable, and available in web and print formats.

### What should be updated

- **Two Responsible AI Routine designs are in use.** Lessons 2–8 still use the older horizontal “AI Decision Pathway” in their overviews, while selected application steps use the newer vertical routine. This creates unnecessary visual inconsistency.
- **Complex infographics need enlargement.** Several portrait graphics contain substantial text that becomes small on a phone. The click-to-enlarge behavior should be reusable for every complex infographic, not only the Responsible AI Routine.
- **Complex-image alternatives need parity.** Short alt text identifies the image, but a complex flowchart or checklist also needs nearby HTML text that communicates the same steps and relationships.
- **Visual captions should tell students what to do.** Captions should use a single focus such as “Use this diagram to decide where a trained person must review the result.”
- **Color should not carry meaning alone.** Green/yellow/red graphics currently include labels and icons, which is good. Preserve those redundant cues in all future graphics.
- **Text inside images should remain limited.** New graphics should use short labels and move detailed explanations into nearby HTML so they remain readable, translatable, and accessible.

## Lesson-by-lesson audit

| Lesson | Current visual support | Does it enhance learning? | Update needed | Recommended additions | Priority |
|---|---|---|---|---|---|
| **1. Humans Behind AI** | New Responsible AI Routine in 1.1; Model Improvement Cycle in 1.3 | Yes. Both graphics establish recurring mental models. | The model cycle is helpful, but Step 1.5 is named “Human Decisions Map” and has no actual map. | Create a Human Decisions Map showing what AI may do versus what a trained person must decide. | High |
| **2. Prompt Like a Pro** | Older routine graphic in 2.1; videos but no step-specific graphics | The routine adds limited value here because it is generic. The prompting and auditing concepts need direct visual support. | Replace/retire the old routine design. | Place the existing 5-Tip Prompting Formula in 2.3 and existing 3-Step Audit Process in 2.4. | Critical |
| **3. Verify Before You Trust** | Routine overview; four-image media example; 15 comparison pairs in 3.5 | Strong. Images are evidence and are essential to the learning task. | Add enlargement to the four-image example and every comparison image. Confirm all intentionally unsafe examples are labeled in surrounding HTML as fictional practice material. | Add a small Pause–Trace–Check–Decide–Disclose visual only if this exact routine is used repeatedly in the text. | High |
| **4. The Bias Trap** | Routine overview; risk guide; bias red flags; human oversight flowchart; routine in 4.5 | Strongest visual sequence in the course. Each graphic supports a distinct decision. | The Step 4.4 alt text incorrectly describes the Human Oversight Flowchart as a data-security flowchart. Step 4.5 uses a generic routine even though a task-specific review-board graphic already exists. | Use `M01_AIReviewBoard_v1.png` in 4.5. Keep the routine as a small text reminder instead of a second full infographic. | High |
| **5. Privacy Shield** | Routine overview; Privacy Scanner; Responsible AI Routine; Confidential Information guide | The privacy-specific graphics strongly support decisions. | Step 5.2 is visually crowded with two large infographics. Move the full routine reminder to 5.5 or reduce it to a compact text cue. Add enlargement to both privacy infographics. | Consider a “Minimum Necessary Data” before/after prompt example using fictional data. | Medium |
| **6. Create with Integrity** | Routine overview and routine in 6.5; no copyright-, permission-, attribution-, or disclosure-specific graphic | The routine reinforces responsibility, but it does not explain the new concepts students must apply. | Add direct visual support for permission and disclosure. | Create a Copyright and Permission Decision Path and an “Anatomy of an AI-Use Disclosure” example. | Critical |
| **7. Level Up** | Older routine graphic in 7.1; no other images | Insufficient. The lesson covers task change, augmentation, human-led work, access, social effects, and environmental costs without a visual organizer. | Add visuals to 7.3 and 7.4; do not add decorative career photos. | Create an AI Task Change Continuum and a Career Impact Balance Map. Optionally add one career-task before/after example. | Critical |
| **8. Build, Test, Improve** | Routine overview; five-step Model Improvement Cycle in 8.3; routine in 8.5 | The cycle is useful, but it conflicts with the step title and text, which describe six steps. | Replace the five-step cycle with a six-step model-building cycle. Add a visual for uneven model performance in 8.2. | Create a Six-Step Model-Building Cycle and an Uneven Outcomes comparison graphic. | Critical |

## Existing graphic decisions

| Graphic | Current use | Recommendation | Rationale |
|---|---|---|---|
| New Responsible AI Routine web/mobile graphic | 1.1, 4.5, 5.2, 6.5, 8.5 | Keep in 1.1. Use selectively at true transfer points. | Excellent recurring framework, but full-size repetition can crowd step-specific instruction. |
| `M01_ResponsibleAIRoutine_v1.png` | Overviews 2–8 | Replace with the new design or a compact horizontal version derived from it. | The old and new designs compete visually and use different naming (“Decision Pathway” versus “Responsible AI Routine”). |
| `M01_ModelImprovementCycle_v1.png` | 1.3 and 8.3 | Keep in 1.3; replace in 8.3. | It accurately supports introductory learning but does not match the six-step model-building instruction in Lesson 8. |
| `M01_MediaAuditExamples_v1.jpg` | 3.2 | Keep, add enlargement, and add a focused caption. | It supports observation and questioning, but details are difficult to inspect at mobile size. |
| Step 3.5 comparison set | 3.5 | Keep; add enlargement and verify surrounding fictional-practice labels. | This is the most instructionally authentic image use in the course. |
| `M01_AIDecisionGuide_v1.png` | 4.2 | Keep; make enlargeable. | Clear risk classification with words, icons, and examples. |
| `M01_BiasRedFlags_v1.png` | 4.3 | Keep; make enlargeable and provide the checklist in HTML. | Useful scanning checklist, but text is dense for a phone screen. |
| `M01_HumanOversightFlowchart_v1.png` | 4.4 | Keep; correct alt text and make enlargeable. | Excellent match to the lesson. The current alt text is inaccurate. |
| `M01_PrivacyScanner_v1.png` | 5.2 | Keep; make enlargeable. | Strong decision aid using redundant labels and symbols. |
| `M01_ConfidentialInformation_v1.png` | 5.4 | Keep; make enlargeable and mirror categories in HTML. | Relevant and concrete, but text-heavy. |
| `M01_5TipPromptFormula_v1.png` | Unused | Add to 2.3. | Already aligned to the exact instructional concept. |
| `M01_3StepAuditProcess_v1.png` | Unused | Add to 2.4. | Already aligned to checking and improving AI responses. |
| `M01_AIReviewBoard_v1.png` | Unused | Add to 4.5. | More specific to the activity than the generic routine graphic. |

## New and revised graphic prompts

The prompts below assume the established course style: white background, navy headings, teal/blue structure, orange for “Check,” green for safe/protective actions, thick high-contrast outlines, simple flat icons, generous whitespace, and no decorative stock-photo background.

### 1. Human Decisions Map — Lesson 1.5

**Purpose:** Show the boundary between AI assistance and accountable human decisions.

**Generation prompt:**

> Create a student-facing educational infographic titled “Human Decisions Map.” Use a two-column pathway for grades 7–8. Left column: “AI may help” with four concise cards—sort information, find patterns, draft options, make a recommendation. Right column: “A trained person must” with four cards—check evidence, consider the full situation, make high-impact decisions, take responsibility. Connect each AI card to a human-review card with arrows. Add a bottom rule: “The greater the effect on health, safety, rights, money, education, reputation, or the future, the more human review is needed.” Use a white background, navy text, teal and blue cards, orange review icons, simple flat vector symbols, large readable type, no gradients behind text, no photographs, no logos, and no tiny body copy. 1600×1000 landscape.

### 2. Five-Tip Prompting Formula — Lesson 2.3 update

**Use existing asset:** `M01_5TipPromptFormula_v1.png`

**Update prompt if revising:**

> Revise the existing “Build a Better Prompt: The 5-Tip Prompting Formula” infographic for mobile accessibility. Preserve the five concepts: Specificity, Role, Format, Interactive Questions, and Tone. Increase the smallest text, shorten each supporting question to one line where possible, preserve numbered icons and color-independent labels, and export a 1200-pixel mobile version plus an 8.5×11 print version. Do not change the instructional meaning or add new tips.

### 3. Three-Step Audit Process — Lesson 2.4 update

**Use existing asset:** `M01_3StepAuditProcess_v1.png`

**Update prompt if revising:**

> Revise the existing “Check and Improve AI Responses: The 3-Step Audit Process” infographic for mobile use. Preserve: 1 Check Facts—Is it accurate? 2 Find Gaps—What is missing? 3 Ask Again—What should improve? Make the three steps equally prominent, enlarge the supporting questions, and add a bottom reminder: “You are responsible for checking the final work.” Use large readable type, simple icons, a white background, navy/teal/blue/orange accents, and export web/mobile and print versions.

### 4. AI Review Board Investigation — Lesson 4.5 update

**Use existing asset:** `M01_AIReviewBoard_v1.png`

**Update prompt if revising:**

> Create a mobile-friendly revision of the “Five-Step AI Review Board Investigation” graphic. Preserve the five steps: Identify the AI’s Role; Find Possible Harm; Require a Human Check; Create a Safer Rule; Give the Verdict. Shorten supporting text to one question per step and retain the verdict labels Green Light, Yellow Light, and Red Light. Add a bottom statement: “Investigate the evidence before deciding.” Use accessible color contrast, labels in addition to color, simple flat icons, and both 1200-pixel web/mobile and 8.5×11 print layouts.

### 5. Minimum Necessary Data — Lesson 5.5

**Purpose:** Turn privacy principles into a concrete editing action.

**Generation prompt:**

> Create a before-and-after educational infographic titled “Use Only the Information You Need.” Left panel labeled “Too Much Information” shows a fictional prompt containing a person’s full name, phone number, account number, employer file details, and exact incident date, with those details visibly crossed out. Right panel labeled “Safer Version” shows a rewritten fictional prompt using only a general role, a fictional situation, and the task goal. Add three checks: permission confirmed, identifying details removed, approved tool used. Clearly label all examples “Fictional practice example.” Use large readable text, high contrast, no real personal data, no real company names, and no realistic identification documents. 1600×1000 landscape.

### 6. Copyright and Permission Decision Path — Lesson 6.3

**Purpose:** Help students distinguish access, permission, license, credit, and AI disclosure.

**Generation prompt:**

> Create a student-facing flowchart titled “May I Use and Share This?” Start with “Did I create every part myself?” If no, ask: “Do I have permission or a license?” Then ask: “What credit is required?” Then ask: “Did AI help create or revise it?” End with two outcomes: “Ready to share with credit and disclosure” or “Stop and get permission, replace the material, or ask for help.” Include a visible note: “Finding something online does not give permission to use it.” Use plain grade 7–8 language, navy/teal/blue/orange colors, yes/no labels plus arrows, large type, simple icons, no legal seals, and no claim that the graphic is legal advice. 1400×1100 portrait.

### 7. Anatomy of an AI-Use Disclosure — Lesson 6.4 or 6.5

**Purpose:** Model what transparent disclosure looks like.

**Generation prompt:**

> Create an annotated example titled “A Clear AI-Use Disclosure.” Show one short fictional disclosure: “I used an approved AI tool to brainstorm three headings. I chose one heading, wrote the full draft, checked the facts, and revised the final work.” Add four callout labels pointing to the sentence: tool or type of help; specific task AI performed; work the student completed; checking and revision. Add a small reminder: “Follow your course or workplace rules.” Use a clean document-style layout, large readable text, accessible callout lines, navy and teal with orange highlights, and no logos or branded AI interfaces. 1600×900 landscape.

### 8. AI Task Change Continuum — Lesson 7.3

**Purpose:** Distinguish automation, augmentation, and human-led work.

**Generation prompt:**

> Create an educational continuum titled “How AI Can Change a Task.” Show three clearly separated zones from left to right: “Automated step” — AI completes a limited repeatable step; “Augmented work” — AI and a person work together; “Human-led decision” — a trained person interprets evidence and makes the final choice. Use one consistent fictional workplace example across all three zones, such as organizing maintenance requests, drafting a summary, and approving a safety response. Add a bottom question: “Where must human skill, judgment, and responsibility remain?” Use labels and icons rather than color alone, large text, diverse but simple flat human figures, no robots replacing workers, and 1600×900 landscape.

### 9. Career Impact Balance Map — Lesson 7.4

**Purpose:** Organize a long section on benefits, harms, access, skills, and environmental effects.

**Generation prompt:**

> Create a four-part decision map titled “Look at the Full Impact of AI.” Center circle: “Proposed AI use.” Four surrounding sections: “Work and Skills” with time saved, skills gained, and skills at risk; “People and Fairness” with who benefits, who may be excluded, and who can appeal; “Access” with cost, language, disability access, equipment, and training; “Resources and Environment” with energy, devices, data centers, and waste. Finish with the question: “What safeguards would improve the outcome?” Use neutral, balanced language; no claim that AI is always good or always harmful; large readable type; strong contrast; simple icons; and 1600×1200 landscape.

### 10. Uneven Outcomes Comparison — Lesson 8.2

**Purpose:** Make group-level performance differences visible without stereotyping people.

**Generation prompt:**

> Create a fictional data graphic titled “One Accuracy Score Can Hide Uneven Results.” Show an overall model accuracy of 90%, then three clearly labeled fictional test groups with results of 96%, 91%, and 68%. Use neutral labels “Test Group A,” “Test Group B,” and “Test Group C,” not demographic stereotypes or human portraits. Add three review questions: Is each group represented in the test data? Which errors matter most? What must improve before use? Include a note: “Fictional practice data.” Use a simple accessible bar chart with direct value labels, patterns or icons in addition to color, and large text. 1600×900 landscape.

### 11. Six-Step Model-Building Cycle — Lesson 8.3 replacement

**Purpose:** Align the graphic with the actual six-step instruction.

**Generation prompt:**

> Create a circular educational infographic titled “The Six-Step Model-Building Cycle.” Use these six numbered steps: 1 Define the goal and success criteria; 2 Collect and prepare appropriate data; 3 Train the model; 4 Test results and compare groups; 5 Improve data, rules, or training; 6 Monitor use and keep human responsibility. Show an arrow returning from Step 6 to Step 1 to communicate ongoing improvement. Add a center statement: “People make choices at every step.” Use grade 7–8 language, white background, navy headings, blue/teal/green/orange accents, simple flat icons, large readable type, no code screenshots, and no claim that one cycle guarantees fairness or accuracy. Export 1600×1200 landscape plus a mobile portrait version.

## Recommended production order

### Phase 1 — Use and repair what already exists

- [x] Place the existing Lesson 2 graphics.
- [x] Place the existing AI Review Board graphic in 4.5.
- [x] Correct the Human Oversight Flowchart alt text.
- [x] Add enlargement to all complex infographics and Lesson 3 comparison images.
- [x] Standardize the Responsible AI Routine design.

### Phase 2 — Fill the highest-value gaps

- [x] AI Task Change Continuum for 7.3.
- [x] Career Impact Balance Map for 7.4.
- [x] Six-Step Model-Building Cycle for 8.3.
- [x] Copyright and Permission Decision Path for 6.3.
- [x] Human Decisions Map for 1.5.

### Phase 3 — Add supporting examples

- [x] AI-use disclosure anatomy for Lesson 6.4.
- [x] Uneven outcomes comparison for 8.2.
- [x] Minimum Necessary Data example for 5.5.

### Post-audit refinements

- [x] Replace the second full-size graphic in 5.2 with a compact Responsible AI Routine reminder.
- [x] Add an explicit fictional-practice-material notice to 3.5.
- [x] Add the Pause–Trace–Check–Decide–Disclose process graphic to Lesson 3.
- [x] Add a fictional career-task before/after example to 7.3.
- [x] Export mobile and print formats for the selected Lesson 2, 4, and 8 reference graphics.

## Quality checklist for every new graphic

- The image teaches a relationship, process, decision, comparison, or practice—not decoration.
- The instructional purpose can be stated in one sentence.
- The page tells students what to notice or do with the graphic.
- Essential text remains readable on a phone or is available in nearby HTML.
- The image can be enlarged with mouse and keyboard.
- Alt text describes the instructional meaning, not just the appearance.
- Complex content has an equivalent HTML explanation.
- Color is not the only way meaning is communicated.
- People are represented without stereotypes or tokenism.
- Fictional examples are clearly labeled.
- Web/mobile and print versions are exported when students may use the graphic as a reference.
- The graphic follows the established course visual system and uses the same term names as the lesson.
