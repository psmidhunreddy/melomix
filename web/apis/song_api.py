from flask import jsonify, make_response
from ..models import song,Creator 
from .. import db
from .validation import NotFoundError, BusineesValidationError, BadRequest
from werkzeug.security import generate_password_hash
import pytz
import datetime
from flask_restful import Resource, fields, marshal_with, reqparse
from sqlalchemy import and_

class MyDateFormat(fields.Raw):
    def format(self, value):
        return value.strftime("%d-%m-%Y %H:%M:%S")
    
song_fields={
    "id": fields.Integer,
    "cid":fields.Integer,
    "sname": fields.String,
    "slyrics": fields.String,
    "doc": MyDateFormat,
    "stored_rating": fields.String
}
song_parser = reqparse.RequestParser()
song_parser.add_argument('input_song_name')
song_parser.add_argument('input_song_lyrics')

class SongAPI(Resource):
    @marshal_with(song_fields)
    def get(self, song_id = None,creator_id=None):
        if creator_id == None and song_id == None :
            songs = song.query.all()
            if len(songs)==0:
                raise NotFoundError(error_message="No songs present")
            else:
                return songs
        elif creator_id==None and song_id!=None:
            songs=song.query.filter(song.id==song_id).first()
            if songs:
                return songs
            else:
                raise NotFoundError(error_message="Song with song id "+ str(song_id)+" not present")
        else:
            if creator_id !=None and song_id == None:
                songs = song.query.filter(song.cid == creator_id).all()
                if songs:
                    return songs
                else:
                    raise NotFoundError(error_message="Creator with creator id " + str(creator_id) + " doesnt have any songs")
            elif creator_id !=None and song_id != None:
                playlists = song.query.filter(and_(song.cid == creator_id,song.id==song_id)).first()
                if playlists:
                    return playlists
                else:
                    raise NotFoundError(error_message="Creator with creator id " + str(creator_id) + " doesnt have song with song id " +str(song_id))
   


    @marshal_with(song_fields)
    def put(self,song_id,creator_id):
        creator = Creator.query.filter_by(id = creator_id).first()
        if not creator:
            raise BadRequest(error_message="There is no creator with id " + str(creator_id))
        song1 = song.query.filter(and_(song.id ==song_id, song.cid == creator_id)).first()
        if not song1:
            raise BadRequest(error_message="There is no song with id " + str(song_id) + " assocaited with creator id " + str(creator_id))
        
        args = song_parser.parse_args()
        input_song_name = args.get("input_song_name", None)
        input_song_lyrics = args.get("input_song_lyrics", None)

        if not input_song_name:
            raise BusineesValidationError(error_message="Song name cannot be empty")
        elif not input_song_lyrics:
            raise BusineesValidationError(error_message="Song lyrics cannot be empty")
        
        if input_song_name == song.sname:
            raise BusineesValidationError(error_message="You are already using "+ input_song_name + " playlist name. Give some other name")
        
        song.sname = input_song_name
        song.slyrics = input_song_lyrics
        
        db.session.commit()
        return song1
    
    @marshal_with(song_fields)
    def post(self,creator_id):
        creator = Creator.query.filter(Creator.id == creator_id).first()
        if not creator:
            raise BadRequest(error_message="There is no creator with id " + str(creator_id))
        args = song_parser.parse_args()
        input_song_name = args.get("input_song_name", None)
        input_song_lyrics = args.get("input_song_lyrics", None)

        if not input_song_name:
            raise BusineesValidationError(error_message="Song name cannot be empty")
        elif not input_song_lyrics:
            raise BusineesValidationError(error_message="Song lyrics cannot be empty")

        new_song = song(sname=input_song_name, slyrics=input_song_lyrics, cid=creator_id, doc = datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
        db.session.add(new_song)
        db.session.commit()
        return new_song,201
    
    
    def delete(self, creator_id=None, song_id=None):
        if creator_id!= None and song_id!= None:
            creator = Creator.query.filter(Creator.id == creator_id).first()
            songs = song.query.filter(and_(song.id == song_id, song.cid == creator_id)).first()
            if not creator:
                raise BadRequest(error_message="There is no creator with id")
            elif not songs:
                raise BadRequest(error_message="Creator with id " + str(creator_id) + " doesn't contain song with id " + str(song_id))
            else:
                db.session.delete(songs)
                db.session.commit()
            return make_response(jsonify({"message":"Song with id " + str(song_id) + " successfully deleted"}),200)
        else:
            raise BadRequest(error_message="Please give user id & song id")
        