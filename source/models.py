from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


    
class User(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(70), nullable = False)
    apellido = db.Column(db.String(100), nullable = False)
    edad = db.Column(db.Integer, nullable = False)
    presentacion = db.Column(db.String(100))
    correo = db.Column(db.String(100),unique =True)
    contraseña = db.Column(db.String(200), nullable = False)
    foto = db.Column(db.String(500), nullable = True)




    # relacion
    user_insignia = db.relationship('User_Insignia', backref='user', lazy=True)
    seguidores = db.relationship("Seguidor", foreign_keys="[Seguidor.id_usuario_seguido]", back_populates="user_seguido", lazy="dynamic")
    seguidos = db.relationship("Seguidor", foreign_keys="[Seguidor.id_user_seguidor]", back_populates="user_seguidor", lazy="dynamic")

    post = db.relationship("Post",backref = "user", lazy = True)
    mensaje = db.relationship('Mensajes', backref='user', lazy=True)

    user_from = db.relationship("Chat", foreign_keys="[Chat.id_user_from]", back_populates="id_user_from_rel", lazy="dynamic")
    user_to = db.relationship("Chat", foreign_keys="[Chat.id_user_to]", back_populates="id_user_to_rel", lazy="dynamic")
    user_last_message = db.relationship("Chat", foreign_keys="[Chat.id_user_last_message]", back_populates="user_l_t", lazy="dynamic")


    def __init__(self,nombre,apellido,edad,presentacion,correo,contraseña,foto):
        self.nombre = nombre
        self.apellido = apellido
        self.edad = edad
        self.presentacion = presentacion
        self.correo = correo
        self.contraseña = contraseña
        self.foto = foto

    def serialize(self):
        return {
        "id":self.id,
        "nombre":self.nombre,
        "apellido":self.apellido ,
        "edad":self.edad ,
        "presentacion":self.presentacion ,
        "correo":self.correo ,
        "contraseña":self.contraseña,
        "foto":self.foto
        }
    
class User_Insignia(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_insignia = db.Column(db.Integer, db.ForeignKey('insignia.id'), nullable=False)
    fecha_obt = db.Column(db.String(100),nullable = False)

    def __init__(self,id_user,id_insignia,fecha_obt):
        self.id_user = id_user
        self.id_insignia = id_insignia
        self.fecha_obt = fecha_obt

    def serialize(self):
        return {
        "id":self.id,
        "id_user":self.id_user ,
        "id_insignia":self.id_insignia,
        "fecha_obt":self.fecha_obt ,
        }


class Insignia(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(70), nullable = False)
    tipo = db.Column(db.String(100), nullable = False)
    img = db.Column(db.String(500), nullable = False)

    # relacion
    user_insignia = db.relationship('User_Insignia', backref='insignia', lazy=True)

    def __init__ (self,nombre,tipo,img):
        self.nombre = nombre
        self.tipo = tipo
        self.img = img
        
    
    def serialize(self):
        return {
        "id":self.id,
        "nombre":self.nombre,
        "tipo":self.tipo ,
        "img":self.img ,
        }
    
class Estado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable = False)

    # relacion 
    seguidor = db.relationship('Seguidor', backref='estado', lazy=True)

    def __init__ (self,nombre):
        self.nombre = nombre    
        
    def serialize(self):
        return {
        "id":self.id,
        "nombre":self.nombre
        }
    


class Seguidor(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    # representa el id del usaurio quien sigue a la otra persona
    id_user_seguidor = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # reoresenta 
    id_usuario_seguido = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fecha_inicio = db.Column(db.String(100), nullable = False)
    id_estado = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)
    # relacion 
    
    
    user_seguidor = db.relationship("User", foreign_keys=[id_user_seguidor], back_populates="seguidores")
    user_seguido = db.relationship("User", foreign_keys=[id_usuario_seguido], back_populates="seguidos")



    def __init__ (self,id_user_seguidor,id_usuario_seguido,fecha_inicio,id_estado):
        self.id_usuario_seguido = id_usuario_seguido
        self.id_user_seguidor = id_user_seguidor,
        self.fecha_inicio = fecha_inicio
        self.id_estado = id_estado
        

    def serialize(self):
        return {
        "id":self.id,
        "id_usuario_seguido":self.id_usuario_seguido,
        "fecha_inicio":self.fecha_inicio,
        "id_user_seguidor":self.id_user_seguidor,
        "id_estado":self.id_estado,
        }
    


    
class Post(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    descripcion = db.Column(db.String(500), nullable = True)
    fecha = db.Column(db.String(50), nullable = False)
    
    # relacion 
    photo_post = db.relationship('Photo_post', backref='post', lazy=True)

    def __init__ (self,id_user,descripcion,fecha):
        self.id_user = id_user,
        self.descripcion = descripcion,
        self.fecha = fecha,

    def serialize(self):
        return {
        "id":self.id,
        "id_user":self.id_user,
        "descripcion":self.descripcion ,
        "fecha":self.fecha 
        }
    
class Like_Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_post = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __init__ (self,id_user,id_post):
        self.id_user = id_user,
        self.id_post = id_post,


    def serialize(self):
        return {
        "id":self.id,
        "id_user":self.id_user,
        "id_post":self.id_post ,
        }

class Comentario_Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_post = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    comentario = db.Column(db.String(1000),nullable = False)
    fecha_comentario = db.Column(db.String(1000),nullable = False)

    def __init__ (self,id_user,id_post,comentario,fecha_comentario):
        self.id_user = id_user,
        self.id_post = id_post,
        self.comentario = comentario,
        self.fecha_comentario = fecha_comentario,


    def serialize(self):
        return {
        "id":self.id,
        "id_user":self.id_user,
        "id_post":self.id_post ,
        "comentario":self.comentario,
        "fecha_comentario":self.fecha_comentario ,
        }

class Photo_post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_post = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    photo_url = db.Column(db.String(1000), nullable=False)

    def __init__ (self,id_post,photo_url):
        self.id_post = id_post,
        self.photo_url = photo_url,


    def serialize(self):
        return {
        "id":self.id,
        "id_post":self.id_post,
        "photo_url":self.photo_url ,
        }

    
class Chat(db.Model): 

    id = db.Column(db.Integer, primary_key=True)
    id_user_from = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_user_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fecha_inicio = db.Column(db.String(50), nullable=False)
    last_message = db.Column(db.String(50), nullable=True)
    id_user_last_message = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    show_last_message = db.Column(db.Boolean, nullable = True, default = False)
    date_last_message = db.Column(db.String(50), nullable=True)

    # relación 
    mensaje = db.relationship('Mensajes', backref='chat', lazy=True)

    id_user_from_rel = db.relationship("User", foreign_keys=[id_user_from], back_populates="user_from")
    id_user_to_rel = db.relationship("User", foreign_keys=[id_user_to], back_populates="user_to")
    user_l_t = db.relationship("User", foreign_keys=[id_user_last_message], back_populates="user_last_message")

    def __init__(self, id_user_from, id_user_to, fecha_inicio, last_message, date_last_message, id_user_last_message,show_last_message):
        self.id_user_from = id_user_from
        self.id_user_to = id_user_to
        self.fecha_inicio = fecha_inicio
        self.last_message = last_message
        self.id_user_last_message = id_user_last_message
        self.date_last_message = date_last_message
        self.show_last_message = show_last_message

    def serialize(self):
        return {
            "id": self.id,
            "id_user_from": self.id_user_from,
            "id_user_to": self.id_user_to,
            "fecha_inicio": self.fecha_inicio,
            "last_message": self.last_message,
            "id_user_last_message": self.id_user_last_message,
            "date_last_message": self.date_last_message,
            "show_last_message":self.show_last_message
        }
    
class Mensajes(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    id_chat = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fecha = db.Column(db.String(50), nullable=False)
    mensaje = db.Column(db.String(1000), nullable=False)

    # relación 
    def __init__(self, id_chat, id_user, fecha, mensaje):
        self.id_chat = id_chat
        self.id_user = id_user
        self.fecha = fecha
        self.mensaje = mensaje

    def serialize(self):
        return {
            "id":self.id,
            "id_chat": self.id_chat,
            "id_user": self.id_user,
            "fecha": self.fecha,
            "mensaje": self.mensaje
        }

# Cuetionario 

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50),nullable = False)

    # relación 
    def __init__(self, nombre):
        self.nombre = nombre

    def serialize(self):
        return {
            "id":self.id,
            "nombre": self.nombre
        }
    

class Entidad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50),nullable = False)
    foto = db.Column(db.String(100), nullable = False)
    id_categoria = db.Column(db.Integer, db.ForeignKey("categoria.id"),nullable = False)

    # relación 
    def __init__(self, nombre,foto,id_categoria):
        self.nombre = nombre
        self.foto = foto
        self.id_categoria = id_categoria

    def serialize(self):
        return {
            "id":self.id,
            "nombre": self.nombre,
            "foto": self.foto,
            "id_categoria": self.id_categoria

        }
    
class Cuestionario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable = False)
    descripcion = db.Column(db.String(1000), nullable = True)
    inicio = db.Column(db.String(100))
    fin = db.Column(db.String(100),)
    max_p = db.Column(db.Integer,)
    id_insignia = db.Column(db.Integer, db.ForeignKey("insignia.id"),nullable = False)
    entidad_id = db.Column(db.Integer, db.ForeignKey("entidad.id"),nullable = False)


    def __init__(self,nombre,descripcion,inicio,fin,max_p,id_insignia,entidad_id):
        self.nombre = nombre,
        self.descripcion = descripcion,
        self.inicio = inicio,
        self.fin = fin,
        self.id_insignia = id_insignia
        self.entidad_id = entidad_id
    

    def serialize(self):
        return {
            "id":self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "inicio": self.inicio,
            "fin": self.fin,
            "max_p": self.max_p,
            "id_insignia": self.id_insignia,
            "entidad_id":self.entidad_id

        }
    
class Preguntas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(200), nullable = False)
    id_cuestionario = db.Column(db.Integer,db.ForeignKey("cuestionario.id"),nullable = False)
    puntos = db.Column(db.Integer)
    foto = db.Column(db.String(500), nullable = True)

    def __init__(self,texto,id_cuestionario,puntos,foto):
        self.texto = texto,
        self.id_cuestionario = id_cuestionario,
        self.puntos = puntos,
        self.foto = foto
    

    def serialize(self):
        return {
            "id":self.id,
            "texto": self.texto,
            "id_cuestionario": self.id_cuestionario,
            "puntos": self.puntos,
            "foto" : self.foto
        }
    
class Opciones(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(200), nullable = False)
    id_pregunta = db.Column(db.Integer,db.ForeignKey("preguntas.id"),nullable = False)
    is_true = db.Column(db.Boolean, nullable = True, default = False)


    def __init__(self,texto,id_pregunta,is_true):
        self.texto = texto,
        self.id_pregunta = id_pregunta,
        self.is_true = is_true
    

    def serialize(self):
        return {
            "id":self.id,
            "texto": self.texto,
            "id_pregunta": self.id_pregunta,
            "is_true": self.is_true,
        }


class CuestionarioUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    id_cuestionario = db.Column(db.Integer, db.ForeignKey("cuestionario.id"), nullable=False)
    id_estado = db.Column(db.Integer, db.ForeignKey("estado.id"), nullable=False)
    total_points = db.Column(db.Integer,nullable = True)

    def __init__(self, id_user, id_cuestionario, id_estado,total_points):
        self.id_user = id_user
        self.id_cuestionario = id_cuestionario
        self.id_estado = id_estado
        self.total_points = total_points

    def serialize(self):
        return {
            "id": self.id,
            "id_user": self.id_user,
            "id_cuestionario": self.id_cuestionario,
            "id_estado": self.id_estado,
            "total_points":self.total_points
        }
    
class Respuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_cuestionario_user = db.Column(db.Integer, db.ForeignKey("cuestionario_user.id"), nullable=False)
    id_opcion = db.Column(db.Integer, db.ForeignKey("opciones.id"), nullable=False)

    def __init__(self, id_cuestionario_user, id_opcion):
        self.id_cuestionario_user = id_cuestionario_user
        self.id_opcion = id_opcion

    def serialize(self):
        return {
            "id": self.id,
            "id_cuestionario_user": self.id_cuestionario_user,
            "id_opcion": self.id_opcion,
        }