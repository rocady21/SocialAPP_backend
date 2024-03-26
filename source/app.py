from flask import Flask,request,jsonify
from flask_marshmallow import Marshmallow
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import create_access_token
from flask_migrate import Migrate
from models import db
from flask_socketio import SocketIO,emit
from functions_routes.user import generate_bp
from functions_routes.chat import generate_bp_chat
from functions_routes.questions import generate_bp_questions
from functions_routes.posts import generate_bp_post
from socket_routes import socket_io
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from datetime import timedelta


app = Flask(__name__)
CORS(app, origins="*")
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://Rodrigo:oliverman12@localhost/socialapp"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'secret!'


# Inicializar la base de datos y migraciones
db.init_app(app)
migrate = Migrate(app, db)
# Inicializo las rutas y blueprint
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "super-secret_pal4br4SecReTaa4" 
app.config['JWT_EXPIRATION_DELTA'] = timedelta(minutes=1)
# Inicializar 
user_bp = generate_bp()
chat_bp = generate_bp_chat()
post_bp = generate_bp_post()
questions_bp = generate_bp_questions()

app.register_blueprint(user_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(post_bp)
app.register_blueprint(questions_bp)


socket_io.init_app(app)

if __name__ == "__main__":
    socket_io.run(app,debug=True,host="0.0.0.0", port=4000)




