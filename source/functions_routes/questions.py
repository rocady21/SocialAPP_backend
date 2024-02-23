from flask import Blueprint,jsonify
from models import Cuestionario,Estado,CuestionarioUser,Entidad,Insignia,Opciones,Respuesta,Categoria,Preguntas

def generate_bp_questions():
    from app import app 
    questions_bp = Blueprint("questions",__name__)

    @questions_bp.route("/mensaje",methods = ["GET"])
    def Mostrar_mensaje():
        return jsonify({"ok":True,"msg":"Correctoooooooo"})


    return questions_bp