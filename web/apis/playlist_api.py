from flask import jsonify, make_response
from ..models import User,Playlist
from .. import db
from .validation import NotFoundError, BusineesValidationError, BadRequest
import pytz
import datetime
from flask_restful import Resource, fields, marshal_with, reqparse
from sqlalchemy import and_

class MyDateFormat(fields.Raw):
    def format(self, value):
        return value.strftime("%d-%m-%Y %H:%M:%S")
    
playlist_fields={
    "id": fields.Integer,
    "uid":fields.Integer,
    "playlist_name": fields.String,
    "doc": MyDateFormat,
    "privacy":fields.Integer,
    "stored_songs": fields.String
}
playlist_parser = reqparse.RequestParser()
playlist_parser.add_argument('input_playlist_name')
playlist_parser.add_argument('input_privacy')

class PlaylistAPI(Resource):
    @marshal_with(playlist_fields)
    def get(self, playlist_id = None,user_id=None):
        if user_id == None and playlist_id==None :
            playlists = Playlist.query.all()
            if len(playlists)==0:
                raise NotFoundError(error_message="No playlists present")
            else:
                return playlists
        elif user_id==None and playlist_id!=None:
            playlists=Playlist.query.filter(Playlist.id==playlist_id).first()
            if playlists:
                return playlists
            else:
                raise NotFoundError(error_message="No playlists present")
        else:
            if user_id !=None and playlist_id == None:
                playlists = Playlist.query.filter(Playlist.uid == user_id).all()
                if playlists:
                    return playlists
                else:
                    raise NotFoundError(error_message="User with user id " + str(user_id) + " doesnt have any playlists")
            elif user_id !=None and playlist_id != None:
                playlists = Playlist.query.filter(and_(Playlist.uid == user_id,Playlist.id==playlist_id)).first()
                if playlists:
                    return playlists
                else:
                    raise NotFoundError(error_message="User with user id " + str(user_id) + " doesnt have playlist with playlist id " +str(playlist_id))
   


    @marshal_with(playlist_fields)
    def put(self,playlist_id,user_id):
        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise BadRequest(error_message="There is no user with id " + str(user_id))
        playlist = Playlist.query.filter(and_(Playlist.id ==playlist_id, Playlist.uid == user_id)).first()
        if not playlist:
            raise BadRequest(error_message="There is no playlist with id " + str(playlist_id) + " assocaited with user id " + str(user_id))
        
        args = playlist_parser.parse_args()
        input_playlist_name = args.get("input_playlist_name", None)
        input_privacy = args.get("input_privacy", None)

        if not input_playlist_name:
            raise BusineesValidationError(error_message="Playlist name cannot be empty")
        elif not input_privacy:
            raise BusineesValidationError(error_message="Privacy cannot be empty")
        
        if input_playlist_name == playlist.playlist_name:
            raise BusineesValidationError(error_message="You are already using "+ input_playlist_name + " playlist name. Give some other name")
        
        playlist.playlist_name = input_playlist_name
        playlist.privacy = input_privacy
        
        db.session.commit()
        return playlist
    
    @marshal_with(playlist_fields)
    def post(self,user_id):
        user = User.query.filter(User.id == user_id).first()
        if not user:
            raise BadRequest(error_message="There is no user with id " + str(user_id))
        args = playlist_parser.parse_args()
        input_playlist_name = args.get("input_playlist_name", None)
        input_privacy = args.get("input_privacy", None)

        if not input_playlist_name:
            raise BusineesValidationError(error_message="playlist name cannot be empty")
        elif not input_privacy:
            raise BusineesValidationError(error_message="Privacy is importent please specify")

        new_playlist = Playlist(playlist_name=input_playlist_name, privacy=input_privacy, uid=user_id, doc = datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
        db.session.add(new_playlist)
        db.session.commit()
        return new_playlist,201
    
    
    def delete(self, user_id=None, playlist_id=None):
        if user_id!= None and playlist_id!= None:
            user = User.query.filter(User.id == user_id).first()
            playlist = Playlist.query.filter(and_(Playlist.id == playlist_id, Playlist.uid == user_id)).first()
            if not user:
                raise BadRequest(error_message="Please enter correct user id to delete")
            elif not playlist:
                raise BadRequest(error_message="User with id " + str(user_id) + " doesn't contain playlist with id " + str(playlist_id))
            else:
                db.session.delete(playlist)
                db.session.commit()
            return make_response(jsonify({"message":"Playlist with id " + str(playlist_id) + " successfully deleted"}),200)
        else:
            raise BadRequest(error_message="Please give user id & playlist id")
        