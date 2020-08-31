# Facial-Recognition-SAAS-Django

## This API is deployed on http://areebaseher04.pythonanywhere.com/

## ENDPOINTS

### Create Account
```
import requests

url = "http://areebaseher04.pythonanywhere.com/rest-auth/registration/"

payload = {
            'username': 'AreebaSeher',
            'email': 'areebaseher@gmail.com',
            'password1': 'AreebaSeher123456789',
            'password2': 'AreebaSeher123456789'
            }
files = [
]
headers = {
}

response = requests.request("POST", url, headers=headers, data = payload, files = files)

print(response.text.encode('utf8'))
```

### Login
```
import requests

url = "http://areebaseher04.pythonanywhere.com/rest-auth/login/"

payload = {
           'username': 'AreebaSeher',
           'password': 'AreebaSeher123456789'
           }
files = [
]
headers = {
}

response = requests.request("POST", url, headers=headers, data = payload, files = files)

print(response.text.encode('utf8')) #It will give you Authorization Token
```

### Demo ( 3 requests/day)
```
import requests

url = "http://areebaseher04.pythonanywhere.com/api/demo/"

payload = {}
files = [
  ('file', open('E:/Images/bday_2/WhatsApp Image 2020-07-13 at 11.23.34 PM (1).jpeg','rb')) #Your path to image
]
headers = {
}

response = requests.request("POST", url, headers=headers, data = payload, files = files)

print(response.text.encode('utf8'))
```

### Upload image after logged in |Free trial users can use this endpoint for 14 days only | Members can use it until the end of subscription date | For member, this endpoint will charge 0.05$ for a group of 2 api calls
```
import requests

url = "http://areebaseher04.pythonanywhere.com/api/upload/"

payload = {}
files = [
  ('file', open('/E:/Images/bday_2/WhatsApp Image 2020-07-13 at 11.23.34 PM (1).jpeg','rb'))
]
headers = {
  'Authorization': 'Token ff79dfc866e6e89a4ab31257c94b928ed9965b61' #Your Authorization Token
}

response = requests.request("POST", url, headers=headers, data = payload, files = files)

print(response.text.encode('utf8'))
```

### Get User API key (Users can see their API key)
```
import requests

url = "http://areebaseher04.pythonanywhere.com/api/api-key/"

payload = {}
headers = {
  'Authorization': 'Token ff79dfc866e6e89a4ab31257c94b928ed9965b61'
}

response = requests.request("GET", url, headers=headers, data = payload)

print(response.text.encode('utf8'))
```

### Get Current Email (Users can see their current Email)
```
import requests

url = "http://areebaseher04.pythonanywhere.com/api/email/"

payload = {}
headers = {
  'Authorization': 'Token ff79dfc866e6e89a4ab31257c94b928ed9965b61'
}

response = requests.request("GET", url, headers=headers, data = payload)

print(response.text.encode('utf8'))
```

### Change Email
```
import requests

url = "http://areebaseher04.pythonanywhere.com/api/change-email/"

payload = {
    'email': 'areebaseher1998@gmail.com',  #new email
    'confirm_email': 'areebaseher1998@gmail.com'
    }
files = [

]
headers = {
  'Authorization': 'Token ff79dfc866e6e89a4ab31257c94b928ed9965b61'
}

response = requests.request("POST", url, headers=headers, data = payload, files = files)

print(response.text.encode('utf8'))
```

### Change Password
```
import requests

url = "http://areebaseher04.pythonanywhere.com/api/change-password/"

payload = {
    'password': 'AreebaSeher1998',  #new password
    'confirm_password': 'AreebaSeher1990',
    'current_password': 'AreebaSeher123456789'
    }
files = [
]
headers = {
  'Authorization': 'Token ff79dfc866e6e89a4ab31257c94b928ed9965b61'
}

response = requests.request("POST", url, headers=headers, data = payload, files = files)

print(response.text.encode('utf8'))
```

### User Detail about Billing (membership type, subscription end date, free trial end date and amount due)
```
import requests

url = "http://areebaseher04.pythonanywhere.com/api/billing/"

payload = {}
headers = {
  'Authorization': 'Token ff79dfc866e6e89a4ab31257c94b928ed9965b61'
}

response = requests.request("GET", url, headers=headers, data = payload)

print(response.text.encode('utf8'))
```

### Subscription (Go pro from free trial to member) | Members will charge automatically at the end of each month
```
import requests

url = "http://areebaseher04.pythonanywhere.com/api/subscribe/"

payload = {'stripeToken': 'tok_1HLTM7IT5J9fMCNzREpaqXEv'}  #this is test stripeToken
files = [
]
headers = {
  'Authorization': 'Token ff79dfc866e6e89a4ab31257c94b928ed9965b61'
}

response = requests.request("POST", url, headers=headers, data = payload, files = files)

print(response.text.encode('utf8'))
```

### Cancel Subscription
```
import requests

url = "http://areebaseher04.pythonanywhere.com/api/cancel-subscribe/"

payload = {}
files = {}
headers = {
  'Authorization': 'Token 9a2a2e085d7a722a537be045eccd5e40ee499736'
}

response = requests.request("POST", url, headers=headers, data = payload, files = files)

print(response.text.encode('utf8'))
```

