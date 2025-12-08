import requests

# Your Firebase Web API Key
api_key = settings.FIREBASE_API_KEY 
url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

payload = {
    "email": "khalfanathman12@yahoo.com",
    "password": "Khalif01@2023",
    "returnSecureToken": True
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    print(response.json().get("idToken"))
else:
    print("Error:", response.text)