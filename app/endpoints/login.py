import bcrypt
import jwt
from flask import Blueprint, jsonify, request
from datetime import datetime
from datetime import timedelta
from app.data import sql_connection
from app.config import SECRET_KEY
login_blueprint = Blueprint('login', __name__, url_prefix='/login')

@login_blueprint.route('', methods=['post'])
def login():

    try:

        username = request.json["username"]
        password = request.json["password"]

        if not isinstance(username,str) or len(username.strip())==0:
            return {"error": "Invalid username type"},400
        
    
        if not isinstance(password,str) or len(password.strip())==0:
            return {"error":"Invalid password type"},400

        con = sql_connection()
        cur = con.cursor()

        cur.execute("SELECT  id,username, password FROM user where username = ?",(username,))
        user = cur.fetchone()
        
        if not user:
            return {"error":"Invalid username or password"},400


        con.commit()
        con.close()

        if bcrypt.checkpw(password.encode("utf-8"),user[2]):
            token = jwt.encode({"user_id":user[0],"exp":datetime.utcnow() + timedelta(minutes=30)},SECRET_KEY)
            return {"id":user[0],"token":token}
        else:
            return {"error":"Invalid username or password"}        
        
    except BaseException as err:

        if(isinstance(err,KeyError)):
             return {'error_message':"Invaid payload"},400

        print(f"Unexpected {err}, {type(err)}")
        response = {'error_message':"error occured"}
        return (jsonify(response), 500) 
