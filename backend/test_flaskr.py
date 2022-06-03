import os
import random
import unittest
from flask_sqlalchemy import SQLAlchemy

from flaskr import (
    create_app,
    paginate
)

from models import (
    setup_db,
    Question,
    Category
)

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}@{}/{}".format(
            os.getenv('DATABASE_USERNAME'),
            'localhost:5432',
            self.database_name
        )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        response = self.client().get("/categories")
        data = response.get_json()

        categories = Category.query.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
        self.assertEqual(data["total_categories"], len(categories))

    def test_405_post_categories(self):
        response = self.client().post("/categories", json={"type": "Social Science"})
        data = response.get_json()

        self.assertEqual(response.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_get_questions_by_category(self):
        totalCategories = Category.query.all()
        randomCategory = random.choice(totalCategories)

        response = self.client().get(
            "/categories/{}/questions".format(randomCategory.id)
        )

        data = response.get_json()
        request = response.request

        totalQuestions = Question.query.filter_by(
            category = randomCategory.id
        ).all()

        questions = paginate(request, totalQuestions)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), len(questions))
        self.assertEqual(data["total_questions"], len(totalQuestions))

    def test_404_get_questions_by_invalid_category(self):
        response = self.client().get("/categories/0/questions")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_404_get_questions_by_categories_invalid_page_limit(self):
        totalCategories = Category.query.all()
        randomCategory = random.choice(totalCategories)

        response = self.client().get(
            "/categories/{}/questions?page=0".format(randomCategory.id)
        )

        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_questions(self):
        response = self.client().get("/questions")

        data = response.get_json()
        request = response.request

        totalQuestions = Question.query.all()
        questions = paginate(request, totalQuestions)

        totalCategories = Category.query.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), len(questions))
        self.assertEqual(len(data["categories"]), len(totalCategories))
        self.assertEqual(data["total_questions"], len(totalQuestions))

    def test_404_get_questions_invalid_page_limit(self):
        response = self.client().get("/questions?page=0")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_create_questions(self):
        question = Question(
            question="who is the 2021 motogp world champion?",
            answer="Fabio Quartararo",
            category=6,
            difficulty=3
        )

        response = self.client().post("/questions", json = question.format())
        data = response.get_json()

        createdQuestion = Question.query.get(data["created"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertNotEqual(createdQuestion, None)
        self.assertEqual(data["created"], createdQuestion.id)

    def test_400_create_question_invalid(self):
        response = self.client().post("/questions", json = {})
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    def test_get_search_questions(self):
        requestData = {"searchTerm": "title"}
        response = self.client().post("/questions/search", json=requestData)

        responseData = response.get_json()
        request = response.request

        totalQuestions = Question.query.filter(
            Question.question.ilike("%{}%".format(requestData["searchTerm"]))
        ).all()

        questions = paginate(request, totalQuestions)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(responseData["success"], True)
        self.assertEqual(len(responseData["questions"]), len(questions))
        self.assertEqual(responseData["total_questions"], len(totalQuestions))

    def test_404_search_questions_invalid_page_limit(self):
        requestData = {"searchTerm": "title"}
        response = self.client().post("/questions/search?page=0", json=requestData)
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_delete_question(self):
        totalQuestions = Question.query.all()
        randomQuestion = random.choice(totalQuestions)

        response = self.client().delete('/questions/{}'.format(randomQuestion.id))
        data = response.get_json()

        deletedQuestion = Question.query.filter(id == randomQuestion.id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], randomQuestion.id)
        self.assertEqual(deletedQuestion, None)

    def test_404_delete_question_invalid(self):
        response = self.client().delete("/questions/0")
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_quiz_question_by_all_categories(self):
        requestData = {
            "previous_questions": [],
            "quiz_category": { "id": 0 }
        }
        response = self.client().post("/quizzes", json=requestData)
        responseData = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(responseData["success"], True)
        self.assertTrue(responseData["question"])

    def test_400_get_quiz_question_by_invalid_request_data(self):
        requestData = {}
        response = self.client().post("/quizzes", json=requestData)
        responseData = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(responseData["success"], False)
        self.assertEqual(responseData["message"], "bad request")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
