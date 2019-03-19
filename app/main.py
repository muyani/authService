from flask import Flask
from flask_restful import Api

from flask_sqlalchemy import SQLAlchemy
import os
import sentry_sdk
sentry_sdk.init("https://fa58d7aeb71d48caa3ff6b42ae3fb59d@sentry.io/1393298")

DB_URL = 'postgresql://postgres:123@142.93.225.175:5432/authService'
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'
db = SQLAlchemy(app)


@app.before_first_request
def create_tables():
    db.create_all()

def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)

api = Api(app)

import models, resources

api.add_resource(resources.UserRegistration, '/register')
api.add_resource(resources.Homepage, '/')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogout, '/logout')
# api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
# api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.AllUsers, '/users')
api.add_resource(resources.SecretResource, '/secret')

# if __name__ == "__main__":
#     app.run(debug=True,port=5000)
