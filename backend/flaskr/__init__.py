from flask_cors import CORS

from flask import (
    Flask,
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

        return jsonify({
            "success": True,
            "questions": [question.format() for question in questions],
            "total_questions": len(totalQuestions),
            "categories": {category.id : category.type for category in categories},
            "current_category": None
        })

    @app.route("/questions", methods=["POST"])
    def createQuestion():
        body = request.get_json()

        question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)

        question = Question(question, answer, category, difficulty)
        questionId = question.id
        status = question.insert()

        if status:
            return jsonify({
                "success": status,
                "created": questionId
            })
        else:
            abort(422)

    @app.route("/questions/<int:id>", methods=["DELETE"])
    def deleteQuestion(id):
        question = Question.query.get_or_404(id)
        status = question.delete()
        if status:
            return jsonify({
                "success": status,
                "deleted": id
            })
        else:
            abort(422)

    @app.errorhandler(404)
    def notFound(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

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
