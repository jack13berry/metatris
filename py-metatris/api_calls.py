import requests
import boto3
import os
import json
from pathlib import Path
import paths

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

def upload_latest_game_data(username, log_directory=None):
    if(username!=""):
        try:
            file = open(paths.app_directory() / "secret_keys.txt")
            keys = file.read().strip().split("\n")
            file.close()

            access_key = keys[0]
            secret_access_key = keys[1]
            s3_bucket = keys[2]

            s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_access_key)

            if log_directory is None:
                data_directory = paths.app_directory() / "data"
                latest_subdir = max((entry for entry in data_directory.iterdir() if entry.is_dir()),
                                    key=lambda entry: entry.stat().st_mtime)
            else:
                latest_subdir = Path(log_directory)

            for data_file in latest_subdir.iterdir():
                if data_file.is_file():
                    s3_client.upload_file(str(data_file), s3_bucket,
                                          "/".join((username, latest_subdir.name, data_file.name)))
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
