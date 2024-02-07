from flask import Blueprint
from flask import jsonify,request
from datetime import datetime
from models import db,Chat,Comentario_Post,Estado,User,Seguidor,Post,Photo_post,Like_Post

from app import app


post_bp = Blueprint("post",__name__)


# Rutas para post
    # Api para crear un nuevo post
@post_bp.route("/api/newPost", methods=["POST"])
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
@post_bp.route("/api/post/<int:id_post>", methods=["DELETE"])
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
@post_bp.route("/api/post/<int:id_post>", methods=["GET"])
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
@post_bp.route("/api/post/user/<int:id_user>", methods=["GET"])
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
                "date":item["fecha_comentario"]
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
@post_bp.route("/api/post/like", methods=["POST"])
def UserAddLike():
    requestF = request.json
    id_user = requestF["id_user"]
    id_post = requestF["id_post"]


    LikeExist = Like_Post.query.filter((Like_Post.id_user == id_user) & (Like_Post.id_post == id_post)).first()

    if LikeExist:
        return jsonify({"ok":False,"msg":"No puedes dar 2 likes"}),400


    Newlike = Like_Post(
        id_user=id_user,
        id_post=id_post
    )

    db.session.add(Newlike)
    db.session.commit()

    return jsonify({"ok":True,"msg":"like agregado correctamente"})

#User quita like
@post_bp.route("/api/post/like", methods=["DELETE"])
def UserQuitLike():
    requestF = request.json
    id_user = requestF["id_user"]
    id_post = requestF["id_post"]

    LikeExist = Like_Post.query.filter((Like_Post.id_user == id_user) & (Like_Post.id_post == id_post)).first()

    if LikeExist == None:
        return jsonify({"ok":False,"msg":"Error, el like no existe"}),400

    db.session.delete(LikeExist)
    db.session.commit()

    return jsonify({"ok":True,"msg":"like quitado correctamente"})
# Añadir comentario
@post_bp.route("/api/post/comment", methods=["POST"])
def UserAddComentPost():
    data = request.json

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
@post_bp.route("/api/post/comment/<int:id_comment>", methods=["DELETE"])
def UserQuitComentPost(id_comment):
    
    comentarioExist = Comentario_Post.query.filter_by(id=id_comment).first()

    if comentarioExist == None:
        return jsonify({"ok":False,"msg":"el comentario con ese id no existe"}),400
    


    db.session.delete(comentarioExist)
    db.session.commit()
    return jsonify({"ok":True,"msg":"comentario eliminado correctamente"}),200