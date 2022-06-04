import sqlite3
import bcrypt
from flask import Blueprint, request
from app.data import sql_connection
user_blueprint = Blueprint('user', __name__, url_prefix='/users')

@user_blueprint.route('', methods=['post'])
def register():

    try:

        username = request.json["username"]
        password = request.json["password"]

        if not isinstance(username,str) or len(username.strip())==0:
            return {"error": "Invalid username type"},400
        
        if not username.strip().isalnum():
            return {"error":"username should be alphanumeric"},400
        
        if not isinstance(password,str) or len(password.strip())==0:
            return {"error":"Invalid password type"},400

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14))

        con = sql_connection()
        cur = con.cursor()
        cur.execute("INSERT INTO user (username, password)\
                       VALUES (?,?);",(username.strip(),hashed))
        con.commit()
        con.close()

        return {"id":cur.lastrowid},200

    except BaseException as err:
        print(f"error info: {err}") 
        if(isinstance(err,sqlite3.IntegrityError)):
            return {'error_message':"username already exists! try with a different username"},400
        
        if(isinstance(err,KeyError)):
             return {'error_message':"Invaid payload"},400

        print(type(err)) 
        return {'error_message':"unknown error"},500