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
        "info":""
    }
    for i in range(0, len(users)):
        userdata = users[i].split()
        username = userdata[0]
        pw = userdata[1]
        if(not user["username"]==username):
            continue
        if(user["pw"]==pw):
            perf_data = getperfdata(username)
            result["perf_data"]=perf_data
            result["info"]="signed in"
            return result
        else:
            result["info"]="password wrong"
            return result
    result["info"] = "not signed in"
    return result

@app.route("/uploadperfdata",methods=['POST'])
def uploadperfdata():
    try:
        perf_data = request.json["perf_data"]
        username = request.json["username"]
        file=open("perf-data/"+username+".txt","w")
        for i in range(0,len(perf_data)):
            file.write(perf_data[i]+"\n")
        file.close()
        return "api - performance data saved"
    except:
        return "api - error in performance data saving"


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=80)

