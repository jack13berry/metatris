from flask import Flask
from flask import request


app = Flask(__name__)

@app.route("/")
def metatris():
    return "metatris"

@app.route("/register",methods=['POST'])
def register():
    user = request.json
    new_user = user["username"]+" "+user["pw"]+" "+user["email"]+"\n"
    file = open("users.txt","a")
    file.write(new_user)
    file.close()
    return "registered successfully"

@app.route("/signin",methods=['POST'])
def signin():
    user = request.json
    file = open("users.txt")
    users = file.read().split("\n")
    file.close()
    for i in range(0, len(users)):
        userdata = users[i].split()
        username = userdata[0]
        pw = userdata[1]
        if(not user["username"]==username):
            continue
        if(user["pw"]==pw):
            return "signed in"
        else:
            return "password wrong"
    return "not signed in"


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=80)

