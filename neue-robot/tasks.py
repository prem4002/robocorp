import requests
from robocorp.tasks import task

@task
def fetch_user_from_api():
    response = requests.get("https://jsonplaceholder.typicode.com/users/1")
    print(f"status code: {response.status_code}")

    user = response.json()
    print(user)

    name    = user["name"]
    email   = user["email"]
    city    = user["address"]["city"]               # nested field
    company = user["company"]["name"]               # nested field

    print(f"Name    : {name}")
    print(f"Email   : {email}")
    print(f"City    : {city}")
    print(f"Company : {company}")

    new_post = {
        "title":  "My Robot Post",
        "body":   "Created by my first API robot!",+
        "userId": 1
    }

    response2 = requests.post(
        "https://jsonplaceholder.typicode.com/posts",
        json=new_post
    )
    print(f"POST Status: {response2.status_code}")
    created = response2.json()
    print(f"New ID from server: {created['id']}")
