from flask_jwt_extended import JWTManager
from datetime import timedelta
from functions_routes.user import user_bp
from functions_routes.chat import chat_bp
from functions_routes.posts import post_bp
from flask import request,jsonify
from app import socket_io
from datetime import datetime
from flask_socketio import emit
from models import User,Mensajes,Chat,db
# Rutas de usuario
def conifure_routes(app):
    jwt = JWTManager(app)
    app.config["JWT_SECRET_KEY"] = "super-secret_pal4br4SecReTaa4" 
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(minutes=1)

    app.register_blueprint(user_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(post_bp)






        


        
