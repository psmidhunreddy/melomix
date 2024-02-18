from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path
from flask_restful import Resource, Api, fields, marshal_with, reqparse

db = SQLAlchemy()
DB_NAME = "msapp.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "gveghwijlmrkb"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    api = Api(app)
    from .diff_views import view
    from .auth import auth
    from .apis.user_api import UserAPI
    from .apis.song_api import SongAPI
    from .apis.playlist_api import PlaylistAPI
        
    app.register_blueprint(view, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    api.add_resource(UserAPI,"/api/users", "/api/user/<int:user_id>")
    api.add_resource(SongAPI,"/api/songs","/api/song/<int:song_id>","/api/creator/<int:creator_id>/songs","/api/creator/<int:creator_id>/song/<int:song_id>")
    api.add_resource(PlaylistAPI,"/api/playlists","/api/playlist/<int:playlist_id>","/api/user/<int:user_id>/playlists","/api/user/<int:user_id>/playlist/<int:playlist_id>")
    
    from .models import User,Admin
    create_database(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.home"

    @login_manager.user_loader
    def load_user(id):
        record =None
        if 'user_type' in session:
            if session["user_type"] == "user":
                record = User.query.get(int(id))
            if session["user_type"] == "admin":
                record = Admin.query.get(int(id))
            return record
    
    return app

def create_database(app):
    if not path.exists("web/" + DB_NAME):
        with app.app_context():
            db.create_all()