from flask import Flask
from app.service.db_service import clean_db, init_db
from app.views.home import home 
from app.views.auth import auth
from dotenv import load_dotenv
import os

def create_app():
    #clean_db() 
    load_dotenv()
    init_db()
    app=Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', default='1111')
    app.register_blueprint(home)
    app.register_blueprint(auth)
    return app