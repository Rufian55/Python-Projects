#!/usr/bin/env python
"""-------------------------------------------------------------------------------------------------------
clientAuth.py is the initial random state variable and user redirect to Google's authentication page.
Following successful authentication, user is returned to OAuth.py and processed.
CITATIONS:
[1] Lecture and materials as professed by My Justion Wolford, Oregon State University, 2017.
[2] The various Google Cloud Platform developer documents, including:
    https://developers.google.com/identity/protocols/OAuth2WebServer
    https://developers.google.com/api-client-library/python/guide/aaa_oauth
    et. al.
[3] https://docs.python.org/2/
[4] et. al. further detailed below.   
-------------------------------------------------------------------------------------------------------"""
from google.appengine.ext import ndb
import logging, webapp2, json, random

URL_SAFE_KEY = "ahJwfmNocmlzYXV0aC0xNjY0MTZyEgsSBVN0YXRlGICAgICAgIAKDA"

class State(ndb.Model):
    """ Models an individual State variable """
    currState = ndb.StringProperty()


def getRandomState():
    """ http://stackoverflow.com/questions/2511222/efficiently-generate-a-16-character-alphanumeric-string """
    aState = ''.join(random.choice('123456789ABCDEF') for i in range(15))
    return aState

def saveState(newState):
    stateEntity = ndb.Key(urlsafe=URL_SAFE_KEY).get()
    stateEntity.currState = newState
    stateEntity.put()

class MainPage(webapp2.RequestHandler):
    def get(self):
        baseURL = "https://accounts.google.com/o/oauth2/auth"
        response_type = "?response_type=code"
        client_id = "&client_id=5131047478-9dn4qc3m7su443o44iurio48hv2g607t.apps.googleusercontent.com"
        redirect_uri = "&redirect_uri=https://chrisauth-166416.appspot.com/OAuth"
        scope = "&scope=email"
        access_type = "&access_type=offline"
        stateKey = "&state="
        state = getRandomState()
        saveState(state)
        url = baseURL + response_type + client_id + redirect_uri + scope + access_type + stateKey + state
        self.redirect(url)
        
app = webapp2.WSGIApplication([
    ('/clientAuth', MainPage)
], debug=True)
