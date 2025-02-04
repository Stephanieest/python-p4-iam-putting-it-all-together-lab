from flask import request, session
from flask_restful import Resource, Api
from models import User, Recipe, db
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
api = Api(app)
bcrypt = Bcrypt(app)

class Signup(Resource):
    def post(self):
        data = request.get_json()
        new_user = User(username=data['username'])
        new_user.password = data['password']
        new_user.image_url = data.get('image_url')
        new_user.bio = data.get('bio')

        try:
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return {
                'id': new_user.id,
                'username': new_user.username,
                'image_url': new_user.image_url,
                'bio': new_user.bio
            }, 201
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Username already exists'}, 422

class CheckSession(Resource):
    def get(self):
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 200
        return {'error': 'Unauthorized'}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and bcrypt.check_password_hash(user._password_hash, data['password']):
            session['user_id'] = user.id
            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 200
        return {'error': 'Unauthorized'}, 401

class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return '', 204

class RecipeIndex(Resource):
    def get(self):
        if 'user_id' not in session:
            return {'error': 'Unauthorized'}, 401
        recipes = Recipe.query.all()
        return [{'id': recipe.id, 'title': recipe.title, 'instructions': recipe.instructions, 'minutes_to_complete': recipe.minutes_to_complete} for recipe in recipes], 200

    def post(self):
        if 'user_id' not in session:
            return {'error': 'Unauthorized'}, 401
        data = request.get_json()
        new_recipe = Recipe(
            title=data['title'],
            instructions=data['instructions'],
            minutes_to_complete=data['minutes_to_complete'],
            user_id=session['user_id']
        )
        db.session.add(new_recipe)
        db.session.commit()
        return {
            'id': new_recipe.id,
            'title': new_recipe.title,
            'instructions': new_recipe.instructions,
            'minutes_to_complete': new_recipe.minutes_to_complete
        }, 201

api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(RecipeIndex, '/recipes')
