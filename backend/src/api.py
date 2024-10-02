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
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
        if len(drinks) == 0:
            abort(404)
        formatted_drinks = [drink.short() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": formatted_drinks
        })
    except exc.SQLAlchemyError as e:
        print(e)
        abort(500)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(self):
    try:
        drinks = Drink.query.all()
        if len(drinks) == 0:
            abort(404)
        formatted_drinks = [drink.long() for drink in drinks]
        return jsonify({
            "success": True,
            "drinks": formatted_drinks
        })
    except exc.SQLAlchemyError as e:
        print(e)
        abort(500)
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def save_drink(self):
    try:
        body = request.get_json()
        title = body.get('title')
        recipe = json.dumps([body.get('recipe')])
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        formatted_drink = drink.long()
        return jsonify({
            "success": True,
            "drinks": formatted_drink
        }), 200
    except exc.SQLAlchemyError as e:
        print(e)
        abort(500)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(self, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)

    try:
        body = request.get_json()
        title = body.get('title')
        if title:
            drink.title = title
        recipe = body.get('recipe')
        if recipe:
            drink.recipe = json.dumps(recipe)
        drink.update()
        formatted_drink = drink.long()
        return jsonify({
            "success": True,
            "drinks": [formatted_drink]
        }), 200
    except exc.SQLAlchemyError as e:
        print(e)
        abort(500)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(self, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)

    try:    
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        }), 200
    except Exception:
        abort(500)

# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error.get('description')
    }), error.status_code

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405

@app.errorhandler(500)
def interal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500