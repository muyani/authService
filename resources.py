from flask_restful import Resource,reqparse



parser = reqparse.RequestParser()
parser.add_argument('username', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)

class UserRegistration(Resource):
    def post(self):
        import models
        data = parser.parse_args()
        user = models.UserModel(username=data['username'],password=data['password'])
        user.save_to_db()
        return {"Message":"User {} has been saved successfully".format(data['username'])},201

            # return {'message':'something is wrong'},500

class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        return data

class UserLogoutAccess(Resource):
    def post(self):
        return {'message': 'User logout'}

class UserLogoutRefresh(Resource):
    def post(self):
        return {'message': 'User logout'}

class TokenRefresh(Resource):
    def post(self):
        return {'message': 'Token refresh'}

class AllUsers(Resource):
    def get(self):
        return {'message': 'List of users'}

    def delete(self):
        return {'message': 'Delete all users'}

class SecretResource(Resource):
    def get(self):
        return {
            'answer': 42
        }