from sqlite3 import Timestamp
from . import db
from flask_login import UserMixin

class Playlist(db.Model,UserMixin):
    __tablename__='playlist'
    id=db.Column(db.Integer, primary_key=True)
    playlist_name=db.Column(db.String(64))
    uid=db.Column(db.Integer, db.ForeignKey('user.id',ondelete="CASCADE"))
    doc=db.Column(db.DateTime(timezone=True))
    playlist_coverphoto=db.Column(db.Text,default="/static/decors/playlist.jpg")
    flag_rate=db.Column(db.Integer,default=0)
    privacy=db.Column(db.Integer,default=0)
    stored_songs=db.relationship('SongPlaylist',backref='playlist',cascade="all,delete")
    

class SongPlaylist(db.Model,UserMixin):
    __tablename__='songplaylist'
    id=db.Column(db.Integer, primary_key=True)
    pid=db.Column(db.Integer,db.ForeignKey('playlist.id',ondelete="CASCADE"))
    sid=db.Column(db.Integer,db.ForeignKey('song.id',ondelete="CASCADE"))

    
class User(db.Model,UserMixin):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    profile_photo = db.Column(db.Text, default="/static/profile_photos/default.jpg")
    email = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64), unique=True)
    doc=db.Column(db.DateTime(timezone=True))
    name=db.Column(db.String(64),default="")
    pno=db.Column(db.String(64))
    
    
class Admin(db.Model,UserMixin):
    __tablename__='admin'
    id=db.Column(db.Integer, primary_key=True)
    profile_photo = db.Column(db.Text, default="/static/profile_photos/default.jpg")
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64), unique=True)

class Creator(db.Model,UserMixin):
    __tablename__='creator'
    id = db.Column(db.Integer, primary_key=True)
    cname=db.Column(db.String(64), unique=True)
    profile_photo=db.Column(db.Text, default="/static/profile_photos/default.jpg")
    uid=db.Column(db.Integer, db.ForeignKey('user.id',ondelete="CASCADE"))
    doc=db.Column(db.DateTime(timezone=True))
    flag=db.Column(db.Integer,default=0)
    stored_album = db.relationship('Album', backref='creator',cascade="all,delete")
    stored_song = db.relationship('song', backref='creator',cascade="all,delete")
    
    
class song(db.Model,UserMixin):
    __tablename__='song'
    id=db.Column(db.Integer, primary_key=True)
    sname=db.Column(db.String(64), unique=True)
    slyrics=db.Column(db.String, unique=True)
    sfile=db.Column(db.String(64))
    scover_photo=db.Column(db.String(64), default="/static/song_coverphoto/default.jpg")
    cid=db.Column(db.Integer, db.ForeignKey('creator.id',ondelete="CASCADE"))
    doc=db.Column(db.DateTime(timezone=True))
    flag_rate=db.Column(db.Integer,default=0)
    stored_rating = db.relationship('rating', backref='song',cascade="all,delete")
    stored_playlists=db.relationship('SongPlaylist',backref='song',cascade="all,delete")
    stored_albums=db.relationship('SongAlbum',backref='song',cascade="all,delete")

class rating(db.Model,UserMixin):
    __tablename__='rating'
    id=db.Column(db.Integer, primary_key=True)
    rating=db.Column(db.Integer)
    sid=db.Column(db.Integer, db.ForeignKey('song.id',ondelete="CASCADE"))
    uid=db.Column(db.Integer, db.ForeignKey('user.id',ondelete="CASCADE"))

class Album(db.Model,UserMixin):
    __tablename__='album'
    id=db.Column(db.Integer, primary_key=True)
    album_name=db.Column(db.String(64))
    cid=db.Column(db.Integer, db.ForeignKey('creator.id',ondelete="CASCADE"))
    doc=db.Column(db.DateTime(timezone=True))
    album_coverphoto=db.Column(db.Text,default="/static/decors/album.jpg")
    genre=db.Column(db.Text)
    flag_rate=db.Column(db.Integer,default=0)
    stored_songs=db.relationship('SongAlbum',backref='album',cascade="all,delete")

class SongAlbum(db.Model,UserMixin):
    __tablename__='songalbum'
    id=db.Column(db.Integer, primary_key=True)
    aid=db.Column(db.Integer,db.ForeignKey('album.id',ondelete="CASCADE"))
    sid=db.Column(db.Integer,db.ForeignKey('song.id',ondelete="CASCADE"))