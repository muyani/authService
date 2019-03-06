from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
import os
import sentry_sdk
sentry_sdk.init("https://fa58d7aeb71d48caa3ff6b42ae3fb59d@sentry.io/1393298")

DB_URL = 'postgresql://postgres:123@127.0.0.1:5432/authService'
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'
db = SQLAlchemy(app)

app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)

@app.before_first_request
def create_tables():
    db.create_all()

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)

api = Api(app)

import models, resources
api.add_resource(resources.UserRegistration, '/register')
api.add_resource(resources.Homepage, '/')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.AllUsers, '/users')
api.add_resource(resources.SecretResource, '/secret')


# if __name__ == "__main__":
#     app.run(debug=True,port=5000)
