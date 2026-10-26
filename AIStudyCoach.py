import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader
import os
import json
import re
import random


# ==================================================
# PAGE SETUP
# ==================================================

st.set_page_config(
    page_title="AI Study Coach",
    page_icon="📚",
    layout="centered"
)


# ==================================================
# DESIGN
# ==================================================

st.markdown("""
<style>

.main {
    background-color: #faf8ff;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 850px;
}

.hero {
    background: linear-gradient(135deg, #eee7ff, #f8efff);
    padding: 30px;
    border-radius: 24px;
    text-align: center;
    margin-bottom: 25px;
    border: 1px solid #e4d9ff;
}

.hero h1 {
    color: #5b3b8c;
    font-size: 42px;
    margin-bottom: 8px;
}

.hero p {
    color: #6d6380;
    font-size: 17px;
}

.section-title {
    color: #5b3b8c;
    font-size: 24px;
    font-weight: 700;
    margin-top: 20px;
}

.quiz-card {
    background: white;
    padding: 25px;
    border-radius: 20px;
    border: 1px solid #e4d9ff;
    margin-top: 15px;
}

.result-card {
    background: linear-gradient(135deg, #f2ebff, #fff4fb);
    padding: 30px;
    border-radius: 24px;
    text-align: center;
    border: 1px solid #e4d9ff;
}

.result-score {
    font-size: 48px;
    font-weight: bold;
    color: #5b3b8c;
}

.quick-card {
    background: #f8f4ff;
    padding: 15px;
    border-radius: 14px;
    border: 1px solid #e4d9ff;
    margin-top: 10px;
}

.stButton > button {
    border-radius: 12px;
    border: none;
    font-weight: 600;
}

.footer {
    text-align: center;
    color: #8a8099;
    font-size: 13px;
    margin-top: 40px;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# HERO
# ==================================================

st.markdown("""
<div class="hero">

<h1>📚 AI Study Coach</h1>

<p>Your personal AI-powered study companion</p>

<p>✨ Learn • Practice • Revise • Improve</p>

</div>
""", unsafe_allow_html=True)

st.write(
    "Turn your study notes into personalized learning material using AI."
)


# ==================================================
# GEMINI CONNECTION
# ==================================================

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
    http_options=types.HttpOptions(
        timeout=15000,
        retry_options=types.HttpRetryOptions(
            attempts=1
        )
    )
)


# ==================================================
# GEMINI FUNCTION
# ==================================================

def generate_ai(prompt):

    try:

        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt
        )

        return response.text

    except Exception as e:

        error_message = str(e)

        if (
            "503" in error_message
            or "UNAVAILABLE" in error_message
            or "504" in error_message
            or "DEADLINE_EXCEEDED" in error_message
            or "timeout" in error_message.lower()
        ):

            return None

        else:

            raise e


# ==================================================
# CLEAN JSON
# ==================================================

def clean_json(text):

    if text is None:
        return None

    text = text.strip()

    text = text.replace(
        "```json",
        ""
    )

    text = text.replace(
        "```JSON",
        ""
    )

    text = text.replace(
        "```",
        ""
    )

    return text.strip()


# ==================================================
# QUICK MODE FUNCTIONS
# ==================================================

def clean_notes(notes):

    text = notes.replace(
        "\n",
        " "
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def get_sentences(notes):

    text = clean_notes(notes)

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) > 20
    ]

    return sentences


def get_keywords(notes):

    words = re.findall(
        r"\b[A-Za-z][A-Za-z\-]{4,}\b",
        notes
    )

    stop_words = {
        "which",
        "their",
        "there",
        "these",
        "those",
        "about",
        "where",
        "while",
        "would",
        "could",
        "should",
        "using",
        "through",
        "because",
        "between",
        "study",
        "notes",
        "important",
        "following",
        "other",
        "into",
        "from",
        "with",
        "that",
        "this",
        "have",
        "also",
        "such",
        "than",
        "when"
    }

    filtered = []

    for word in words:

        if word.lower() not in stop_words:
            filtered.append(word)

    unique = []

    for word in filtered:

        if word.lower() not in [
            item.lower()
            for item in unique
        ]:

            unique.append(word)

    return unique


# ==================================================
# QUICK SUMMARY
# ==================================================

def quick_summary(notes):

    sentences = get_sentences(notes)

    if len(sentences) == 0:
        return notes

    selected = sentences[:6]

    result = "### ⚡ Quick Summary\n\n"

    for sentence in selected:

        result += "- " + sentence + "\n"

    result += (
        "\n*Generated directly from your notes "
        "using Quick Mode.*"
    )

    return result


# ==================================================
# QUICK FLASHCARDS
# ==================================================

def quick_flashcards(notes):

    sentences = get_sentences(notes)

    keywords = get_keywords(notes)

    cards = []

    for sentence in sentences:

        matching_keyword = None

        for keyword in keywords:

            if keyword.lower() in sentence.lower():

                matching_keyword = keyword
                break

        if matching_keyword:

            question = (
                "What should you remember about "
                + matching_keyword
                + "?"
            )

            cards.append(
                {
                    "question": question,
                    "answer": sentence
                }
            )

        if len(cards) == 5:
            break

    if len(cards) == 0:

        cards.append(
            {
                "question": "What is the main idea of these notes?",
                "answer": clean_notes(notes)[:300]
            }
        )

    return cards


# ==================================================
# QUICK STUDY PLAN
# ==================================================

def quick_study_plan(notes):

    keywords = get_keywords(notes)

    topics = keywords[:6]

    if len(topics) == 0:

        topics = [
            "Main concepts from your notes"
        ]

    result = "### ⚡ Quick Study Plan\n\n"

    result += "#### 1. Important Topics\n"

    for topic in topics:

        result += "- " + topic + "\n"

    result += """

#### 2. First Study Session — 25 minutes

Read the complete notes once and understand the main ideas.

#### 3. Concept Revision — 20 minutes

Go through the important topics individually.

#### 4. Active Recall — 15 minutes

Close your notes and try to recall the important concepts.

#### 5. Practice — 20 minutes

Create questions from the notes and answer them.

#### 6. Final Revision — 10 minutes

Review the concepts that were difficult to remember.

#### ✅ Final Checklist

- Understand the main concepts
- Remember important definitions
- Review examples
- Practice important questions
- Revise difficult topics again

*Generated from your notes using Quick Mode.*
"""

    return result


# ==================================================
# QUICK EXPLANATION
# ==================================================

def quick_explanation(notes):

    sentences = get_sentences(notes)

    keywords = get_keywords(notes)

    result = "### ⚡ Quick Explanation\n\n"

    if len(sentences) == 0:

        result += clean_notes(notes)

        return result

    for i, sentence in enumerate(
        sentences[:6]
    ):

        if i < len(keywords):

            title = keywords[i]

        else:

            title = "Concept " + str(i + 1)

        result += (
            "#### "
            + title
            + "\n"
        )

        result += (
            sentence
            + "\n\n"
        )

        result += (
            "**Exam Tip:** Remember the key idea "
            "and how it connects to the topic.\n\n"
        )

    result += (
        "*Generated directly from your notes "
        "using Quick Mode.*"
    )

    return result


# ==================================================
# QUICK QUIZ
# ==================================================

def quick_quiz(notes):

    sentences = get_sentences(notes)

    keywords = get_keywords(notes)

    quiz = []

    if len(sentences) == 0:

        return None

    for sentence in sentences:

        sentence_keywords = []

        for keyword in keywords:

            if keyword.lower() in sentence.lower():

                sentence_keywords.append(keyword)

        if len(sentence_keywords) == 0:
            continue

        answer_word = sentence_keywords[0]

        question_text = re.sub(
            re.escape(answer_word),
            "________",
            sentence,
            count=1,
            flags=re.IGNORECASE
        )

        wrong_options = []

        for word in keywords:

            if word.lower() != answer_word.lower():

                wrong_options.append(word)

        if len(wrong_options) < 3:
            continue

        wrong_options = wrong_options[:3]

        options = [
            answer_word,
            wrong_options[0],
            wrong_options[1],
            wrong_options[2]
        ]

        random.shuffle(options)

        correct_index = options.index(
            answer_word
        )

        quiz.append(
            {
                "question":
                    "Complete the statement:\n\n"
                    + question_text,

                "options": options,

                "answer": correct_index
            }
        )

        if len(quiz) == 5:
            break

    if len(quiz) < 3:
        return None

    return quiz


# ==================================================
# SESSION STATE
# ==================================================

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = None

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_mode" not in st.session_state:
    st.session_state.quiz_mode = None

if "flashcards" not in st.session_state:
    st.session_state.flashcards = None

if "flashcard_mode" not in st.session_state:
    st.session_state.flashcard_mode = None


# ==================================================
# NOTES
# ==================================================

st.markdown(
    '<div class="section-title">📝 Your Study Notes</div>',
    unsafe_allow_html=True
)

input_method = st.radio(
    "Choose how you want to add your study material:",
    [
        "✍️ Paste Notes",
        "📄 Upload PDF"
    ],
    horizontal=True
)

notes = ""

if input_method == "✍️ Paste Notes":

    notes = st.text_area(
        "Paste your notes here:",
        height=220,
        placeholder=(
            "Paste your lecture notes, textbook "
            "content or study material here..."
        )
    )

else:

    uploaded_file = st.file_uploader(
        "Upload your study PDF:",
        type=["pdf"]
    )

    if uploaded_file is not None:

        try:

            pdf_reader = PdfReader(
                uploaded_file
            )

            pdf_text = ""

            for page in pdf_reader.pages:

                page_text = page.extract_text()

                if page_text:

                    pdf_text += (
                        page_text
                        + "\n"
                    )

            notes = pdf_text

            if notes.strip() != "":

                st.success(
                    "📄 PDF uploaded successfully!"
                )

                st.caption(
                    "Your PDF text has been extracted "
                    "and is ready for AI processing."
                )

            else:

                st.warning(
                    "⚠️ I couldn't extract text from this PDF. "
                    "Try a text-based PDF."
                )

        except Exception:

            st.error(
                "❌ Something went wrong while reading the PDF."
            )


# ==================================================
# SETTINGS
# ==================================================

col1, col2 = st.columns(2)

with col1:

    difficulty = st.selectbox(
        "🎯 Difficulty",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

with col2:

    feature = st.selectbox(
        "🧠 Study Mode",
        [
            "🃏 Flashcards",
            "📝 Quiz",
            "📚 Study Plan",
            "✨ Summary",
            "💡 Explain Topic"
        ]
    )


# ==================================================
# GENERATE BUTTON
# ==================================================

if st.button(
    "✨ Generate",
    use_container_width=True
):

    if notes.strip() == "":

        st.warning(
            "Please enter some study notes first."
        )

    else:

        # ==================================================
        # FLASHCARDS
        # ==================================================

        if feature == "🃏 Flashcards":

            prompt = """
Create exactly 5 useful flashcards
from these study notes.

Difficulty: {difficulty}

Return ONLY valid JSON.

Format:

[
  {{
    "question": "Question",
    "answer": "Answer"
  }}
]

Rules:

- Exactly 5 flashcards
- Use ONLY the study notes
- Keep questions clear
- Keep answers concise
- No markdown
- No explanations outside the JSON

Study Notes:

{notes}
""".format(
                difficulty=difficulty,
                notes=notes
            )

            with st.spinner(
                "🤖 Creating your flashcards..."
            ):

                try:

                    flashcard_text = generate_ai(
                        prompt
                    )

                except Exception:

                    flashcard_text = None

            flashcards = None

            if flashcard_text is not None:

                try:

                    cleaned = clean_json(
                        flashcard_text
                    )

                    flashcard_data = json.loads(
                        cleaned
                    )

                    if (
                        isinstance(
                            flashcard_data,
                            list
                        )
                        and len(
                            flashcard_data
                        ) == 5
                    ):

                        valid = True

                        for card in flashcard_data:

                            if (
                                "question" not in card
                                or "answer" not in card
                            ):

                                valid = False

                        if valid:

                            flashcards = (
                                flashcard_data
                            )

                            st.session_state.flashcard_mode = "AI"

                except Exception:

                    flashcards = None

            if flashcards is None:

                flashcards = quick_flashcards(
                    notes
                )

                st.session_state.flashcard_mode = "Quick"

            st.session_state.flashcards = flashcards

            st.rerun()


        # ==================================================
        # QUIZ
        # ==================================================

        elif feature == "📝 Quiz":

            prompt = """
Create exactly 5 multiple-choice questions
using ONLY these study notes.

Difficulty: {difficulty}

Return ONLY valid JSON.

Format:

[
  {{
    "question": "Question",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer": 0
  }}
]

The answer must be an integer from 0 to 3.

No markdown.
No explanations.

Study Notes:

{notes}
""".format(
                difficulty=difficulty,
                notes=notes
            )

            with st.spinner(
                "🤖 Creating your quiz..."
            ):

                try:

                    quiz_text = generate_ai(
                        prompt
                    )

                except Exception:

                    quiz_text = None

            quiz_data = None

            if quiz_text is not None:

                try:

                    quiz_text = clean_json(
                        quiz_text
                    )

                    quiz_data = json.loads(
                        quiz_text
                    )

                    if not (
                        isinstance(
                            quiz_data,
                            list
                        )
                        and len(
                            quiz_data
                        ) == 5
                    ):

                        quiz_data = None

                except Exception:

                    quiz_data = None

            if quiz_data is not None:

                st.session_state.quiz_mode = "AI"

            else:

                quiz_data = quick_quiz(
                    notes
                )

                if quiz_data is None:

                    st.error(
                        "Could not create a reliable quiz "
                        "from these notes."
                    )

                    st.stop()

                st.session_state.quiz_mode = "Quick"

            st.session_state.quiz = quiz_data

            st.session_state.quiz_index = 0

            st.session_state.quiz_answers = {}

            st.session_state.quiz_score = None

            st.session_state.quiz_submitted = False

            st.rerun()


        # ==================================================
        # OTHER MODES
        # ==================================================

        else:

            if feature == "📚 Study Plan":

                prompt = """
Create a practical study plan
from these notes.

Difficulty: {difficulty}

Include:

Important topics
Study order
Study time
Practice strategy
Revision strategy
Final checklist

Study Notes:

{notes}
""".format(
                    difficulty=difficulty,
                    notes=notes
                )

            elif feature == "✨ Summary":

                prompt = """
Summarize these study notes.

Difficulty: {difficulty}

Make the summary:

Simple
Clear
Exam-oriented
Easy to revise

Use headings and bullet points.

Study Notes:

{notes}
""".format(
                    difficulty=difficulty,
                    notes=notes
                )

            else:

                prompt = """
Explain the important concepts
from these notes.

Difficulty: {difficulty}

For each concept provide:

Simple explanation
Example
Exam point

Study Notes:

{notes}
""".format(
                    difficulty=difficulty,
                    notes=notes
                )

            with st.spinner(
                "🤖 Preparing your study material..."
            ):

                try:

                    result = generate_ai(
                        prompt
                    )

                except Exception:

                    result = None

            if result is not None:

                st.success(
                    "✨ Generated with Gemini AI"
                )

                if feature == "📚 Study Plan":

                    st.subheader(
                        "📚 Your Study Plan"
                    )

                elif feature == "✨ Summary":

                    st.subheader(
                        "✨ Smart Summary"
                    )

                else:

                    st.subheader(
                        "💡 AI Explanation"
                    )

                st.write(
                    result
                )

            else:

                st.info(
                    "⚡ Gemini is currently busy, "
                    "so Quick Mode was used."
                )

                if feature == "📚 Study Plan":

                    result = quick_study_plan(
                        notes
                    )

                elif feature == "✨ Summary":

                    result = quick_summary(
                        notes
                    )

                else:

                    result = quick_explanation(
                        notes
                    )

                st.markdown(
                    result
                )


# ==================================================
# EDITABLE FLASHCARDS
# ==================================================

if (
    feature == "🃏 Flashcards"
    and st.session_state.flashcards is not None
):

    flashcards = st.session_state.flashcards

    st.divider()

    if (
        st.session_state.flashcard_mode
        == "AI"
    ):

        st.success(
            "✨ Flashcards generated with Gemini AI"
        )

    else:

        st.info(
            "⚡ Gemini was busy, so these flashcards "
            "were generated using Quick Mode."
        )

    st.subheader(
        "🧠 Your Flashcards"
    )

    st.write(
        "✏️ Edit the questions or answers before exporting."
    )

    edited_flashcards = []

    for i, card in enumerate(
        flashcards
    ):

        st.markdown(
            "### 🃏 Flashcard "
            + str(i + 1)
        )

        question = st.text_area(
            "Question",
            value=card.get(
                "question",
                ""
            ),
            key="flashcard_question_" + str(i)
        )

        answer = st.text_area(
            "Answer",
            value=card.get(
                "answer",
                ""
            ),
            key="flashcard_answer_" + str(i)
        )

        edited_flashcards.append(
            {
                "question": question,
                "answer": answer
            }
        )

    st.session_state.flashcards = (
        edited_flashcards
    )

    export_data = {
        "flashcards": edited_flashcards
    }

    json_file = json.dumps(
        export_data,
        indent=4,
        ensure_ascii=False
    )

    st.download_button(
        "📥 Download Flashcards as JSON",
        data=json_file,
        file_name="AI_Study_Coach_Flashcards.json",
        mime="application/json",
        use_container_width=True
    )


# ==================================================
# INTERACTIVE QUIZ
# ==================================================

if (
    feature == "📝 Quiz"
    and st.session_state.quiz is not None
):

    quiz = st.session_state.quiz

    st.divider()

    if (
        st.session_state.quiz_mode
        == "Quick"
    ):

        st.info(
            "⚡ Gemini was busy, so this quiz "
            "was generated directly from your notes "
            "using Quick Mode."
        )

    else:

        st.success(
            "✨ Quiz generated with Gemini AI"
        )


    # ==================================================
    # EDIT QUIZ
    # ==================================================

    with st.expander(
        "✏️ Edit Quiz Before Starting"
    ):

        st.write(
            "You can edit the questions, options "
            "and correct answers."
        )

        for i, question in enumerate(
            quiz
        ):

            st.markdown(
                "### Question "
                + str(i + 1)
            )

            question["question"] = st.text_area(
                "Question",
                value=question["question"],
                key="edit_quiz_question_" + str(i)
            )

            for j in range(4):

                question["options"][j] = st.text_input(
                    "Option "
                    + str(j + 1),
                    value=question["options"][j],
                    key=(
                        "edit_quiz_option_"
                        + str(i)
                        + "_"
                        + str(j)
                    )
                )

            answer_number = st.selectbox(
                "Correct Answer",
                [
                    1,
                    2,
                    3,
                    4
                ],
                index=question["answer"],
                key="edit_quiz_answer_" + str(i)
            )

            question["answer"] = (
                answer_number - 1
            )

            st.divider()


    # ==================================================
    # QUIZ IN PROGRESS
    # ==================================================

    if not st.session_state.quiz_submitted:

        current = (
            st.session_state.quiz_index
        )

        question = quiz[current]

        st.markdown(
            """
            <div class="quiz-card">
            <h3>
            📝 Question {0} of {1}
            </h3>
            </div>
            """.format(
                current + 1,
                len(quiz)
            ),
            unsafe_allow_html=True
        )

        progress = (
            current + 1
        ) / len(quiz)

        st.progress(
            progress
        )

        st.write("")

        st.markdown(
            "### "
            + question["question"]
        )

        selected = st.radio(
            "Choose your answer:",
            question["options"],
            index=None,
            key="question_" + str(current)
        )

        st.write("")


        # ==================================================
        # NEXT
        # ==================================================

        if current < len(quiz) - 1:

            if st.button(
                "Next →",
                use_container_width=True
            ):

                if selected is None:

                    st.warning(
                        "Please select an answer."
                    )

                else:

                    st.session_state.quiz_answers[
                        current
                    ] = selected

                    st.session_state.quiz_index += 1

                    st.rerun()


        # ==================================================
        # SUBMIT
        # ==================================================

        else:

            if st.button(
                "🎯 Submit Quiz",
                use_container_width=True
            ):

                if selected is None:

                    st.warning(
                        "Please select an answer."
                    )

                else:

                    st.session_state.quiz_answers[
                        current
                    ] = selected

                    score = 0

                    for i in range(
                        len(quiz)
                    ):

                        correct_answer = (
                            quiz[i]["options"][
                                quiz[i]["answer"]
                            ]
                        )

                        user_answer = (
                            st.session_state
                            .quiz_answers
                            .get(i)
                        )

                        if (
                            user_answer
                            == correct_answer
                        ):

                            score += 1

                    st.session_state.quiz_score = (
                        score
                    )

                    st.session_state.quiz_submitted = (
                        True
                    )

                    st.rerun()


    # ==================================================
    # RESULTS
    # ==================================================

    else:

        score = (
            st.session_state.quiz_score
        )

        total = len(
            quiz
        )

        percentage = int(
            (score / total) * 100
        )

        st.markdown(
            """
            <div class="result-card">

            <h2>🎉 Quiz Complete!</h2>

            <div class="result-score">
            {0} / {1}
            </div>

            <p>{2}%</p>

            </div>
            """.format(
                score,
                total,
                percentage
            ),
            unsafe_allow_html=True
        )

        st.write("")

        if percentage == 100:

            st.success(
                "🏆 Perfect score! "
                "You absolutely nailed it!"
            )

        elif percentage >= 80:

            st.success(
                "🔥 Great job! "
                "You understand this topic really well!"
            )

        elif percentage >= 60:

            st.info(
                "👍 Good effort! "
                "A little more revision will help."
            )

        else:

            st.warning(
                "📚 Keep practicing! "
                "Review your notes and try again."
            )


        # ==================================================
        # ANSWER REVIEW
        # ==================================================

        st.subheader(
            "📋 Answer Review"
        )

        for i in range(
            total
        ):

            correct_answer = (
                quiz[i]["options"][
                    quiz[i]["answer"]
                ]
            )

            user_answer = (
                st.session_state
                .quiz_answers
                .get(i)
            )

            st.write(
                "**Question "
                + str(i + 1)
                + ":** "
                + quiz[i]["question"]
            )

            if (
                user_answer
                == correct_answer
            ):

                st.success(
                    "✅ Your answer: "
                    + str(user_answer)
                )

            else:

                st.error(
                    "❌ Your answer: "
                    + str(user_answer)
                )

                st.info(
                    "Correct answer: "
                    + str(correct_answer)
                )


        # ==================================================
        # EXPORT QUIZ
        # ==================================================

        export_quiz = {
            "quiz": quiz
        }

        quiz_json = json.dumps(
            export_quiz,
            indent=4,
            ensure_ascii=False
        )

        st.download_button(
            "📥 Download Quiz as JSON",
            data=quiz_json,
            file_name="AI_Study_Coach_Quiz.json",
            mime="application/json",
            use_container_width=True
        )


        # ==================================================
        # NEW QUIZ
        # ==================================================

        st.write("")

        if st.button(
            "🔄 Try Another Quiz",
            use_container_width=True
        ):

            st.session_state.quiz = None

            st.session_state.quiz_index = 0

            st.session_state.quiz_answers = {}

            st.session_state.quiz_score = None

            st.session_state.quiz_submitted = False

            st.session_state.quiz_mode = None

            st.rerun()


# ==================================================
# FOOTER
# ==================================================

st.markdown(
    """
    <div class="footer">
    Built with ❤️ using Python, Streamlit & Gemini AI
    </div>
    """,
    unsafe_allow_html=True
)