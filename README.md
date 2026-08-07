# AI Literacy Student Course

Eight student-facing AI literacy lessons designed for online course delivery. Each lesson pages through six numbered steps and includes an accessible progress indicator, a practical activity, and a linked Google Form assessment.

## Local preview

Run a static server from the repository root:

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Rebuild from the source course archive

The extracted package is intentionally ignored by Git. Run:

```powershell
python tools/build_course.py
```

The generator rebuilds the lesson pages, copies course media, and exports the cumulative assessment to `ASSESSMENT.md` and `assessment-questions.json`.
