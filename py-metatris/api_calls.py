import requests
import boto3
import os
import json

# base_url = "http://192.168.1.3:5000"
base_url = "http://18.116.114.15:5000"

def call_signin(world, username,pw):
    data = {
        "username": username,
        "pw": pw
    }
    try:
        response = requests.post(base_url+'/signin', json=data)
        response_info = json.loads(response.text)["info"]
        response_perfdata = json.loads(response.text)["perf_data"]
        response_email = json.loads(response.text)["email"]
        if(response_info=="signed in"):
            world.setusername(username)
            world.setemail(response_email)
            world.setperf(response_perfdata)
        return(response_info)
    except:
        return("not signin")

def call_register(email,username,pw):
    data = {
        "email": email,
        "username":username,
        "pw":pw
    }
    try:
        response = requests.post(base_url+'/register', json=data)
        print(response.text)
        return(response.text)
    except:
        return("not registered")

def upload_latest_game_data(username):
    if(username!=""):
        try:
            file = open("secret_keys.txt")
            keys = file.read().strip().split("\n")
            file.close()

            access_key = keys[0]
            secret_access_key = keys[1]
            s3_bucket = keys[2]

            s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_access_key)

            data_directory = ".\data\\"

            content = os.listdir(data_directory)
            new_content = []
            for i in range(0, len(content)):
                new_content.append(data_directory + content[i])
            latest_subdir = max(new_content, key=os.path.getmtime)

            folder = latest_subdir.split('\\')[2]
            data_files = [f for f in os.listdir(latest_subdir)]
            for i in range(0, len(data_files)):
                s3_client.upload_file(os.path.join(latest_subdir, data_files[i]), s3_bucket,
                                      os.path.join(username + "/" + folder + "/" + data_files[i]))
            print("game data successfully uploaded")
        except:
            print("game data not uploaded")

def upload_perf_data(perf_data, username, email):
    if(username!=""):
        data = {
            "perf_data": perf_data,
            "username":username,
            "email":email
        }
        try:
            response = requests.post(base_url+'/uploadperfdata', json=data)
            print(response.text)
            return(response.text)
        except:
            return("not uploaded performance data")
