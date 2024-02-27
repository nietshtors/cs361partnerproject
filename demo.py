import requests


URL = 'http://localhost:8000/'

user = {
    'username': 'seth',
    'password': 'thispassword'
}

profile_info = {
    'color': 'red',
    'age': 25
}

"""User Service"""
print('Add a new user:')
print(requests.post(URL + 'users', params=user).text)

print('\nReturns User ID given a username and password:')
user_id = requests.get(URL + 'users', params=user).text
print(user_id)

print('\nReturns username and password from a User ID:')
print(requests.get(URL + f'users/{user_id}').text)

print('\nUpdate a username or password:')
print(requests.put(URL + f'users/{user_id}', params={'password': 'drowssap'}).text)

print('\nDelete a user:')
print(requests.get(URL + 'users').text)
print(requests.delete(URL + f'users/{user_id}').text)
print(requests.get(URL + 'users').text)
print('Add user back')
user_id = requests.post(URL + 'users', params=user).text

print('\nGets all users:')
print(requests.get(URL + 'users').text)


"""Authentication?"""
print('\nLogin returns User ID:')
print(requests.post(URL + 'login', params=user).text)


"""User Profiles"""
print('\nGets user profile info from ID:')
print(requests.get(URL + f'profiles/{user_id}').text)

print('\nUpdates user profile info from ID:')
print(requests.get(URL + f'profiles/{user_id}').text)
print(requests.put(URL + f'profiles/{user_id}', params=profile_info).text)
print(requests.get(URL + f'profiles/{user_id}').text)



