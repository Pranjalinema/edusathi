
from flask import Flask, render_template, request, jsonify
import os
from google import genai
import mysql.connector

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="edusathi"
    )


# Gemini AI client
client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)

# Supported classes and subjects
VALID_CLASSES = [6, 7, 8, 9, 10]

VALID_SUBJECTS = [
    "mathematics",
    "science",
    "english",
    "social-science"
]


# AI Study Assistant
@app.route("/ask-ai", methods=["POST"])
def ask_ai():
    data = request.get_json() or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "Please enter a question."}), 400

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=(
                "You are EduSathi's friendly AI study assistant. "
                "Explain concepts in simple language for school students. "
                "Help with learning and practice questions. "
                "Student's question: " + question
            )
        )
        return jsonify({"answer": response.text})

    except Exception:
        app.logger.exception("Gemini API request failed")
        return jsonify({
            "answer": (
                "Sorry, the AI assistant is temporarily unavailable. "
                "Please try again."
            )
        }), 503


# Homepage
@app.route("/")
def home():
    return render_template("index.html")


# AI assistant page
@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


# Existing quiz page
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


# Courses page
@app.route("/courses")
def courses():
    return render_template("courses.html")


# Class page
@app.route("/class/<int:class_id>")
def class_page(class_id):
    if class_id not in VALID_CLASSES:
        return "Class not found", 404

    return render_template("class.html", class_id=class_id)


# Subject page
@app.route("/class/<int:class_id>/subject/<subject_name>")
def subject_page(class_id, subject_name):
    if class_id not in VALID_CLASSES:
        return "Class not found", 404

    if subject_name not in VALID_SUBJECTS:
        return "Subject not found", 404

    return render_template(
        "mathematics.html",
        class_id=class_id,
        subject_name=subject_name
    )


# Backward-compatible Mathematics link
@app.route("/subject/mathematics")
def mathematics():
    return render_template(
        "mathematics.html",
        class_id=6,
        subject_name="mathematics"
    )


# Chapter page
@app.route(
    "/class/<int:class_id>/subject/<subject_name>/chapter/<int:chapter_id>"
)
def chapter_page(class_id, subject_name, chapter_id):
    if class_id not in VALID_CLASSES:
        return "Class not found", 404

    if subject_name not in VALID_SUBJECTS:
        return "Subject not found", 404

    if chapter_id not in [1, 2, 3]:
        return "Chapter not found", 404

    return render_template(
        "chapter.html",
        class_id=class_id,
        subject_name=subject_name,
        chapter_id=chapter_id
    )


# Chapter resource pages
@app.route(
    "/class/<int:class_id>/subject/<subject_name>/chapter/"
    "<int:chapter_id>/<content_type>"
)
def chapter_content(class_id, subject_name, chapter_id, content_type):
    if class_id not in VALID_CLASSES:
        return "Class not found", 404

    if subject_name not in VALID_SUBJECTS:
        return "Subject not found", 404

    if chapter_id not in [1, 2, 3]:
        return "Chapter not found", 404

    messages = {
        "video": "No lecture available yet.",
        "notes": "No notes available yet.",
        "quiz": "No quiz available yet."
    }

    if content_type not in messages:
        return "Content not found", 404

    return render_template(
        "unavailable.html",
        class_id=class_id,
        subject_name=subject_name,
        chapter_id=chapter_id,
        message=messages[content_type]
    )


# Database connection test
@app.route("/test-db")
def test_db():
    try:
        connection = get_db_connection()
        connection.close()
        return "EduSathi database connected successfully!"
    except Exception:
        app.logger.exception("Database connection failed")
        return "Database connection failed. Check the Flask terminal.", 500


if __name__ == "__main__":
    app.run(debug=True)
