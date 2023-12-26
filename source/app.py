from flask import Flask,request,jsonify
from flask_marshmallow import Marshmallow
from flask import Flask
from flask_cors import CORS
from models import db 
from flask_jwt_extended import create_access_token
from flask_migrate import Migrate

app = Flask(__name__)
CORS(app)
migrate = Migrate(app, db)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://Rodrigo:oliverman12@localhost/socialapp"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# aqui lo que hago es decirle que la base de dato inisialice con app
# porque decidi crear los modelos en models y asi no generar una import circular
# al tratar de importar db desde models y los modelos desde index
ma = Marshmallow(app)
db.init_app(app)




def init_route():
    from routes import init_routes
    init_routes(app)


init_route()


if __name__ == "__main__":
    app.run(debug=True)


