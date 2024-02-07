from flask import Flask,request,jsonify
from models import db,User, Seguidor,Chat,Mensajes,Post,Photo_post,Like_Post,Comentario_Post,Estado
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from sockets_routes import socket_io
from datetime import timedelta
from utils.getDaysDate import getDaysDate
from utils.days_in_format import days_in_format
from functions_routes.user import user_bp
from functions_routes.chat import chat_bp
from functions_routes.posts import post_bp

# Rutas de usuario
def init_routes(app):
    # inicializamos bcrypt

    app.config["JWT_SECRET_KEY"] = "super-secret_pal4br4SecReTaa4" 
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(minutes=1)
    jwt = JWTManager(app)

    app.register_blueprint(user_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(post_bp)

    # Login


        
