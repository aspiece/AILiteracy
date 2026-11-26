# AI Literacy Student Course

Eight student-facing AI literacy lessons designed for online course delivery. Each lesson pages through six numbered steps and includes an accessible progress indicator, a practical activity, and a linked Google Form assessment.

## Local preview

Run a static server from the repository root:

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Pilot release validation

See [the student experience validation checklist](docs/pilot-validation-checklist.md). The revised published lesson HTML and worksheet text are the current source of truth. Test the deployed course on authorized student devices before closing pilot feedback items.

## Rebuild from the source course archive

**Important:** The original archive does not contain the November 2026 pilot revisions. The generator stops when it detects the revised lesson pages. Reconcile the archived source and question bank in a separate review branch before generating replacement pages. Do not overwrite the revised pages or assessment banks from the old archive.

The extracted package is intentionally ignored by Git. Run:

```powershell
python tools/build_course.py
```

The generator rebuilds the lesson pages, copies course media, and exports the cumulative assessment to `ASSESSMENT.md` and `assessment-questions.json`.
