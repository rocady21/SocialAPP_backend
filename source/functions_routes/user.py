from flask import Blueprint
from flask import jsonify,request
from models import db,Chat,Comentario_Post,Estado,User,Seguidor,Post,Mensajes
from utils.getDaysDate import getDaysDate
from utils.days_in_format import days_in_format 
from datetime import datetime
from sqlalchemy import asc,desc
from flask_bcrypt import Bcrypt
from app import app
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

user_bp = Blueprint('user', __name__)


bcrypt = Bcrypt(app)
@user_bp.route("/", methods=["GET"])
def Hello():
    return jsonify({"ok":"trueeweeeeeeeeeeeeeeeeeeeee"})


@user_bp.route("/api/register", methods=["POST"])
def Register():
    data = request.json

    userExist = User.query.filter_by(correo=data["correo"]).first()

    if userExist != None:
        return jsonify({"ok":False,"msg":"Error, ya hay un usuario registrado con ese correo"}),400

    if data["nombre"] != "" and data["apellido"] != "" and data["edad"] != None and data["presentacion"] != "" and data["correo"] != "" and data["contraseña"] != "":
        # Encriptacion de contraseña
        password_encripted = bcrypt.generate_password_hash(data["contraseña"]).decode('utf-8')
        newUser = User( nombre= data["nombre"],
                        apellido=data["apellido"],
                        edad=data["edad"],
                        presentacion=data["presentacion"],
                        correo=data["correo"],
                        foto = data["foto"],
                        contraseña=password_encripted)
        db.session.add(newUser)
        db.session.commit()

        return jsonify({"ok":True,"msg":"Usuario creado correctamente"}),200


    return jsonify({"ok":"true"})

@user_bp.route("/api/login", methods=["POST"])
def Login():
    data = request.json

    email = data["correo"]
    password = data["contraseña"]

    #verificamos que haya un usuario con ese correo
    userExist = User.query.filter_by(correo=email).first()

    if userExist == None:
        return jsonify({"ok":False,"msg":"Error, no hay ningun usuario con ese correo"}),400
    
    userExistF = userExist.serialize()
    # ahora que tenemos el usuario, desencriptamos la contraseña para comparar
    password_compare = bcrypt.check_password_hash(userExistF["contraseña"],password)
    if userExistF["correo"] == email and password_compare == True:
        # generar token
        access_token = create_access_token(identity=email)
        # cargar seguidores y seguidos
        seguidores_user = Seguidor.query.filter((Seguidor.id_usuario_seguido == userExistF["id"]) & (Seguidor.id_estado == 2)).all()
        seguidos_user = Seguidor.query.filter((Seguidor.id_user_seguidor == userExistF["id"]) & (Seguidor.id_estado == 2)).all()
        number_posts = Post.query.filter(Post.id_user == userExistF["id"]).all()
        request_friend = Seguidor.query.filter((Seguidor.id_usuario_seguido == userExistF["id"]) & (Seguidor.id_estado == 1)).all()

        return jsonify({"ok":True,"data":{
            "number_posts":len(number_posts),
            "seguidores":len(seguidores_user),
            "seguidos_user":len(seguidos_user),
            "exist_friend_request": False if len(request_friend) == 0 else True,
            **userExistF,

        },"token":access_token}),200
    return jsonify({"ok":False,"msg":"Error, contraseña incorrecta"}),401 

# jwt_required te devulelve lo que queramos si el token es valido, sino devolvera 404


@user_bp.route('/api/validToken', methods=['GET'])
@jwt_required()
def ValidarToken():
    current_user = get_jwt_identity()
    user = User.query.filter(User.correo==current_user).first()
    userf = user.serialize()

    seguidores_user = Seguidor.query.filter((Seguidor.id_usuario_seguido == userf["id"]) & Seguidor.id_estado == 2).all()
    seguidos_user = Seguidor.query.filter((Seguidor.id_user_seguidor == userf["id"]) & Seguidor.id_estado == 2).all()
    number_posts = Post.query.filter(Post.id_user == userf["id"]).all()
    request_friend = Seguidor.query.filter((Seguidor.id_usuario_seguido == userf["id"]) & (Seguidor.id_estado == 1)).all()

    return jsonify({"isLogged": True,"user":{
        **userf,
        "exist_friend_request": False if len(request_friend) == 0 else True,
        "seguidores":len(seguidores_user),
        "seguidos_user":len(seguidos_user),
        "number_posts":len(number_posts)
    },}), 200

@user_bp.route("/api/peoples",methods= ["GET"])
@jwt_required()
def get_people():
    current_user = get_jwt_identity()

    userAll = User.query.filter(User.correo != current_user).all()

    if len(userAll) == 0:
        return jsonify({"ok":False,"msg":"no hay usuarios "}),400
    
    def dataMap(it):

        item = it.serialize()
        return {
            "nombre" : item["nombre"],
            "apellido" : item["apellido"],
            "edad" : item["edad"],
            "presentacion" : item["presentacion"],
            "correo" : item["correo"]
        }
    result = list(map(lambda item: dataMap(item),userAll))
    return jsonify({"ok":True, "users":result }),200

# Ruta para traer persona en espesifico
@user_bp.route("/api/people/<int:id_user>",methods= ["POST"])
def get_people_spesifique(id_user):
    
    data = request.json
    id_user_session = data["id_user_session"]
    user = User.query.filter_by(id=id_user).first()
    if user == None:
        return jsonify({"ok":False,"msg":"no hay usuario con ese id "}),400
    userF = user.serialize()
    print(userF["id"])

    seguidores_user = Seguidor.query.filter((Seguidor.id_usuario_seguido == userF["id"]) & (Seguidor.id_estado == 2)).all()
    seguidos_user = Seguidor.query.filter((Seguidor.id_user_seguidor == userF["id"]) & (Seguidor.id_estado == 2)).all()
    number_posts = Post.query.filter(Post.id_user == userF["id"]).all()
    isFollower = Seguidor.query.filter((Seguidor.id_user_seguidor == id_user_session) & (Seguidor.id_usuario_seguido == id_user) | (Seguidor.id_user_seguidor == id_user) & (Seguidor.id_usuario_seguido == id_user_session)).first()
    chatExist = Chat.query.filter(((Chat.id_user_from == id_user_session) & (Chat.id_user_to == id_user)) | ((Chat.id_user_from == id_user) & (Chat.id_user_to == id_user_session))).first()


    print("seguidores",seguidores_user)
    print("seguidos",seguidos_user)

    if chatExist == None:

        if isFollower != None:
            isFollowerF = isFollower.serialize()
            status_follower = Estado.query.filter_by(id=isFollowerF["id_estado"]).first().serialize()
            print(status_follower)
            return jsonify({"ok":True, "user":{
                **userF,
                "seguidos_user":len(seguidos_user),
                "number_posts":len(number_posts),
                "seguidores_user":len(seguidores_user),
                "isFollower": status_follower["nombre"],
                "chatExist": False,
                "messages":[]
            } }),200 
        else:
            return jsonify({"ok":True, "user":{
                **userF,
                "seguidos_user":len(seguidos_user),
                "number_posts":len(number_posts),
                "seguidores_user":len(seguidores_user),
                "isFollower": False,
                "chatExist": False,
                "messages":[]
            } }),200 
    else: 
        print(chatExist)
        chatExistF = chatExist.serialize()

        user_chat = User.query.filter((User.id != id_user_session) & ((User.id == chatExistF["id_user_from"]) | (User.id == chatExistF["id_user_to"])) ).first().serialize()
        
        
        date_format = {
                "id":chatExistF["id"],
                "user_from":chatExistF["id_user_from"],
                "user_to":chatExistF["id_user_to"],
                "nombre_user": user_chat["nombre"] + " " + user_chat["apellido"],
                "id_user_chat":user_chat["id"],
                "photo":user_chat["foto"],
                "time_last_message": chatExistF["date_last_message"],
                "id_user_last_message":chatExistF["id_user_last_message"]
        }


        last_ten_messages = Mensajes.query.filter(Mensajes.id_chat==chatExistF["id"]).order_by(desc(Mensajes.id)).offset(0).limit(10).all()

        if len(last_ten_messages) != 0:
            def filter_first_five_messages(it):
                item = it.serialize()
                date_fromat = getDaysDate(item["fecha"])
                if item["id_user"] == id_user_session:
                    is_me = True
                    user_info = User.query.filter_by(id=id_user_session).first().serialize()
                    return {
                    "id":item["id"],
                    "fecha":item["fecha"],
                    "chat":item["id_chat"],
                    "usuario":item["id_user"],
                    "mensaje":item["mensaje"],
                    "foto":user_info["foto"],
                    "nombre":user_info["nombre"] + " " + user_info["apellido"],
                    "is_me":is_me,
                    "date_fromat": date_fromat
                    }
                else:
                    is_me = False
                    user_info = User.query.filter_by(id=item["id_user"]).first().serialize()
                    return {
                    "id":item["id"],
                    "fecha":item["fecha"],
                    "chat":item["id_chat"],
                    "usuario":item["id_user"],
                    "mensaje":item["mensaje"],
                    "foto":user_info["foto"],
                    "nombre":user_info["nombre"] + " " + user_info["apellido"],
                    "is_me":is_me,
                    "date_fromat": date_fromat
                    }
            result = list(map(lambda item:filter_first_five_messages(item),last_ten_messages))

            
            list_days = []

            def separe_in_days(item):
                    
                date_fromat = getDaysDate(item["fecha"])                 

                for element in list_days:
                    if element["day"] == date_fromat:
                        # Si existe, agregar el mensaje al día existente
                        element["messages"].append(item)
                        break
                else:
                    obj = {
                        "day": date_fromat,
                        "messages": [item]
                    }
                    list_days.append(obj)
            list(map(lambda item: separe_in_days(item),result))


            def filter_days(it):
                past_days = days_in_format(it["day"])

                fecha_str = it["messages"][0]["fecha"]
                fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S.%f").date()

                past_daysF = past_days if past_days != 0 else datetime.strftime(fecha_obj, "%Y-%m-%d")
                    
                it["day"] = past_daysF
                it["messages"].reverse()
                return it
            result_messages_f = list(map(lambda item: filter_days(item),list_days))

            if isFollower != None:
                isFollowerF = isFollower.serialize()
                status_follower = Estado.query.filter_by(id=isFollowerF["id_estado"]).first().serialize()

                return jsonify({"ok":True, "user":{
                    **userF,
                    "seguidos_user":len(seguidos_user),
                    "number_posts":len(number_posts),
                    "seguidores_user":len(seguidores_user),
                    "isFollower": status_follower["nombre"],
                    "chatExist": date_format,
                    "messagesExist": len(last_ten_messages),
                    "messages":result_messages_f
                } }),200 
            else:
                return jsonify({"ok":True, "user":{
                    **userF,
                    "seguidos_user":len(seguidos_user),
                    "number_posts":len(number_posts),
                    "seguidores_user":len(seguidores_user),
                    "isFollower": False,
                    "chatExist": date_format,
                    "messagesExist": len(last_ten_messages),
                    "messages":result_messages_f
                } }),200 

        else:
            if isFollower != None:
                isFollowerF = isFollower.serialize()
                status_follower = Estado.query.filter_by(id=isFollowerF["id_estado"]).first().serialize()
                print(status_follower)
                return jsonify({"ok":True, "user":{
                    **userF,
                    "seguidos_user":len(seguidos_user),
                    "number_posts":len(number_posts),
                    "seguidores_user":len(seguidores_user),
                    "isFollower": status_follower["nombre"],
                    "chatExist": date_format,
                    "messagesExist": len(last_ten_messages),
                    "messages":[]
                } }),200 
            else:
                return jsonify({"ok":True, "user":{
                    **userF,
                    "seguidos_user":len(seguidos_user),
                    "number_posts":len(number_posts),
                    "seguidores_user":len(seguidores_user),
                    "isFollower": False,
                    "chatExist": date_format,
                    "messagesExist": len(last_ten_messages),
                    "messages":[]
                } }),200 

            
    

# Ruta para enviar solicitud de seguimiento    
@user_bp.route("/api/send_request_friend",methods= ["POST"])
def send_request():
    print("jasjasdjasdjas")
    data = request.json
    
    id_user_seguidor = data["id_user_seguidor"]
    id_user_seguid = data["id_user_seguido"]
    # chequeamos que no haya ningun seguimiento entre ambos 
    seguimiento_exist = Seguidor.query.filter((Seguidor.id_user_seguidor == id_user_seguidor) & (Seguidor.id_usuario_seguido == id_user_seguid)).first()

    if seguimiento_exist == None:
        now = datetime.now()
        newRequest = Seguidor(
                    id_user_seguidor=id_user_seguidor,
                    id_usuario_seguido=id_user_seguid,
                    fecha_inicio=now,
                    id_estado = 1
                    )
        
        db.session.add(newRequest),
        db.session.commit()
        return jsonify({
            "ok":True,
            "msg":"Solicitud enviada con exito" 
        }),200
        
    return jsonify({
        "ok":True,
        "msg":"ya hay una solicitud pendiente" 

    }),200
        
    
# ruta para filtrar user por nombre

@user_bp.route("/api/user/<string:nombre_user>",methods = ["GET"])
def Filter_user_By_name(nombre_user):

    user_filter = User.query.filter(User.nombre.contains(nombre_user)).all()
    if len(user_filter) == 0: 
        return jsonify({"ok":False,"msg":"No hay usuario con ese nombre"}),400
    
    def filter_info_user(it):
        item = it.serialize()
        seguidores_user = Seguidor.query.filter((Seguidor.id_usuario_seguido == item["id"]) & (Seguidor.id_estado == 2)).all()
    

        return {
            "id":item["id"],
            "nombre" : item["nombre"],
            "apellido" : item["apellido"],
            "edad" : item["edad"],
            "correo" : item["correo"],
            "photo": item["foto"],
            "seguidores":len(seguidores_user)
        }
    user_map = list(map(lambda item: filter_info_user(item),user_filter))
    return jsonify({"ok":True,"result":user_map}),200

# ruta para traer solicitudes de seguimiento de un usuario
@user_bp.route("/api/request_friends/<int:id_user>",methods= ["GET"])
def get_request_friends(id_user):
    user = User.query.filter_by(id=id_user).first()
    if user == None:
        return jsonify({"ok":False,"msg":"Error, no hay ningun usuario con ese id"}),400
    # buscamos todos los seguidores en estado pendiente
    request_friend = Seguidor.query.filter((Seguidor.id_usuario_seguido == id_user) & (Seguidor.id_estado == 1)).all()
    if len(request_friend) == 0 :
        return jsonify({"ok":False,"msg":"No tienes ninguan solicitud de amistad"}),400
    
    def filter_userInfo(it):
        item = it.serialize()
        userInfo = User.query.filter_by(id=item["id_user_seguidor"]).first()
        userInfoF = userInfo.serialize()
        return {
            "id":userInfoF["id"],
            "nombre":userInfoF["nombre"],
            "apellido":userInfoF["apellido"],
            "foto":userInfoF["foto"]
        }

    request_f_F = list(map(lambda item: filter_userInfo(item),request_friend))

    return jsonify({
        "ok":True,
        "msg":"estan son tus solicitudes de seguimiento",
        "friend_request":request_f_F
        })

# ruta para aceptar solicitud de seguimiento
@user_bp.route("/api/accept_request_friend",methods= ["PUT"])
def get_accept_request_friend():
    
    data = request.json
    user_seguidor = data["id_user_seguidor"]
    me = data["id_user_seguido"]
    friend_request = Seguidor.query.filter((Seguidor.id_user_seguidor == user_seguidor) & (Seguidor.id_usuario_seguido == me)).first()
    # Aceptamos la solicitud
    if friend_request == None:
        return jsonify({"ok":False,"msg":"no existe solicitud de seguimiento"}),400
    friend_request.id_estado = 2

    db.session.add(friend_request)
    db.session.commit()

    print("se accepto la solicitud de amistad")

    return jsonify({"ok":True,"msg":"Solicitud de amistad aceptada"})
# ruta para rechazar solicitud de seguimiento
@user_bp.route("/api/reject_request_friend",methods= ["DELETE"])
def get_reject_request_friend():

    user_seguidor = request.args.get('param1')
    me = request.args.get('param2')

    friend_request = Seguidor.query.filter((Seguidor.id_user_seguidor == user_seguidor) & (Seguidor.id_usuario_seguido == me)).first()
    # Aceptamos la solicitud
    db.session.delete(friend_request)
    db.session.commit()

    return jsonify({"ok":True,"msg":"Solicitud de amistad rechazada"})


@user_bp.route("/api/following/<int:id_user>",methods= ["GET"])
def get_following_user(id_user):
    user = User.query.filter_by(id=id_user).first()
    if user == None:
        return jsonify({"ok":False,"msg":"Error, no hay ningun usuario con ese id"}),400
    # buscamos todos los amigos de este usuario
    friends = Seguidor.query.filter_by(id_user_seguidor=id_user).all()

    if len(friends) == 0:
        return jsonify({"ok":False,"msg":"No tienens ningun amigo"}),400

    def filter_amigos(it):
        item = it.serialize()
        user = User.query.filter_by(id=item["id_usuario_seguido"]).first()
        userF = user.serialize()
        return {
            "id":userF["id"],
            "foto":userF["foto"],
            "nombre":userF["nombre"],
            "apellido":userF["apellido"]
                
        }
    
    amigos_f = list(map(lambda item: filter_amigos(item),friends))
    return jsonify({"ok":True,"msg":"estos son tus amigos","amigos":amigos_f}),200
# api para traer personas que me siguen 
@user_bp.route("/api/follower/<int:id_user>",methods= ["GET"])
def get_follower_user(id_user):
    user = User.query.filter_by(id=id_user).first()
    if user == None:
        return jsonify({"ok":False,"msg":"Error, no hay ningun usuario con ese id"}),400
    # buscamos todos los amigos de este usuario
    friends = Seguidor.query.filter_by(id_usuario_seguido=id_user).all()

    if len(friends) == 0:
        return jsonify({"ok":False,"msg":"No tienens ningun amigo"}),400

    def filter_amigos(it):
        item = it.serialize()
        user = User.query.filter_by(id=item["id_user_seguidor"]).first()
        userF = user.serialize()
        return {
            "id":userF["id"],
            "foto":userF["foto"],
            "nombre":userF["nombre"],
            "apellido":userF["apellido"]
                
        }
    
    amigos_f = list(map(lambda item: filter_amigos(item),friends))
    return jsonify({"ok":True,"msg":"estos son tus amigos","amigos":amigos_f}),200