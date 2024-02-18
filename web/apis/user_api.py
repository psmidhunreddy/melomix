from flask import jsonify, make_response
from ..models import User,Creator,Playlist
from .. import db
from .validation import NotFoundError, BusineesValidationError, BadRequest
from werkzeug.security import generate_password_hash
import pytz
import datetime
from flask_restful import Resource, fields, marshal_with, reqparse

class MyDateFormat(fields.Raw):
    def format(self, value):
        return value.strftime("%d-%m-%Y %H:%M:%S")
    
user_fields = {
    "id": fields.Integer,
    "email": fields.String,
    "username": fields.String,
    "doc": MyDateFormat,
    "name":fields.String,
    "pno": fields.String
}

user_parser = reqparse.RequestParser()
user_parser.add_argument('input_email')
user_parser.add_argument('input_username')
user_parser.add_argument('input_password')
user_parser.add_argument('input_confirm_password')
user_parser.add_argument('input_name')
user_parser.add_argument('input_pno')

class UserAPI(Resource):
    @marshal_with(user_fields)
    def get(self, user_id = None):
        if user_id ==None :
            users = User.query.all()
            if len(users)==0:
                raise NotFoundError(error_message="No user present")
            else:
                return users
                
        else:
            user = User.query.filter_by(id = user_id).first()
            if user:
                return user
            else:
                raise NotFoundError(error_message="User with user id " + str(user_id) +" is not present")
            

    @marshal_with(user_fields)
    def post(self):
        args = user_parser.parse_args()
        input_email = args.get("input_email")
        input_username = args.get("input_username")
        input_password = args.get("input_password")
        input_confirm_password = args.get("input_confirm_password")
        input_name = args.get("input_name")
        input_pno = args.get("input_pno")

        if not input_email:
            raise BusineesValidationError(error_message="Email cannot be empty")
        elif not input_username:
            raise BusineesValidationError(error_message="Username cannot be empty")
        elif not input_password:
            raise BusineesValidationError(error_message="Password cannot be empty")
        elif not input_confirm_password:
            raise BusineesValidationError(error_message="Confirm password cannot be empty")    

        email_exists = User.query.filter(User.email==input_email).first()
        username_exists = User.query.filter(User.username==input_username).first()

        if email_exists:
            raise BadRequest(error_message=input_email + " is already registered with us. Try to use different email")
        elif username_exists:
            raise BadRequest(error_message=input_username + " is already registered with us. Try to use different username")
        elif input_password != input_confirm_password:
            raise BadRequest(error_message='Passwords did not match! ')
        elif len(input_username) < 2:
            raise BadRequest(error_message='Username length should be atleast 2')
        elif len(input_password) < 6:
            raise BadRequest(error_message='Password length should be atleast 6')
        elif len(input_email) < 4:
            raise BadRequest(error_message='Email address is invalid')
        else:
            new_user = User(name = input_name, email=input_email, username=input_username, password=generate_password_hash(input_password),doc = datetime.datetime.now(pytz.timezone('Asia/Kolkata')),pno=input_pno )
            db.session.add(new_user)
            db.session.commit()
            return new_user,201
        
    @marshal_with(user_fields)
    def put(self, user_id):

        user = User.query.filter_by(id = user_id).first()
        if not user:
            raise BadRequest(error_message="Please enter correct user id to update")

        args = user_parser.parse_args()
        input_email = args.get("input_email")
        input_username = args.get("input_username")
        input_name = args.get("input_name")
        input_pno = args.get("input_pno")

        if input_email == user.email:
            raise BusineesValidationError(error_message="You are already using "+ input_email + " email. Update to another email")
        elif input_username == user.username:
            raise BusineesValidationError(error_message="You are already using "+ input_username + " username. Update to another username")
        elif input_name == user.name and user.name != "":
            raise BusineesValidationError(error_message="You are already using "+ input_name + " name. Update to another name")
        elif input_pno == user.pno and user.pno != "":
            raise BusineesValidationError(error_message="You are already using "+ input_pno + " bio. Update to another bio")
        

        email_exists = User.query.filter(User.email==input_email).first()
        username_exists = User.query.filter(User.username==input_username).first()

        if email_exists:
            raise BadRequest(error_message=input_email + " is already registered with us. Try to use different email")
        elif username_exists:
            raise BadRequest(error_message=input_username + " is already registered with us. Try to use different username")
        elif len(input_username) < 2 and input_username:
            raise BadRequest(error_message='Username length should be atleast 2')
        elif len(input_email) < 4 and input_email:
            raise BadRequest(error_message='Email address is invalid')
        else:
            if input_email:
                user.email = input_email
            if input_username:
                user.username = input_username
            if input_name:
                user.name = input_name
            if input_pno:
                user.pno = input_pno
            db.session.commit()
            return user
    
    
    def delete(self, user_id=None):
        user = User.query.filter(User.id == user_id).first()
        if not user:
            raise BadRequest(error_message="User with user id "+str(user_id)+" not present")
        else:
            cre=Creator.query.filter(Creator.uid==user_id).first()
            playlsits=Playlist.query.filter(Playlist.uid==user_id).all()
            if cre:
                db.session.delete(cre)
            if playlsits:
                for p in playlsits:
                    db.session.delete(p)
            db.session.delete(user)
            db.session.commit()
        return make_response(jsonify({"message":"User with id " + str(user_id) + " successfully deleted"}),200)
