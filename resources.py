from flask import request
from flask_restful import Resource
from models import UserModel,RevokedTokenModel
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
            return {'message':email},201

        except Exception as e:
            capture_exception(e)
            return {"message":"Unable to create user"},500



class UserLogin(Resource):
    def post(self):
        if request.is_json:
            try:
                email = request.get_json()['email']
                password = request.get_json()['password']
            except KeyError:
                return {"message": "Some field is empty"}, 400
        else:
            return {"message": "Request body is null/not JSON"}, 400
        current_user = UserModel.find_by_email(email)
        if not current_user:
            return {"message":"User {} doesnt exist".format(email)},400
        if UserModel.verify_hash(password,current_user.password):
            return {
            'message': email
                 },200
        else:
            return {'message': 'Wrong credentials'},403

class UserLogout(Resource):
    def post(self):
        try:
            return {'message': 'Access token has been revoked'},200
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    def post(self):
        try:
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500

class TokenRefresh(Resource):
    def post(self):
        return {'access_token'},200

class AllUsers(Resource):
    def get(self):
        return UserModel.return_all()

    # def delete(self):
    #     return UserModel.delete_all()

class SecretResource(Resource):
    def get(self):
        return {
            'answer': 42
        }

class Homepage(Resource):
    def get(self):
        return {'message':'This is a private api'},200