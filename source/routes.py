from flask import Flask,request,jsonify
from models import db,User, Seguidor,Chat,Mensajes,Post,Photo_post,Like_Post,Comentario_Post
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from sockets_routes import socket_io



# Rutas de usuario
def init_routes(app):
    # inicializamos bcrypt
    bcrypt = Bcrypt(app)

    app.config["JWT_SECRET_KEY"] = "super-secret_pal4br4SecReTaa4"  # Change this!
    jwt = JWTManager(app)

    # Login
    @app.route("/", methods=["GET"])
    def Hello():
        return jsonify({"ok":"true"})


    @app.route("/api/register", methods=["POST"])
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

    @app.route("/api/login", methods=["POST"])
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
            return jsonify({"ok":True,"data":userExistF,"token":access_token}),200
        return jsonify({"ok":False,"msg":"Error, contraseña incorrecta"}),401 

    # jwt_required te devulelve lo que queramos si el token es valido, sino devolvera 404
    @app.route('/api/validToken', methods=['GET'])
    @jwt_required()
    def ValidarToken():
        current_user = get_jwt_identity()
        user = User.query.filter(User.correo==current_user).first()
        userf = user.serialize()
        return jsonify({"isLogged": True,"user":userf,}), 200


    # Ruta para traer personas menos a mi mismo
    @app.route("/api/peoples",methods= ["GET"])
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
    @app.route("/api/people/<int:id_user>",methods= ["GET"])
    def get_people_spesifique(id_user):
        
        user = User.query.filter_by(id=id_user).first()

        if user == None:
            return jsonify({"ok":False,"msg":"no hay usuario con ese id "}),400
        
        userF = user.serialize()
        return jsonify({"ok":True, "user":userF }),200
        

    # Ruta para enviar solicitud de seguimiento    
    @app.route("/api/send_request_friend",methods= ["POST"])
    def send_request():
        data = request.json
        
        id_user_seguidor = data["id_user_seguidor"]
        id_user_seguid = data["id_user_seguido"]
        # chequeamos que no haya ningun seguimiento entre ambos 
        seguimiento_exist = Seguidor.query.filter_by(id_user_seguidor=1).first()

        if seguimiento_exist == None:
            return "Coso"
        return jsonify({
            "ok":True,
            "msg":"Solicitud enviada a " 

        }),200
            
        
    # ruta para traer solicitudes de seguimiento de un usuario
    @app.route("/api/request_friends/<int:id_user>",methods= ["GET"])
    def get_request_friends(id_user):
        user = User.query.filter_by(id=id_user)
        if user == None:
            return jsonify({"ok":False,"msg":"Error, no hay ningun usuario con ese id"}),400
        # buscamos todos los seguidores en estado pendiente
        request_friend = Seguidor.query.filter(Seguidor.id_usuario_seguido == id_user and Seguidor.id_estado == 1)
        if request_friend == None:
            return jsonify({"ok":True,"msg":"No tienes ninguan solicitud de amistad"}),200
        
        def filter_userInfo(it):
            item = it.serialize()
            userInfo = User.query.filter_by(id=item.id_user_seguidor)
            
            return {
                "id":userInfo["id"],
                "nombre":userInfo["nombre"],
                "apellido":userInfo["apellido"],
                "foto":userInfo["foto"]
            }

        request_f_F = list(map(lambda item: filter_userInfo(item),request_friend))

        return jsonify({
            "ok":True,
            "msg":"estan son tus solicitudes de seguimiento",
            "friend_request":request_f_F
            })


    # ruta para aceptar solicitud de seguimiento
    @app.route("/api/accept_request_friend",methods= ["PUT"])
    def get_accept_request_friend():
        data = request.json
        user_seguidor = data["id_user_seguidor"]
        me = data["id_user_seguido"]
        friend_request = Seguidor.query.filter(Seguidor.id_user_seguidor == user_seguidor and Seguidor.id_usuario_seguido == me).first()
        # Aceptamos la solicitud
        friend_request.id_estado = 2

        db.session.add(friend_request)
        db.session.commit()

        return jsonify({"ok":True,"msg":"Solicitud de amistad aceptada"})
        return
    # ruta para rechazar solicitud de seguimiento
    @app.route("/api/reject_request_friend",methods= ["DELETE"])
    def get_reject_request_friend():
        data = request.json
        user_seguidor = data["id_user_seguidor"]
        me = data["id_user_seguido"]
        friend_request = Seguidor.query.filter(Seguidor.id_user_seguidor == user_seguidor and Seguidor.id_usuario_seguido == me).first()
        # Aceptamos la solicitud
        db.session.delete(friend_request)
        db.session.commit()

        return jsonify({"ok":True,"msg":"Solicitud de amistad aceptada"})

       # traer todos los amigos de un usuario    
    @app.route("/api/friends/<int:id_user>",methods= ["GET"])
    def get_friends_user(id_user):
        user = User.query.filter_by(id_user=id).first()
        if user == None:
            return jsonify({"ok":False,"msg":"Error, no hay ningun usuario con ese id"}),400
        # buscamos todos los amigos de este usuario
        friends = Seguidor.query.filter(Seguidor.id_user_seguidor == id ).all()

        if len(friends) == 0:
            return jsonify({"ok":False,"msg":"No tienens ningun amigo"}),400

        def filter_amigos(it):
            item = it.serialize()
            user = User.query.filter_by(id=item["id_usuario_seguido"])
            userF = user.serialize()
            return {
                "id":userF["id"],
                "foto":userF["foto"],
                "nombre":userF["nombre"],
                "apellido":userF["apellido"]
                  
            }
        
        amigos_f = list(map(lambda item: filter_amigos(item)))
        return jsonify({"ok":True,"msg":"estos son tus amigos","amigos":amigos_f}),200
    
    # Ruta para enviar un mensaje a un usuario 
    @app.route("/api/messages/send",methods= ["POST"])
    def send_message():
        id_from = request.json["id_from"]
        id_to = request.json["id_to"]
        mensaje= request.json["mensaje"]


        hoy = datetime.now()
        # Buscamos el chat
        userSendMessage = User.query.filter(User.id == id_from).first()
        userSendMessageF = userSendMessage.serialize()
        chatExist = Chat.query.filter((Chat.id_user_from == id_from) & (Chat.id_user_to == id_to) | (Chat.id_user_from == id_to) & (Chat.id_user_to == id_from)).first()
        # si el chat existe, voy a enviar un mensaje normalmente y insertar el last message
        if chatExist != None:
            chatExistF = chatExist.serialize()
            chatExist.last_message = mensaje
            chatExist.date_last_message = hoy
            chatExist.id_user_last_message = id_from

            
            # creo un nuevo mensaje
            newMessage = Mensajes(
                id_chat = chatExistF["id"],
                id_user = id_from,
                fecha = hoy,
                mensaje = mensaje
            )

            db.session.add(newMessage,chatExist)
            db.session.commit()
            # mando al front el nuevo mensaje creado
            newMessageUsable = newMessage.serialize()
            channel_name ="chat_" + str(chatExistF["id_user_from"]) + "_and_" + str(chatExistF["id_user_to"])
            

            format_response_message = {
                    "id":newMessageUsable["id"],
                    "fecha":newMessageUsable["fecha"],
                    "chat":newMessageUsable["id_chat"],
                    "usuario":newMessageUsable["id_user"],
                    "mensaje":newMessageUsable["mensaje"],
                    "foto":userSendMessageF["foto"],
                    "nombre":userSendMessageF["nombre"] + " " + userSendMessageF["apellido"]
                    }
            
            socket_io.emit(channel_name,{"mensaje":format_response_message})
            return jsonify({"ok":True,"msg":"Mensaje enviado correctamente","msg_send":format_response_message})
        # creamos un nuevo chat
        
        UserExist1 = User.query.filter(User.id==id_from).first()
        UserExist2 = User.query.filter(User.id==id_to).first()

        if UserExist1 == None or UserExist2 == None:
            return jsonify({"ok":False,"msg":"alguno de los usuarios no existen"})


        new_chat = Chat(
            id_user_from = id_from,
            id_user_to = id_to,
            fecha_inicio = hoy,
            last_message = mensaje,
            date_last_message = hoy,
            id_user_last_message = id_from
        )
        db.session.add(new_chat)
        db.session.commit()

        # creamos el mensaje
        new_message = Mensajes(
            id_chat = new_chat.id,
            id_user = id_from,
            fecha = hoy,
            mensaje = mensaje
        )
        db.session.add(new_message)
        db.session.commit()

        return jsonify({"ok":True,"msg":"El pñrimer mensaje se envio correctamente"})
    
    
    # traer todos los chats 
    @app.route("/api/chats/<int:id>",methods= ["GET"])
    def get_messages(id):
        chats_user = Chat.query.filter((Chat.id_user_from == id) | (Chat.id_user_to == id)).all()
        if len(chats_user) == 0:
            return jsonify({"ok":False,"msg":"No tienes ningun chat"}),200
        def filtrar_info(it):
            item = it.serialize()
            # condicional para cargar la info del usuario el cual inicio o le inicie el chat
            id_user_search = None
            if(item["id_user_to"] == id):
                id_user_search = item["id_user_from"]
            else:
                id_user_search = item["id_user_to"]
            

            user_info = User.query.filter_by(id=id_user_search).first()
            if user_info == None:
                return jsonify({"ok":False,"msg":"No se encontró el usuario"}),400
            user_infoF = user_info.serialize()
        
            return {
                "id":item["id"],
                "user_from":item["id_user_from"],
                "user_to":item["id_user_to"],
                "nombre_user": user_infoF["nombre"] + " " + user_infoF["apellido"],
                "last_message": item["last_message"],
                "id_user_chat":user_infoF["id"],
                "photo":user_infoF["foto"],
                "time_last_message": item["date_last_message"],
                "id_user_last_message":item["id_user_last_message"]
            }

        filter_chats_user = list(map(lambda item : filtrar_info(item),chats_user))


        return jsonify({"ok":True,"msg":"Estos son tus menajes","Chats":filter_chats_user})

        
    
    # traer mensajes con alguien espesifico
    @app.route("/api/messages/<int:id_chat>",methods= ["GET"])
    @jwt_required()
    def get_messages_user(id_chat):

        me = get_jwt_identity()

        chat = Chat.query.filter_by(id=id_chat).first()
        user_me = User.query.filter_by(correo=me).first()

        user_meF = user_me.serialize()
        if chat == None:
            return jsonify({"ok":False,"msg":"no hay mensajes"}),400
        # filtramos los mensajes del chat
        msgs = Mensajes.query.filter_by(id_chat = id_chat).all()

        def filter_messages(it):
            item = it.serialize()
            is_me = None

            if item["id_user"] == user_meF["id"]:
                is_me = True
                
                return {
                "id":item["id"],
                "fecha":item["fecha"],
                "chat":item["id_chat"],
                "usuario":item["id_user"],
                "mensaje":item["mensaje"],
                "foto":user_meF["foto"],
                "nombre":user_meF["nombre"] + " " + user_meF["apellido"],
                "is_me":is_me
                }
            else:
                is_me= False
                info_User = User.query.filter_by(id=item["id_user"]).first()
                info_UserF = info_User.serialize()

                return {
                "id":item["id"],
                "fecha":item["fecha"],
                "chat":item["id_chat"],
                "usuario":item["id_user"],
                "mensaje":item["mensaje"],
                "foto":info_UserF["foto"],
                "nombre":info_UserF["nombre"] + " " + info_UserF["apellido"],
                "is_me": is_me
                }




        msgsF = list(map(lambda item: filter_messages(item),msgs))
        return jsonify({"ok":True,"messages":msgsF,}),200
        
# Rutas para post
    # Api para crear un nuevo post
    @app.route("/api/newPost", methods=["POST"])
    def AddNewPost(): 
        info = request.json
        now = datetime.now()
        # creamos el post
        newPost = Post(
            id_user = info["id_user"],
            descripcion = info["descripcion"],
            fecha = now
        )
        db.session.add(newPost)
        db.session.commit()
        # ahora añadimos la foto
        newPostF = newPost.serialize()
        photos = info["photo"]
        for x in photos:
            newPhoto = Photo_post(
                id_post=newPostF["id"],
                photo_url=x
            )
            db.session.add(newPhoto)
            db.session.commit()

        return jsonify({"ok":True,"msg":"post creado correctamente"}),200
    
    # borrar un post
    @app.route("/api/post/<int:id_post>", methods=["DELETE"])
    def DeletePost(id_post): 
        PostExist = Post.query.filter_by(id=id_post).first()

        if PostExist == None:
            return jsonify({"ok":False,"msg":"No se encontro ningun post con ese id"})

        # primero borramos sus fotos y luego el post
        
        photos_post = Photo_post.query.filter(Photo_post.id_post == id_post).all()

        for x in photos_post:
            db.session.delete(x)
            db.session.commit()

        db.session.delete(PostExist)
        db.session.commit()

        return jsonify({"ok":True,"msg":"post borrado correctamente"})


    # Posts espesifico
    @app.route("/api/post/<int:id_post>", methods=["GET"])
    def LoadPostSepsifique(id_post): 
        posterExist = Post.query.filter_by(id=id_post).first()
        if posterExist == None:
            return jsonify({"ok":False,"msg":"No hay ningun poster con ese id"}),400
        posterExistF = posterExist.serialize()
        # cargo sus fotos y likes
        photos_post = Photo_post.query.filter_by(id_post=posterExistF["id"]).all()

        photos_f = list(map(lambda item: item.serialize(),photos_post))
        # cargamos los likes y comentarios
        likes_post = Like_Post.query.filter_by(id_post=posterExistF["id"]).all()
        comments_post = Comentario_Post.query.filter(Comentario_Post.id_post == id_post).all()

        def filter_info_comment(it):
            item = it.serialize()
            infoUser = User.query.filter_by(id=item["id_user"]).first()
            infoF = infoUser.serialize()

            dataResponse = {
                "post_id":item["id_post"],
                "user_id":infoF["id"],
                "name":infoF["nombre"] + " " + infoF["apellido"],
                "photo":infoF["foto"],
                "id_comment":item["id"],
                "comment":item["comentario"],
                "date":item["fecha"]
            }
            return dataResponse
        
        comments_filter = list(map(lambda item: filter_info_comment(item),comments_post))
        
        if len(likes_post) != 0 :
            def filter_infoUser(it):
                item = it.serialize()
                infoUser = User.query.filter_by(id=item["id_user"]).first()
                if infoUser is None:
                    return "user no exist"
                infF = infoUser.serialize()
                return {    
                    "id_like": item["id"],
                    "id_user":infF["id"],
                    "nombre":infF["nombre"],
                    "apellido":infF["apellido"],
                    "photo":infF["foto"],
                }
            info_likes = list(map(lambda item: filter_infoUser(item),likes_post))

            return jsonify({"ok":True,"msg":"este es el post","data":{
                "infoPost":posterExistF,
                "photos":photos_f,
                "likes":len(info_likes),
                "info_likes": info_likes,
                "comments": 0 if len(comments_post) == 0 else len(comments_filter),
                "info_comments": None if len(comments_post) == 0 else comments_filter
            }})


        # comentarios
        
        
        
        return jsonify({"ok":True,"msg":"este es el post","data":{
            "infoPost":posterExistF,
            "photos":photos_f,
            "likes":0,
            "comments":0
        }})
    
    # posts de un usuario 
    @app.route("/api/post/user/<int:id_user>", methods=["GET"])
    def LoadPostsUser(id_user): 
        posterExist = Post.query.filter_by(id_user=id_user).all()
        if len(posterExist) == 0:
            return jsonify({"ok":False,"msg":"este usuario no tiene ningun post"}),200
        userPosted = User.query.filter_by(id=id_user).first()

        if userPosted == None:
            return jsonify({"ok":False,"msg":"no existe el usuario"}),400
        userPostedF = userPosted.serialize()
        user_info_response = {key: value for key, value in userPostedF.items() if key not in ['correo', 'contraseña','edad','presentacion']}
        # filtro info de cada post
        def filter_info_post(item): 
            itmeF = item.serialize()
            # cargo sus fotos y likes
            photos_post = Photo_post.query.filter_by(id_post=itmeF["id"]).all()
            photos_f = list(map(lambda item: item.serialize(),photos_post))
            
            # cargamos los likes y comentarios
            likes_post = Like_Post.query.filter_by(id_post=itmeF["id"]).all()

            comments_post = Comentario_Post.query.filter(Comentario_Post.id_post == itmeF["id"]).all()

            def filter_info_comment(it):
                item = it.serialize()
                infoUser = User.query.filter_by(id=item["id_user"]).first()
                infoF = infoUser.serialize()

                dataResponse = {
                    "post_id":item["id_post"],
                    "user_id":infoF["id"],
                    "name":infoF["nombre"] + " " + infoF["apellido"],
                    "photo":infoF["foto"],
                    "id_comment":item["id"],
                    "comment":item["comentario"],
                    "date":item["fecha"]
                }
                return dataResponse

            comments_filter = list(map(lambda item: filter_info_comment(item),comments_post))    
            def filter_infoUser(it):
                item = it.serialize()
                infoUser = User.query.filter_by(id=item["id_user"]).first()
                if infoUser == None:
                    return "user no exist"
                infF = infoUser.serialize()
                return {    
                    "id":infF["id"],
                    "nombre":infF["nombre"],
                    "apellido":infF["apellido"],
                    "photo":infF["foto"],
                }

            likes = list(map(lambda item: filter_infoUser(item),likes_post))


            return{
                "id":itmeF["id"],
                "infoPost":itmeF,
                "likes":len(likes),
                "info_likes": likes,
                "photos":photos_f,
                "user_posted_info":user_info_response,
                "comments": 0 if len(comments_post) == 0 else len(comments_filter),
                "info_comments": None if len(comments_post) == 0 else comments_filter
            }
            

        posts_filter = list(map(lambda item: filter_info_post(item),posterExist))

        
        return jsonify({"ok":True,"msg":"estos son tus posts:","posts":posts_filter}),200
    #User agrega like
    @app.route("/api/post/like", methods=["POST"])
    def UserAddLike():
        requestF = request.json
        id_user = requestF["id_user"]
        id_post = requestF["id_post"]

        Newlike = Like_Post(
            id_user=id_user,
            id_post=id_post
        )

        db.session.add(Newlike)
        db.session.commit()

        return jsonify({"ok":True,"msg":"like agregado correctamente"})
    
    #User quita like
    @app.route("/api/post/like", methods=["DELETE"])
    def UserQuitLike():
        requestF = request.json
        id_user = requestF["id_user"]
        id_post = requestF["id_post"]

        LikeExist = Like_Post.query.filter((Like_Post.id_user == id_user) & (Like_Post.id_post == id_post)).first()

        db.session.delete(LikeExist)
        db.session.commit()

        return jsonify({"ok":True,"msg":"like quitado correctamente"})
    # Añadir comentario
    @app.route("/api/post/comment", methods=["POST"])
    def UserAddComentPost():
        data = request.json()

        AddComent = Comentario_Post(
            id_user = data["id_user"],
            id_post = data["id_post"],
            comentario = data["comentario"],
            fecha_comentario = data["fecha_comentario"]
        )
        db.session.add(AddComent)
        db.session.commit()
        return jsonify({"ok":True,"msg":"comentario insertado correctamente"}),200
    # borrar comentario
    @app.route("/api/post/comment/<int:id_comment>", methods=["DELETE"])
    def UserQuitComentPost(id_comment):
        
        comentarioExist = Comentario_Post.query.filter_by(id=id_comment).first()

        if comentarioExist == None:
            return jsonify({"ok":False,"msg":"el comentario con ese id no existe"}),400
        


        db.session.delete(comentarioExist)
        db.session.commit()
        return jsonify({"ok":True,"msg":"comentario eliminado correctamente"}),200