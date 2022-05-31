import random
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
        totalCategories = Category.query.order_by(Category.id).all()
        categories = paginate(request, totalCategories)

        if len(categories) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "categories": {category.id : category.type for category in categories},
            "total_categories": len(totalCategories)
        })

    @app.route("/categories/<int:id>/questions", methods=["GET"])
    def questionsByCategory(id):
        category = Category.query.get_or_404(id)

        totalQuestions = Question.query.filter_by(category = id).order_by(Question.id).all()
        questions = paginate(request, totalQuestions)

        if len(questions) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": [question.format() for question in questions],
            "total_questions": len(totalQuestions),
            "current_category": category.type
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

        if question is None:
            abort(400)

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

    @app.route("/questions/search", methods=["POST"])
    def searchQuestion():
        body = request.get_json()

        searchTerm = body.get("searchTerm", None)

        totalQuestions = Question.query.filter(
            Question.question.ilike("%{}%".format(searchTerm))
        ).order_by(
            Question.id
        ).all()

        questions = paginate(request, totalQuestions)

        if len(questions) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": [question.format() for question in questions],
            "total_questions": len(totalQuestions),
            "current_category": None
        })

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

    @app.route("/quizzes", methods=["POST"])
    def quizzes():
        body = request.get_json()

        previousQuestions = body.get("previous_questions", None)
        quizCategory = body.get("quiz_category", None)

        if (previousQuestions is None) and (quizCategory is None):
            abort(400)

        categoryId = quizCategory.get("id")

        questions = None
        if (categoryId == 0):
            questions = Question.query.filter(
                Question.id.notin_(previousQuestions)
            ).order_by(
                Question.id
            ).all()
        else:
            questions = Question.query.filter_by(
                category = categoryId
            ).filter(
                Question.id.notin_(previousQuestions)
            ).order_by(
                Question.id
            ).all()

        if len(questions) == 0:
            abort(404)

        randomQuestion = random.choice(questions)

        return jsonify({
            "success": True,
            "question": randomQuestion.format()
        })

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "bad request"}),
            400
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422
        )

    @app.errorhandler(404)
    def notFound(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404
        )

    return app

def paginate(request, records):
    RECORDS_LIMIT = 10

    page = request.args.get("page", 1, type=int)
    start = (page - 1) * RECORDS_LIMIT
    end = start + RECORDS_LIMIT

    result = records[start:end]

    return result
