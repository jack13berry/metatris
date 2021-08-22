from flask import Flask
from flask import request
import smtplib, ssl

app = Flask(__name__)

@app.route("/")
def metatris():
    return "metatris"

@app.route("/register",methods=['POST'])
def register():
    user = request.json
    new_user = user["username"]+" "+user["pw"]+" "+user["email"]+"\n"
    try:
        file = open("users.txt")
        user_data = file.read().strip().split("\n")
        file.close()
        for i in range(0,len(user_data)):
            if(user["username"] == user_data[i].split(" ")[0]):
                return "Username already exist"
    except:
        pass
    file = open("users.txt","a")
    file.write(new_user)
    file.close()
    return "registered successfully"

def getperfdata(username):
    try:
        file=open("perf-data/"+username+".txt")
        perf_data = file.read().strip().split("\n")
        return perf_data
    except:
        return []


@app.route("/signin",methods=['POST'])
def signin():
    user = request.json
    file = open("users.txt")
    users = file.read().split("\n")
    file.close()
    result={
        "perf_data":[],
        "email":"",
        "info":""
    }
    for i in range(0, len(users)):
        userdata = users[i].split()
        username = userdata[0]
        pw = userdata[1]
        email = userdata[2]
        if(not user["username"]==username):
            continue
        if(user["pw"]==pw):
            perf_data = getperfdata(username)
            result["perf_data"]=perf_data
            result["email"]=email
            result["info"]="signed in"
            return result
        else:
            result["info"]="password wrong"
            return result
    result["info"] = "not signed in"
    return result

@app.route("/uploadperfdata",methods=['POST'])
def uploadperfdata():
    return_message = "api - "
    try:
        perf_data = request.json["perf_data"]
        username = request.json["username"]
        receiver_mail = request.json["email"]
        file=open("perf-data/"+username+".txt","w")
        for i in range(0,len(perf_data)):
            file.write(perf_data[i]+"\n")
        file.close()
        return_message += "performance data saved successfully. "
    except:
        return_message += "error in performance data saving. "

    message = ""
    for i in range(0, len(perf_data)):
        message += perf_data[i] + "\n"
    message = message.replace(":", " ->")
    sender_mail = "jackie@metatris.fun"
    password = "9DNM4-CQ9TPa!"
    gmail_server = "smtp.gmail.com"
    gmail_port = 465
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(gmail_server, gmail_port, context=context) as server:
            server.login(sender_mail, password)
            server.sendmail(sender_mail, receiver_mail, message)
            return_message += ("Performance Mail sent to " + receiver_mail)
    except:
        return_message += ("Fail sending performance mail to " + receiver_mail)

    return return_message


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)

