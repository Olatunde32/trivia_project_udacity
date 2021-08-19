import os
from flask import Flask, __init__, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

# paginating questions
    def paginate_questions(request, questions):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in questions]
        current_questions = questions[start:end]

        return current_questions

     # Use the after_request decorator to set Access-Control-Allow
    CORS(app, resources={'/': {'origins': '*'}})
    @app.after_request
    def after_request(response):

       response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
       response.headers.add('Access-Control-Allow-Methods','GET,PATCH,POST,DELETE,OPTIONS')

       return response

 # Endpoint to handle GET requests for all available categories.


    @app.route('/categories')
    # get all categories
    def get_categories():
        categories = Category.query.order_by(Category.type).all()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories}
        })

  # Endpoint to handle GET requests for questions, including pagination (every 10 questions).
  # Endpoint should return a list of questions, number of total questions, current category, categories.
    @app.route('/questions')
    def get_questions():

        # get all questions and paginate
        question_selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, question_selection)

        # get all categories
        categories = Category.query.order_by(Category.type).all()

        # abort 404 if no questions
        if (len(current_questions) == 0):
            abort(404)

        # return data to view
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(question_selection),
            'categories': {category.id: category.type for category in categories},
            'current_category': None
        })

    #endpoint to delete question using a question ID.
    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:

            abort(422)
   #endpoint to POST a new question,which will require the question and answer text,category, and difficulty score.
    @app.route("/questions", methods=['POST'])
    def add_question():
        body = request.get_json()
        if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):

            abort(422)

        add_new_question = body.get('question')
        add_new_answer = body.get('answer')
        add_new_difficulty = body.get('difficulty')
        add_new_category = body.get('category')

        try:
            question = Question(question=add_new_question, answer=_add_new_answer,
                                difficulty=add_new_difficulty, category=add_new_category)
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id,
            })

        except:
            abort(422)

      # endpoint to get questions based on a search term.
      # It should return any questions for whom the search term
      # is a substring of the question.
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        if search_term:
            search_results = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in search_results],
                'total_questions': len(search_results),
                'current_category': None
            })
        abort(404)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):

        try:
            questions = Question.query.filter(
                Question.category == str(category_id)).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            })
        except:

            abort(404)

    #endpoint to get questions based on category.
    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):

        category = Category.query.filter_by(id=id).one_or_none()

        if (category is None):
            abort(400)

        question_selection = Question.query.filter_by(category=category.id).all()
        paginated = paginate_questions(request, question_selection)


        return jsonify({
            'success': True,
            'questions': paginated,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })


    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400


    return app

