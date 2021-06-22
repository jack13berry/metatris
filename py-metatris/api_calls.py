import requests

base_url = "http://192.168.1.4"

def call_signin(username,pw):
    data = {
        "username": username,
        "pw": pw
    }
    try:
        response = requests.post(base_url+'/signin', json=data)
        print(response.text)
        return(response.text)
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