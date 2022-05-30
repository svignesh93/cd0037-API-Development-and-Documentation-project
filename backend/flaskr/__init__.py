import os
import random
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from flask import (
    Flask,
    render_template,
    request,
    abort,
    jsonify
)

from models import (
    setup_db,
    Question,
    Category
)

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Methods", "GET, PATCH, POST, DELETE, OPTIONS")
        return response

    @app.route("/categories", methods=["GET"])
    def categories():
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "categories": {category.id : category.type for category in categories},
            "total_categories": len(categories)
        })

    @app.route("/questions", methods=["GET"])
    def questions():
        totalQuestions = Question.query.order_by(Question.id).all()
        questions = paginate(request, totalQuestions)

        categories = Category.query.order_by(Category.id).all()

        if len(questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": [question.format() for question in questions],
                "total_questions": len(totalQuestions),
                "categories": {category.id : category.type for category in categories},
                "current_category": None
            }
        )

    @app.errorhandler(404)
    def notFound(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

def paginate(request, records):
    RECORDS_LIMIT = 10

    page = request.args.get("page", 1, type=int)
    start = (page - 1) * RECORDS_LIMIT
    end = start + RECORDS_LIMIT

    result = records[start:end]

    return result
