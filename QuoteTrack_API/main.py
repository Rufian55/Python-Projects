"""------------------------------------------------------------------------------
Welcome to the quotetrack API main.py file.  Also see app.yaml.
See https://quotetrack-169521.appspot.com/ for documentation on using the API.

GENERAL CITATION: Code adapted from various Lectures and Materials as professed
by Mr. Justin Woolford, Oregon State University and the various Google NDB
CLient Library online documentation pages.  See within for additional citations.
[Postman Test 14B] https://stackoverflow.com/questions/10311361/accessing-json
                    -object-keys-having-spaces

Developer Notes:
Manage deployment: https://cloud.google.com/sdk/gcloud/reference/config/set
Manage instances: https://console.cloud.google.com/appengine/versions
Manage entities:  https://console.cloud.google.com/datastore/entities
Debug: https://console.cloud.google.com/errors
------------------------------------------------------------------------------"""
import webapp2, json
from datetime import datetime
from google.appengine.ext import ndb

def test4ValidEntity(email):
    """ Returns 1 User entity by email property. """
    userEntity = User.query(User.email == email).fetch(1)
    if not userEntity:
        return None
    else:
        return userEntity

class User(ndb.Model):
    """ Models an individual User Account entity. """
    id = ndb.StringProperty()
    email = ndb.StringProperty()
    ticker0 = ndb.StringProperty()
    ticker1 = ndb.StringProperty()
    ticker2 = ndb.StringProperty()
    ticker3 = ndb.StringProperty()
    ticker4 = ndb.StringProperty()
    ticker5 = ndb.StringProperty()
    ticker6 = ndb.StringProperty()
    ticker7 = ndb.StringProperty()
    ticker8 = ndb.StringProperty()
    ticker9 = ndb.StringProperty()

class UserHandler(webapp2.RequestHandler):
    """ Handles all facets of a user account. """
    def delete(self, email=None):
        """ Deletes a user's account. """
        userEntity = None
        if email:
            userEntity = test4ValidEntity(email)
        if userEntity is not None:
            for result in userEntity:
                if result.email == email:
                    result.key.delete()
                    user_dict = "Account deleted!"
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(user_dict))
        else:
            user_dict = "No such account..."
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(user_dict))
    
    def get(self, email=None):
        userEntity = None
        if email:
            userEntity = test4ValidEntity(email)
        if userEntity is not None:
            user_dict = []
            for result in userEntity:
                user_dict.append({'email': result.email, 'ticker0': result.ticker0,
                                  'ticker1': result.ticker1, 'ticker2': result.ticker2, 'ticker3': result.ticker3,
                                  'ticker4': result.ticker4, 'ticker5': result.ticker5, 'ticker6': result.ticker6,
                                  'ticker7': result.ticker7, 'ticker8': result.ticker8, 'ticker9': result.ticker9 })
            if not user_dict:
                user_dict = "fail"
                self.response.headers['Content-Type'] = 'application/json'
                self.response.write(json.dumps(user_dict))
            else:
                self.response.headers['Content-Type'] = 'application/json'
                self.response.write(json.dumps(user_dict))
        else:
            user_dict = "No such account..."
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(user_dict))

    def patch(self, email=None):
        """ Modifies a user's tickers. Un-addressed properties remain. """
        user_data = json.loads(self.request.body)
        userEntity = None
        if email:
            userEntity = test4ValidEntity(email)
        if userEntity is not None:
            for result in userEntity:
                if 'ticker0' in user_data:
                    result.ticker0 = user_data['ticker0']
                if 'ticker1' in user_data:
                    result.ticker1 = user_data['ticker1']
                if 'ticker2' in user_data:
                    result.ticker2 = user_data['ticker2']
                if 'ticker3' in user_data:
                    result.ticker3 = user_data['ticker3']
                if 'ticker4' in user_data:
                    result.ticker4 = user_data['ticker4']
                if 'ticker5' in user_data:
                    result.ticker5 = user_data['ticker5']
                if 'ticker6' in user_data:
                    result.ticker6 = user_data['ticker6']
                if 'ticker7' in user_data:
                    result.ticker7 = user_data['ticker7']
                if 'ticker8' in user_data:
                    result.ticker8 = user_data['ticker8']
                if 'ticker9' in user_data:
                    result.ticker9 = user_data['ticker9']
            result.put()
            user_dict = result.to_dict()
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(user_dict))
        else:
            user_dict = "No such account..."
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(user_dict))
        
    def post(self):
        """ Creates a new user account and returns json string with its details, 
            but first, tests for user's email already exists. """
        user_data = json.loads(self.request.body)
        user_dict = []
        email = user_data['email']
        userEntity = None
        userEntity = test4ValidEntity(email)
        if userEntity is not None:
            for result in userEntity:
                if result.email == email:
                    user_dict = "dupe"
                    self.response.headers['Content-Type'] = 'application/json'
                    self.response.write(json.dumps(user_dict))
        else:
            parent_key = ndb.Key(User, "parent_user")
            new_user = User(id=None, email=user_data['email'], ticker0=user_data['ticker0'],
                            ticker1=user_data['ticker1'], ticker2=user_data['ticker2'],
                            ticker3=user_data['ticker3'], ticker4=user_data['ticker4'],
                            ticker5=user_data['ticker5'], ticker6=user_data['ticker6'],
                            ticker7=user_data['ticker7'], ticker8=user_data['ticker8'],
                            ticker9=user_data['ticker9'], parent=parent_key)
            new_user.put()
            new_user.id = '/User/' + new_user.key.urlsafe()
            new_user.put()
            user_dict = new_user.to_dict()
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(user_dict))
    
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Welcome to the quoteTrack API.\n\n')
        self.response.out.write(datetime.now())
        self.response.write('\n\nThis is the main quoteTrack API documentation page!\n\n')

""" Adds PATCH method to webapp2. """
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

# Routes and their Handlers.
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/User', UserHandler),
    ('/User/(.*)', UserHandler)
], debug=True)
