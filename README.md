# 📚 AI Study Coach

AI Study Coach is a simple AI-powered study assistant that converts students' notes or PDF study material into useful revision resources such as flashcards, quizzes, summaries, explanations, and study plans.

## 🎯 Problem

Students often have study notes but do not have enough time to turn them into quick revision material.

AI Study Coach solves this by automatically transforming raw study material into structured and editable revision content.

## 💡 Solution

The user can either:

- ✍️ Paste their notes
- 📄 Upload a PDF

The application then uses AI to generate:

- 🃏 Flashcards
- 📝 Quiz questions
- 📖 Summary
- 💡 Topic explanation
- 📅 Study plan

Users can also edit the generated flashcards and quiz questions before using them.

## ✨ Features

- Paste notes or upload a PDF
- AI-generated flashcards
- Editable flashcards
- Interactive quiz
- Editable quiz questions
- Quiz scoring
- Study plan generation
- Simple topic explanations
- Summary generation
- JSON export for flashcards
- JSON export for quizzes
- Quick Mode fallback when AI generation is unavailable

## 🛠️ Tech Stack

- Python
- Streamlit
- Google Gemini API
- PyPDF

## 🔄 How It Works

```text
Study Notes / PDF
       ↓
   AI Study Coach
       ↓
 ┌─────┼─────────────┐
 ↓     ↓             ↓
Flashcards  Quiz   Summary
 ↓          ↓
Edit       Answer
 ↓          ↓
JSON      Score
Export
```

## 🚀 Running the Project

### 1. Install the required packages

```bash
pip install streamlit google-genai pypdf
```

### 2. Set your Gemini API key

Set the environment variable:

```text
GEMINI_API_KEY
```

Do not share or upload your API key publicly.

### 3. Run the application

```bash
python -m streamlit run AIStudyCoach.py
```

## 📦 JSON Output

The application provides structured JSON output for easy editing and exporting.

### Flashcards

```json
{
    "flashcards": [
        {
            "question": "Question",
            "answer": "Answer"
        }
    ]
}
```

### Quiz

```json
{
    "quiz": [
        {
            "question": "Question",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": 0
        }
    ]
}
```

## 🏆 Hackathon Relevance

AI Study Coach addresses the challenge of helping students quickly convert existing study material into useful revision resources.

It supports:

- Pasted notes
- PDF study material
- AI-generated flashcards
- AI-generated quizzes
- Editable results
- Predictable JSON structure
- Exportable revision content

## 🔮 Future Improvements

- User accounts and saved study sets
- More question types
- Spaced-repetition flashcards
- Progress tracking
- Subject-wise organization
- Voice-based study assistance
- Support for additional document formats

## 👩‍💻 Team

**Solo Project — Aakriti Swaroop**

Built for Hacktoberfest Hack Day.