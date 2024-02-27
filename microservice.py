import json
import uuid

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


class StoreHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Sending an '200 OK' response
        self.send_response(200)
        # Setting the header
        self.send_header("Content-type", "text/html")
        # Whenever using 'send_header', you also have to call 'end_headers'
        self.end_headers()

        parsed = urlparse(self.path)
        dest = parsed.path.casefold().split('/')
        dest.remove('')
        query = parse_qs(parsed.query)

        with open('store.json', 'r') as f:
            data = json.load(f)
            user_dict = data['users']       # Dictionary of User IDs {"user_id": ["username", "password"]}
            login_arr = data['login']       # Array of logins   {"username": "user_id", "password": "user_id"}
            profile_arr = data['profiles']  # Array of profiles
            send = ''

            match dest[0]:
                case 'users':
                    # User ID is specified, gets username and password to match
                    if len(dest) > 1:
                        user_id = dest[1]
                        if user_id in user_dict:
                            send = str(user_dict[user_id])
                        else:
                            send = 'Invalid User ID'

                    # Username and password are specified, gets User ID
                    elif 'username' in query and 'password' in query:
                        for user in login_arr:
                            if query['username'][0] in user:
                                if query['password'][0] in user:
                                    uid = [*user.values()][0]
                                    pid = [*user.values()][1]
                                    if uid != pid:
                                        send = 'Error in database: different User IDs for username and password'
                                    else:
                                        send = str(uid)
                                    break
                                else:
                                    send = 'Wrong Password'
                        if not send:
                            send = 'Username not found'

                    # Gets the array of user ids and their associated username and password
                    else:
                        send = str(user_dict)

                case 'login':
                    send = 'You should be using POST with login'

                case 'profiles':
                    if len(dest) > 1:
                        user_id = dest[1]
                        for profile in profile_arr:
                            if profile['user_id'] == user_id:
                                send = str(profile)
                                break
                        if not send:
                            send = 'No profile found'
                    else:
                        send = str(profile_arr)

            # Writing the contents of send with UTF-8
            self.wfile.write(send.encode())

    def do_POST(self):
        """Handles POST, PUT, and DELETE"""
        # Sending an '200 OK' response
        self.send_response(200)
        # Setting the header
        self.send_header("Content-type", "text/html")
        # Whenever using 'send_header', you also have to call 'end_headers'
        self.end_headers()

        parsed = urlparse(self.path)
        dest = parsed.path.casefold().split('/')
        dest.remove('')
        query = parse_qs(parsed.query)  # dict containing params

        # Read in the data
        with open('store.json', 'r') as f:
            data = json.load(f)

        # Unpacking data for ease
        user_ids_arr = data['user_ids']     # Array of User IDs
        usernames_arr = data['usernames']   # Array of usernames
        user_dict = data['users']           # Dictionary of User IDs {"user_id": ["username", "password"]}
        login_arr = data['login']           # Array of logins   {"username": "user_id", "password": "user_id"}
        profile_arr = data['profiles']      # Array of profiles
        send = ''
        username = ''
        password = ''

        match dest[0]:
            case 'users':
                # Try to get username from query or from User ID
                try:
                    username = query['username'][0]
                except KeyError:
                    if len(dest) > 1:
                        user_id = dest[1]
                        if user_id in user_dict:
                            username = user_dict[user_id][0]
                # Try to get password from query or from User ID
                try:
                    password = query['password'][0]
                except KeyError:
                    if len(dest) > 1:
                        user_id = dest[1]
                        if user_id in user_dict:
                            password = user_dict[user_id][1]

                # Adds new username and password
                if len(dest) == 1 and self.command == 'POST':
                    if username in usernames_arr:
                        send = 'Username already exists'
                    elif not username:
                        send = 'Missing username'
                    elif not password:
                        send = 'Missing password'
                    else:
                        user_id = uuid.uuid4().hex
                        while user_id in user_ids_arr:
                            user_id = uuid.uuid4().hex
                        user_ids_arr.append(user_id)
                        usernames_arr.append(username)
                        user_dict[user_id] = [username, password]
                        login_arr.append({username: user_id, password: user_id})
                        profile_arr.append({'user_id': user_id})
                        # Sends back the new User ID on success
                        send = user_id

                # Updates a User ID with a new username and/or password
                elif len(dest) >= 2 and self.command == 'PUT':
                    user_id = dest[1]
                    if user_id not in user_ids_arr:
                        send = 'Invalid User ID'
                    else:
                        if user_id in user_dict:
                            old_username = user_dict[user_id][0]
                            old_password = user_dict[user_id][1]

                            usernames_arr.remove(old_username)
                            usernames_arr.append(username)
                            user_dict[user_id] = [username, password]
                            login_arr.remove({old_username: user_id, old_password: user_id})
                            login_arr.append({username: user_id, password: user_id})

                            send = 'Username and/or password updated'
                        else:
                            send = 'User ID not in users dict'

                # Deletes a user
                elif len(dest) >= 2 and self.command == 'DELETE':
                    user_id = dest[1]
                    if user_id not in user_ids_arr:
                        send = 'Invalid User ID'
                    else:
                        if user_id in user_dict:
                            old_username = user_dict[user_id][0]
                            old_password = user_dict[user_id][1]
                            user_ids_arr.remove(user_id)
                            user_dict.pop(user_id)
                            usernames_arr.remove(old_username)
                            login_arr.remove({old_username: user_id, old_password: user_id})
                            for profile in profile_arr:
                                if profile['user_id'] == user_id:
                                    profile_arr.remove(profile)
                                    break
                            send = f'User {user_id} removed'
                        else:
                            send = 'User ID not in users dict'
                else:
                    send = 'Something went wrong'

            case 'login':
                username = query['username'][0]
                password = query['password'][0]
                for user in login_arr:
                    if username in user:
                        if password in user:
                            if user[username] == user[password]:
                                send = user[username]
                            else:
                                send = 'Data corrupted, User IDs do not match'
                        else:
                            send = 'Incorrect password'
                        break
                if not send:
                    send = 'Login failed'

            case 'profiles':
                if len(dest) > 1:
                    user_id = dest[1]
                    for profile in profile_arr:
                        if profile['user_id'] == user_id:
                            profile_arr.remove(profile)
                            if self.command == 'POST':
                                profile.clear()
                                profile['user_id'] = user_id
                            for key, value in query.items():
                                if len(value) == 1:
                                    value = value[0]
                                profile[key] = value
                            profile_arr.append(profile)
                            break
                    send = 'Profile updated'
                else:
                    send = 'Unspecified user'

        # Repack data and write to file
        data = {
            'user_ids': user_ids_arr,
            'usernames': usernames_arr,
            'users': user_dict,
            'login': login_arr,
            'profiles': profile_arr
        }
        with open('store.json', 'w') as f:
            json.dump(data, f, indent=2)

        # Writing the contents of send with UTF-8
        self.wfile.write(send.encode())

    def do_PUT(self):
        self.do_POST()

    def do_DELETE(self):
        self.do_POST()


with HTTPServer(('', 8000), StoreHandler) as server:
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
