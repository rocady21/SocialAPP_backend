from flask import Flask,request,jsonify
from flask_marshmallow import Marshmallow
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import create_access_token
from flask_migrate import Migrate
from sockets_routes import socket_io
from models import db


app = Flask(__name__)
CORS(app,origins="*")
socket_io.init_app(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://Rodrigo:oliverman12@localhost/socialapp"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'secret!'
migrate = Migrate(app, db)

# socket io recibe el app y los cors



# aqui lo que hago es decirle que la base de dato inisialice con app
# porque decidi crear los modelos en models y asi no generar una import circular
# al tratar de importar db desde models y los modelos desde index
ma = Marshmallow(app)
db.init_app(app)

def init_route():
    from routes import init_routes
    init_routes(app)



if __name__ == "__main__":
    init_route()
    # el host 0.0.0.0 hace que cualquiera pueda iniciar e contectarse al mismo
    socket_io.run(app,host="0.0.0.0",port=5000)


