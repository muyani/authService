from flask import request
from flask_restful import Resource
from models import UserModel,RevokedTokenModel
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
from sentry_sdk import capture_exception,capture_message


class UserRegistration(Resource):
    def post(self):
        if request.is_json:
            try:
                fullName = request.get_json()['fullName']
                email = request.get_json()['email']
                password = request.get_json()['password']
            except Exception as e:
                capture_exception(e)
                return {"Message": "Some field is empty"}, 400
        else:
            capture_message("None JSON data sent")
            return {"Message": "Request body is null/not JSON"}, 400

        if UserModel.find_by_email(email):
            return {"Message":"Email {} already registered".format(email)},409
        try:
            user = UserModel(fullName=fullName, email=email, password=UserModel.generate_hash(password))
            user.save_to_db()
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)
            return {'message': 'User {} was created'.format(email),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                 },200
        except Exception as e:
            capture_exception(e)
            return {"Message":"Unable to create user"},500



class UserLogin(Resource):
    def post(self):
        if request.is_json:
            try:
                username = request.get_json()['username']
                password = request.get_json()['password']
            except KeyError:
                return {"Message": "Some field is empty"}, 400
        else:
            return {"Message": "Request body is null/not JSON"}, 400
        current_user = UserModel.find_by_username(username)
        if not current_user:
            return {"Message":"User {} doesnt exist".format(username)},400
        if UserModel.verify_hash(password,current_user.password):
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            return {
            'message': 'User {} Logged in Successfully'.format(username),
            'access_token': access_token,
            'refresh_token': refresh_token
                 },200
        else:
            return {'message': 'Wrong credentials'},403

class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        print(get_raw_jwt())
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'},200
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        print(current_user)
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token},200

class AllUsers(Resource):
    @jwt_required
    def get(self):
        return UserModel.return_all()
    @jwt_required
    def delete(self):
        return UserModel.delete_all()

class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'answer': 42
        }