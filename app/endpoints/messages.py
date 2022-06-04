import jwt
from functools import wraps
from datetime import datetime
from flask import Blueprint,  jsonify, request
from app.data import sql_connection
from app.config import SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = request.headers["Authorization"]
        if not token:
            return {"error":"please provide token"},403
        try:
            data = jwt.decode(token.split()[1],SECRET_KEY, algorithms=['HS256'])
        except BaseException as err:
            print(err)
            return {"error":"Invalid token"},403
        return f(*args,**kwargs)
    return decorated

messages_blueprint = Blueprint('messages', __name__, url_prefix='/messages')

@messages_blueprint.route('', methods=['post'])
@token_required
def create_messages():

    try:
        sender = request.json["sender"]
        recipient = request.json["recipient"]
        content = request.json["content"]

        if not isinstance(sender,int) or sender<=0:
            return {"error": "Invalid sender id. It has to be a positive interger"},400

        if not isinstance(recipient,int) or recipient<=0:
            return {"error": "Invalid recipient id. It has to be a positive interger"},400
        
        if not isinstance(content,dict):
            return {"error":"The content has to be a JSON object."},400
        
        if not isinstance(content,dict):
            return {"error":"The content has to be a JSON object."},400

        if "type" not in content.keys():
            return {"error":"The content object should have a type key."},400

        if not isinstance(content["type"],str):
            return {"error":"The content type has to be a string."},400

        if content["type"] == "text":

            if "text" not in content.keys():
                return {"error":"The content should have text field when it's type is equal to text"},400
            if not isinstance(content["text"],str):
                return {"error":"The content text should be a string."}

        elif content["type"] == "image":

            if "url"  not in content.keys() or not isinstance(content["url"],str):
                return {"error":"The content should have image url and must be of string type."},400

            if "height"  not in content.keys() or not isinstance(content["height"],int):
                return {"error":"The content should have image height and must be of int type."},400

            if content["height"]<=0:
                return {"error":"The height should be a positive integer."},400

            if "width"  not in content.keys() or not isinstance(content["width"],int):
                return {"error":"The content should have image width and must be of int type."},400

            if content["width"]<=0:
                return {"error":"The width should be a positive integer."},400

        elif content["type"] == "video":
           
           if "url"  not in content.keys() or not isinstance(content["url"],str):
                return {"error":"The content should have image url and must be of string type."},400

           if "source"  not in content.keys() or not isinstance(content["source"],str):
                return {"error":"The content should have image source and must be of string type."},400

           if content["source"] not in ["youtube","vimeo"]:
                return {"error":"The url must be either youtube or vimeo"},400
        else:
            return {"error":"The content type should be a text, image or video"},400
        
        time_now = datetime.utcnow().isoformat()
        time = time_now.split(".")[0]+"Z"

        con = sql_connection()
        cur = con.cursor()

        message_id = None

        if content["type"] == "text":

            text = content["text"]

            cur.execute("INSERT INTO message VALUES(?,?,?,?,?)",(None,recipient,sender,time,"text"))
            message_id = cur.lastrowid
            cur.execute("INSERT INTO text VALUES(?,?,?)",(None,cur.lastrowid,text))
            con.commit()

        elif content["type"] == "image":

            url = content["url"]
            height = content["height"]
            width = content["width"]

            cur.execute("INSERT INTO message VALUES(?,?,?,?,?)",(None,recipient,sender,time,"image"))
            message_id = cur.lastrowid
            cur.execute("INSERT INTO image VALUES(?,?,?,?,?)",(None,cur.lastrowid,url,height,width))
            con.commit()
            
        elif content["type"] == "video":
            url = content["url"]
            source = content["source"]

            cur.execute("INSERT INTO message VALUES(?,?,?,?,?)",(None,recipient,sender,time,"video"))
            message_id = cur.lastrowid
            cur.execute("INSERT INTO video VALUES(?,?,?,?)",(None,cur.lastrowid,url,source))
            con.commit()
            
        else:
            return  400

        response = {
            'id': message_id,
            'timestamp': time
        }

        return (jsonify(response), 200)
    except BaseException as err:
        print(f"Unexpected {err}, {type(err)}")
        response = {'error_message':"error occured"}
        return (jsonify(response), 500) 

@messages_blueprint.route('', methods=['get'])
@token_required
def get_messages():
    try:
    
        recipient = request.args.get("recipient")
        start = request.args.get("start")
        limit = request.args.get("limit") if "limit" in request.args.keys() else "100"


        if not isinstance(recipient,str) or not recipient.isnumeric() or int(recipient)<=0:
                return {"error": "Invalid recipient id. It has to be positive number"},400

        if not isinstance(start,str) or not start.isnumeric() or int(start)<=0:
                return {"error": "Invalid start. It has to be positive number"},400

        if not isinstance(limit,str) or not limit.isnumeric() or int(limit)<=0:
            return {"error": "Invalid limit. It has to be positive number"},400
    
        recipient = int(recipient)
        start = int(start)
        limit = int(limit)

        con = sql_connection()
        cur = con.cursor()

        messages = []

        cur.execute(f'SELECT message.id as id, message.timestamp as timestamp,\
                        message.sender_id as sender, message.recipient_id as recipient,\
                        message.type as type, text.data as text\
                             FROM message JOIN text on message.id=text.message_id\
                               WHERE recipient={recipient} AND message.id>={start}')

        db_response = cur.fetchall()    


        for row in db_response:
            message = {
                "id":row[0],
                "timestamp":row[1],
                "sender":row[2],
                "recipient":row[3],
                "content":{
                "type":row[4],
                "text":row[5]
                }
            }
            messages.append(message)
        

        cur.execute(f'SELECT message.id as id, message.timestamp as timestamp,\
                        message.sender_id as sender, message.recipient_id as recipient,\
                        message.type as type, image.url as url,\
                        image.height as height, image.width as width \
                             from message JOIN image on message.id=image.message_id\
                                  WHERE recipient={recipient} AND message.id>={start}')
                                  
            
        db_response = cur.fetchall() 

        for row in db_response:
            message = {
                "id":row[0],
                "timestamp":row[1],
                "sender":row[2],
                "recipient":row[3],
                "content":{
                "type":row[4],
                "url":row[5],
                "height":row[6],
                "width":row[7]
            }
        }
            messages.append(message)


        cur.execute(f'SELECT message.id as id, message.timestamp as timestamp,\
                        message.sender_id as sender, message.recipient_id as recipient,\
                        message.type as type, video.url as url,\
                        video.source as source\
                             from message JOIN video on message.id=video.message_id\
                                  WHERE recipient={recipient} AND message.id>={start}')
        db_response = cur.fetchall()   

        for row in db_response:
            message = {
                "id":row[0],
                "timestamp":row[1],
                "sender":row[2],
                "recipient":row[3],
                "content":{
                    "type":row[4],
                    "url":row[5],
                    "source":row[6]
                }
            }
            messages.append(message)

        messages = sorted(messages,key=lambda message:message['id'])

        return (jsonify({'messages': messages[:limit]}), 200)
    except BaseException as err:
        print(f"Unexpected {err}, {type(err)}")
        response = {'error_message':"error occured"}
        return (jsonify(response), 500) 

