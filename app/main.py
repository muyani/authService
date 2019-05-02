from flask import Flask,request,make_response,jsonify
from flask_restplus import Api,Resource,reqparse,fields
from flask_sqlalchemy import SQLAlchemy
import os
import sentry_sdk
sentry_sdk.init("https://fa58d7aeb71d48caa3ff6b42ae3fb59d@sentry.io/1393298")
from sentry_sdk import capture_exception,capture_message


DB_URL = 'postgresql://postgres:123@127.0.0.1:5432/authService'
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'
db = SQLAlchemy(app)
import models


api = Api(app)

registerParser = reqparse.RequestParser()
registerParser.add_argument('fullName', type=str, help='user fullname',required= True)
registerParser.add_argument('email', type=str, help='Email of the user',required= True)
registerParser.add_argument('password', type=str, help='Password of the user',required= True)


loginParser = reqparse.RequestParser()
loginParser.add_argument('email', type=str, help='Email of the user',required= True)
loginParser.add_argument('password', type=str, help='Password of the user',required= True)


userStructure = api.model('user',{
    'id':fields.String,
    'fullName':fields.String,
    'email':fields.String
})


@app.before_first_request
def create_tables():
    db.create_all()


@app.errorhandler(400)
def badRequest(e):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

@app.errorhandler(404)
def notFound(e):
    return make_response(jsonify({'error': 'Resource not found'}), 404)

@app.errorhandler(405)
def notAllowed(error):
    return make_response(jsonify({'error': 'Method not allowed'}), 405)

@app.errorhandler(500)
def internalServer(e):
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)


ns = api.namespace('api/v1',description='Bizweb User Service.')


@ns.route('/')
class Homepage(Resource):
    def get(self):
        return {'message':'This is a private api'},200
    def post(self):
        return {'message':'This is a private api'},200

@ns.route('/register')
class UserRegistration(Resource):
    @ns.expect(registerParser)
    @ns.marshal_with(userStructure)
    def post(self):
        body = registerParser.parse_args()
        print(body)
        fullName = body['fullName']
        email = body['email']
        password = body['password']
        if models.UserModel.find_by_email(email):
            return {},409
        try:
            user = models.UserModel(fullName=fullName, email=email, password=models.UserModel.generate_hash(password))
            record = user.save_to_db()
            return record,201

        except Exception as e:
            capture_exception(e)
            return {},500

@ns.route('/login')
@ns.response(400, 'User not found')
class UserLogin(Resource):
    @ns.expect(loginParser)
    @ns.marshal_with(userStructure)
    def post(self):
        body = loginParser.parse_args()
        email = body['email']
        password = body['password']
        current_user = models.UserModel.find_by_email(email)
        if not current_user:
            return {'message':'user not found'},404
        if models.UserModel.verify_hash(password,current_user.password):
            return current_user,200
        else:
            return {'message': 'Wrong credentials'},403

