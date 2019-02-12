import requests
import string
import random
import json
import os
import time

users = os.getenv('NUMBER_OF_USERS', 3)
max_posts = os.getenv('MAX_POSTS_PER_USER', 3)
max_likes = os.getenv('MAX_LIKES_PER_USER', 3)
api_url = os.getenv('API_URL', 'http://localhost:8000/')

posts = []

def string_generator(max_length=32):
    min_char = 8
    allchar = string.ascii_letters + string.punctuation + string.digits
    return "".join(random.choice(allchar) for x in range(random.randint(min_char, max_length)))

class User(object):
    def __init__(self):
        # auth
        self.data = {
            'username': string_generator(),
            'password': 'passwordnumber'+ str(random.randint(1,1000)),
            'first_name': string_generator(),
            'last_name': string_generator(),
            'email': 'clonenumber'+ str(random.randint(1,1000)) + '@google.com',
        }

        self.likes = 0

        self.posts = []

        signup_response = self.signup()

        jwt_token = self.login()

        self.api = Api(jwt_token)

        for _ in range(random.randint(0,max_posts)):
            post = self.api.post().json()
            self.posts.append(post['id'])

    def signup(self):
        url = api_url + 'accounts/user/'
        return requests.post(url,data=self.data)

    def login(self):
        url = api_url + 'accounts/login/'
        data = {'email': self.data['email'],'password': self.data['password']}
        return requests.post(url,data=data).json()

class Api(object):
    def __init__(self, jwt_token):
        self.headers = {'Authorization': 'JWT '+ jwt_token['token'] }

    def get_posts(self):
        url = api_url + 'api/v1/post/'
        return requests.get(url, headers=self.headers)

    def post(self):
        url = api_url + 'api/v1/post/'
        data = {'data': json.dumps({'title': 'StartOver' + string_generator(),'text': string_generator()})}
        return requests.post(url, data=data, headers=self.headers)

    def like(self, post_id):
        url = api_url + 'api/v1/post/{}/like/'.format(post_id)
        return requests.put(url, headers=self.headers)

    def unlike(self, post_id):
        url = api_url + 'api/v1/post/{}/unlike/'.format(post_id)
        return requests.put(url, headers=self.headers)

def main():
    user_instances = []

    for _ in range(users):
        user_instances.append(User())

    while(True):

        winner = None
        max = 0
        for user in user_instances:
            if max < len(user.posts) and user.likes < max_likes:
                max = len(user.posts)
                winner = user

        if winner:
            for post in winner.api.get_posts():
                print(post)
                data = json.loads(post['data'])
                if data['count'] == 0:
                    target = post['owner']

            target_locked = []
            for post in winner.get_posts():
                if post['owner'] == target:
                    target_locked.append(post)

            like_target = random.randint(0, len(target_locked))

            winner.api.like(post_id=target_locked[like_target]['id'])
        else:
            # handy break
            break
        # Do I stop master ?
        # Lets assume yes
        answer = True

        for user in user_instances:
            for post in user.api.get_posts():
                if int(json.loads(post['data'])['count']) > 0:
                    continue
                else:
                    answer = False
                    # Not yet
                    break
            if answer == False:
                # Maybe later
                break

if __name__ == "__main__":
    main()
