

def test_home(client):
    response = client.get("/")
    assert b'Phoner Marketing' in response.data

def test_login(client):
    response = client.get("/login")
    print(response)
    assert b'Password' in response.data

def test_login_post(client):
    response = client.post("/login")
    assert b'This field is required.' in response.data

def test_registration(client, app):
    response = client.post("/register", data={"email":"test@test.com", "password": "testerroniie"})
    with app.app_context():
        user= app.db.Users.find_one({"email": "test@test.com"})
        assert "test@test.com" in user["email"] 

def test_registrations(client, app):
    response = client.post("/login", data={"email":"mads@mads.dk", "password": "mormor16"})
    assert b"Please add graphs dis" in response

def test_notification(client):

    response = client.get("/add_notification")
    assert b'Message Content</label>' in response.data

def test_notification_post(client):

    response = client.post("/add_notification", data={"title":"mads@mads.dk", "content": "mads"})
    print("cheese")
    print(response.data)
    print("cheese")
    
    assert b'Schedule Notifications' in response.data
    
