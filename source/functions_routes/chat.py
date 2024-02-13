from flask import Blueprint,current_app
from flask import jsonify,request
from models import db,Chat,Comentario_Post,Estado,User,Seguidor,Post,Mensajes
from flask_bcrypt import Bcrypt
from datetime import datetime
from utils.getDaysDate import getDaysDate
from utils.days_in_format import days_in_format 
from sqlalchemy import asc,desc
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_socketio import emit
from socket_routes import socket_io

def generate_bp_chat():
    from app import app
    
    chat_bp = Blueprint("chat",__name__)
    
        # Ruta para enviar un mensaje a un usuario 
    @chat_bp.route("/api/messages/send",methods= ["POST"])
    def send_message():
        id_from = request.json["id_from"]
        id_to = request.json["id_to"]


        hoy = datetime.now()
        # Buscamos el chat
        userSendMessage = User.query.filter(User.id == id_from).first()
        userSendMessageF = userSendMessage.serialize()
        chatExist = Chat.query.filter((Chat.id_user_from == id_from) & (Chat.id_user_to == id_to) | (Chat.id_user_from == id_to) & (Chat.id_user_to == id_from)).first()
        # si el chat existe, voy a enviar un mensaje normalmente y insertar el last message
        if chatExist != None:
            print("Existe jasjasjasjas")

            chatExistF = chatExist.serialize()
            chatExist.last_message = request.json["mensaje"]
            chatExist.date_last_message = hoy
            chatExist.id_user_last_message = id_from

            
            # creo un nuevo mensaje
            newMessage = Mensajes(
                id_chat = chatExistF["id"],
                id_user = id_from,
                fecha = hoy,
                mensaje = request.json["mensaje"]
            )

            db.session.add(newMessage,chatExist)
            db.session.commit()
            # mando al front el nuevo mensaje creado
            newMessageUsable = newMessage.serialize()


            channel_name_chatRealTime ="chat_" + str(chatExistF["id_user_from"]) + "_and_" + str(chatExistF["id_user_to"])
            channel_name_ContactMessageRealTime = "user_id_" + str(chatExistF["id_user_to"])
            
            # actualizo el estado de la visivilidad del ultimo mensaje a flase
            chatExist.show_last_message = False

            db.session.add(chatExist)
            db.session.commit()

            format_response_message = {
                    "id":newMessageUsable["id"],
                    "fecha":newMessageUsable["fecha"],
                    "chat":newMessageUsable["id_chat"],
                    "usuario":newMessageUsable["id_user"],
                    "mensaje":newMessageUsable["mensaje"],
                    "foto":userSendMessageF["foto"],
                    "nombre":userSendMessageF["nombre"] + " " + userSendMessageF["apellido"]
                    }
            current_time_iso = hoy.isoformat()




            separe_day = {
                "day":"hoy",
                "messages":format_response_message
            }
            info_user_from = User.query.filter_by(id=chatExistF["id_user_from"]).first().serialize()
            format_contact_response = {
                    "id":chatExistF["id"],
                    "user_from":chatExistF["id_user_from"],
                    "user_to":chatExistF["id_user_to"],
                    "nombre_user": info_user_from["nombre"] + " " + info_user_from["apellido"],
                    "id_user_chat":info_user_from["id"],
                    "photo":info_user_from["foto"],
                    "time_last_message": current_time_iso,
                    "id_user_last_message":id_from,
                    "last_message":request.json["mensaje"],
                    "show_last_message":False,
                    "firsts_messages":separe_day
            }


            socket_io.emit(channel_name_chatRealTime, {"mensaje": format_response_message})
            socket_io.emit(channel_name_ContactMessageRealTime,{"contact":format_contact_response})

            return jsonify({"ok":True,"msg":"Mensaje enviado correctamente","msg_send":format_response_message})
        # creamos un nuevo chat
        else:
            UserExist1 = User.query.filter(User.id==id_from).first()
            UserExist2 = User.query.filter(User.id==id_to).first()

            if UserExist1 == None or UserExist2 == None:
                return jsonify({"ok":False,"msg":"alguno de los usuarios no existen"})

            if "mensaje" in request.json:
                msg = request.json["mensaje"]

                new_chat = Chat(
                    id_user_from = id_from,
                    id_user_to = id_to,
                    fecha_inicio = hoy,
                    date_last_message = hoy,
                    last_message= msg,
                    id_user_last_message = id_from,
                    show_last_message = True
                )
                db.session.add(new_chat)
                db.session.commit()

                new_chatF = new_chat.serialize()

                newMessage = Mensajes(
                    id_chat = new_chatF["id"],
                    id_user = id_from,
                    fecha = hoy,
                    mensaje = msg
                )
                db.session.add(newMessage)
                db.session.commit()
                
                user_infoSend = User.query.filter_by(id=id_to).first()
                user_infoF = user_infoSend.serialize()

                
                return jsonify({"ok":True,"msg":"el chat se creo correctamente","data": {
                    "id":new_chatF["id"],
                    "user_from":new_chatF["id_user_from"],
                    "user_to":new_chatF["id_user_to"],
                    "nombre_user": user_infoF["nombre"] + " " + user_infoF["apellido"],
                    "id_user_chat":user_infoF["id"],
                    "photo":user_infoF["foto"],
                    "time_last_message": new_chatF["date_last_message"],
                    "id_user_last_message":new_chatF["id_user_last_message"],
                    "last_message":new_chatF["last_message"],
                    "show_last_message":new_chatF["show_last_message"]
                }})

            else:

                new_chat = Chat(
                    id_user_from = id_from,
                    id_user_to = id_to,
                    fecha_inicio = hoy,
                    date_last_message = None,
                    last_message= None,
                    id_user_last_message = None
                )
                db.session.add(new_chat)
                db.session.commit()

                new_chatF = new_chat.serialize()

                user_infoSend = User.query.filter_by(id=id_to).first()
                user_infoF = user_infoSend.serialize()

                
                return jsonify({"ok":True,"msg":"el chat se creo correctamente","data": {
                    "id":new_chatF["id"],
                    "user_from":new_chatF["id_user_from"],
                    "user_to":new_chatF["id_user_to"],
                    "nombre_user": user_infoF["nombre"] + " " + user_infoF["apellido"],
                    "id_user_chat":user_infoF["id"],
                    "photo":user_infoF["foto"],
                }})

    @chat_bp.route("/api/show_message/<int:id_chat>",methods=["GET"])
    def Showmessage(id_chat):

        chat = Chat.query.filter_by(id=id_chat).first()

        chat.show_last_message = True

        db.session.add(chat)
        db.session.commit()
        return jsonify({"ok":True,"msg":"chat actualizado"})

    # api para borrar un menasje
    @chat_bp.route("/api/messages/<int:id_message>",methods= ["DELETE"])
    def DeleteMesage(id_message):
        
        MessageExist = Mensajes.query.filter_by(id = id_message).first()

        if MessageExist == None:
            return jsonify({"ok":False, "msg":"No existe el mensaje"}),400



        db.session.delete(MessageExist)
        db.session.commit()

        return jsonify({"ok":True,"msg":"El mensaje se borro correctamente"}),200
    # APi para borrar un chat
    @chat_bp.route("/api/chats/<int:id_chat>",methods= ["DELETE"])
    def DeleteChat(id_chat):

        chatExist = Chat.query.filter_by(id=id_chat).first()
        if not chatExist:
            return jsonify({"ok":False,"msg":"el chat seleccionado no existe"}),404
        
        # Buscamos los mensajes
        chatExistF = chatExist.serialize()
        messages_chat = Mensajes.query.filter_by(id_chat=chatExistF["id"]).all()

        if len(messages_chat) == 0 :
            db.session.delete(chatExist)
            db.session.commit()
            return jsonify({"ok":True,"msg":"El chat se elimio correctamente"}),200
        else:
            for item in messages_chat:
                db.session.delete(item)
                db.session.commit()

            db.session.delete(chatExist)
            db.session.commit()
            return jsonify({"ok":True,"msg":"El chat se borro correctamente"}),200


    # traer todos los chats 
    @chat_bp.route("/api/chats/<int:id>",methods= ["POST"])
    def get_messages(id):
        request_body = request.json
        limit = request_body["limit"]
        index = request_body["index"]

        chats_user = Chat.query.filter((Chat.id_user_from == id) | (Chat.id_user_to == id)).order_by(desc(Chat.id)).limit(limit).offset(index).all()

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
            
            if item["last_message"] is not None: 
                return {
                    "id":item["id"],
                    "user_from":item["id_user_from"],
                    "user_to":item["id_user_to"],
                    "nombre_user": user_infoF["nombre"] + " " + user_infoF["apellido"],
                    "last_message": item["last_message"],
                    "id_user_chat":user_infoF["id"],
                    "photo":user_infoF["foto"],
                    "time_last_message": item["date_last_message"],
                    "id_user_last_message":item["id_user_last_message"],
                    "show_last_message":item["show_last_message"]
                }
            else:
                return None

        filter_chats_user = list(map(lambda item : filtrar_info(item),chats_user))
        chats_filtrados = [chat for chat in filter_chats_user if chat is not None]

        if not chats_filtrados:
            return jsonify({"ok": False, "msg": "No hay mensajes disponibles"}), 200
        # cargamos los primeros 10 mensajes del chat si son los primeros contactos que traigo 
        else:
            def filter_first_five_messages(it):
                item = it.serialize()
                date_fromat = getDaysDate(item["fecha"])
                if item["id_user"] == id:
                    is_me = True
                    user_info = User.query.filter_by(id=id).first().serialize()
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


            def addMessages(item): 
                load_firsts_messages = Mensajes.query.filter(Mensajes.id_chat == item["id"]).order_by(desc(Mensajes.id)).limit(10).offset(0).all()
                messages_filter = list(map(lambda item: filter_first_five_messages(item),load_firsts_messages))

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
                list(map(lambda item: separe_in_days(item),messages_filter))
                
                def filter_days(it):

                    past_days = days_in_format(it["day"])

                    fecha_str = it["messages"][0]["fecha"]
                    fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S.%f").date()

                    past_daysF = past_days if past_days != 0 else datetime.strftime(fecha_obj, "%Y-%m-%d")
                    
                    it["day"] = past_daysF
                    it["messages"].reverse()
                    return it

                result_f = list(map(lambda item: filter_days(item),list_days))

                result_f.reverse()

                return {
                    **item,
                    "firsts_messages":result_f
                }

            

            add_five_messages = list(map(lambda item: addMessages(item),filter_chats_user))

                
            return jsonify({"Chats": add_five_messages, "msg": "Estos son tus mensajes", "ok": True})


        

    # traer mensajes con alguien espesifico
    @chat_bp.route("/api/messages/<int:id_chat>",methods= ["POST"])
    @jwt_required()
    def get_messages_user(id_chat):
        data = request.json
        ofSett = data["ofSett"]
        numberOfMessages= data["numberOfMessages"]
        me = get_jwt_identity()

        chat = Chat.query.filter_by(id=id_chat).first()
        user_me = User.query.filter_by(correo=me).first()

        user_meF = user_me.serialize()
        if chat == None:
            return jsonify({"ok":False,"msg":"no hay mensajes"}),400
        # filtramos los mensajes del chat
        msgs = Mensajes.query.filter_by(id_chat = id_chat).order_by(desc(Mensajes.id)).limit(numberOfMessages).offset(ofSett)
        

        list_days = []

        def separe_in_days(it):
            item = it.serialize()
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

        list(map(lambda item: separe_in_days(item),msgs))

        def filter_messages(item):
            is_me = None
            date_fromat = getDaysDate(item["fecha"])
            
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
                "is_me":is_me,
                "date_fromat": date_fromat
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
                "is_me": is_me,
                "date_fromat": date_fromat
                }

        
        def filter_days(it):
            
            messages_format_f = list(map(lambda item: filter_messages(item),it["messages"]))
            messages_format_f.reverse()
            it["messages"] = messages_format_f

            past_days = days_in_format(it["day"])

            fecha_str = it["messages"][0]["fecha"]
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S.%f").date()

            past_daysF = past_days if past_days != 0 else datetime.strftime(fecha_obj, "%Y-%m-%d")
            
            it["day"] = past_daysF
            return it

        result_f = list(map(lambda item: filter_days(item),list_days))

        result_f.reverse()



        return jsonify({"ok":True,"messages":result_f,}),200
    return chat_bp