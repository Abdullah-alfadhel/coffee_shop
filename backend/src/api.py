import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMITTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json
    {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure /Done
'''


@app.route('/drinks', methods=['GET'])
def drinks_short():
    drinks = Drink.query.all()
    print(drinks, 'this is it')

    return jsonify({
        "success": True,
        "drinks": [drink.short() for drink in drinks]
         }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json
    {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure /Done
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detailed(data):
    drinks = Drink.query.all()
    print(drinks, 'this is it')

    return jsonify({
        "success": True,
        "drinks": [drink.long() for drink in drinks]
         }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json
    {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure /Done
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(data):
    req = request.get_json()

    try:
        detailed_recipe = req['recipe']
        if isinstance(detailed_recipe, dict):
            detailed_recipe = [detailed_recipe]

        drink = Drink()
        drink.title = req['title']
        print(json.dumps(detailed_recipe), 'it should be a string')
        # convert obj to str
        drink.recipe = json.dumps(detailed_recipe)
        drink.insert()

    except Exception:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
         }), 200


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json
    {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure /Done
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(data, id):
    req = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)

    try:
        title = req.get('title')
        recipe = req.get('recipe')
        if title:
            drink.title = title

        if recipe:
            drink.recipe = json.dumps(req['recipe'])

        drink.update()
    except Exception:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
         }), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json
     {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure /Done
'''


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)

    try:
        drink.delete()
    except Exception:
        abort(400)

    return jsonify({
        'success': True,
        'delete': id
         }), 200


# Error Handling /Done
'''
Example error handling for unprocessable entity /Done
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with appropriate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404 /Done

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above /Done
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above  /Done
'''


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unauthorized'
    }), 401


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405
