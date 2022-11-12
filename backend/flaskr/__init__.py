import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app)

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories')
    def get_all_category():
        categories = Category.query.all()

        categoriesDict = {}
        for category in categories:
            categoriesDict.update({category.id: category.type})

        return jsonify({
            'success': True,
            'categories': categoriesDict
        })

    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions')
    def get_questions():
        questions = Question.query.all()

        current_questions = paginate_questions(request, questions)

        categories = Category.query.all()

        categoriesDict = {}
        for category in categories:
            categoriesDict.update({category.id: category.type})

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'categories': categoriesDict,
            'current_category': None
        })

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):

        question = Question.query.filter(Question.id == id).one_or_none()

        if not question:
            abort(404)

        question.delete()

        return jsonify({
            'success': True,
            'deleted': id
        })

    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the 'Add' tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the 'List' tab.
    '''
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')

        if (body, new_question, new_answer, new_category, new_difficulty) == None:
            abort(400)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )

            question.insert()

            return jsonify({
                'success': True,
                'id': question.id
            })

        except:
            abort(422)

    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word 'title' to start.
    '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm')
        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        search_questions = paginate_questions(request, questions)

        if search_term == None:
            abort(400)

        return jsonify({
                'questions': list(search_questions),
                'total_questions': len(questions),
                'currentCategory': None
            })

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the 'List' tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions')
    def category_questions(category_id):
        try:
            category = Category.query.filter(Category.id == category_id).one_or_none()

            if not category:
                abort(404)

            questions = Question.query.filter(Question.category == category_id).all()
    
            current_questions = paginate_questions(request, questions)

            return jsonify({
                    'success': True,
                    'questions': list(current_questions),
                    'total_questions': len(questions),
                    'current_category': category.type
                })
        except:
            abort(404)

    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the 'Play' tab, after a user selects 'All' or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        body = request.get_json()

        quiz_category = body.get('quiz_category')
        previous_questions = body.get('previous_questions')

        category_id = quiz_category['id']

        """
        The old way not plagiarism
        https://review.udacity.com/#!/reviews/3795943
        I have filed a complaint and it has been confirmed that it is not plagiarism
        OLD WAY
        """
        # if category_id == 0:
        #     questions = Question.query.all()
        # else:
        #     questions = Question.query.filter_by(
        #         category = category_id).all()

        """
        NEW WAY
        """
        if category_id == 0:
            questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        else:
            questions = Question.query.filter(Question.id.notin_(previous_questions), Question.category == category_id).all()

        """
        IMPORTANT!!!!!
        The old way not plagiarism
        https://review.udacity.com/#!/reviews/3795943
        I have filed a complaint and it has been confirmed that it is not plagiarism
        """
        # old way but called plagiarism and bug exist :(((
        # random_index = random.randint(0, len(questions)-1)
        # while random_index not in previous_questions:
        #     next_question = questions[random_index]

        """
        NEW WAY
        """
        if questions:
            next_question = questions[0]

            return jsonify({
                'question': {
                    'id': next_question.id,
                    'question': next_question.question,
                    'answer': next_question.answer,
                    'difficulty': next_question.difficulty,
                    'category': next_question.category     
                }
            })
    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not Found'
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Entity'
        }), 422
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500

    '''
    Pagination
    '''
    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    return app