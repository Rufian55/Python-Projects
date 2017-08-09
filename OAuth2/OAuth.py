#!/usr/bin/env python
"""--------------------------------------------------------------------------------------------------------
OAuth.py is the page the user is redirected following successful authentication at Google's authentication
page. Further processing is performed for XSFR and then user's name, Google+ account access link, and the
before and after random State variables are displayed to to the user.  User is also offered a Log Out link.
CITATIONS:
[1] Lecture and materials as professed by Mr. Justin Wolford, Oregon State University, 2017.
[2] The various Google Cloud Platform developer documents, including:
    https://developers.google.com/identity/protocols/OAuth2WebServer
    https://developers.google.com/api-client-library/python/guide/aaa_oauth
    et. al.
[3] https://docs.python.org/2/ (various)
--------------------------------------------------------------------------------------------------------"""
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
import webapp2, json, urllib

class State(ndb.Model):
    """ Models an individual State variable """
    currState = ndb.StringProperty()


class OAuthHandler(webapp2.RequestHandler):
    def get(self):
        result1 = repr(self.request.GET)
        state = result1[31:46]
        code = result1[62:-4]
        query = State.query()
        result2 = query.fetch(1)
        client_secret = "Mismatch"
        if state == result2[0].currState:
            client_secret = "jUoI70YD6GrVw6ZobaZUYREU"
        url = "https://accounts.google.com/o/oauth2/token"
        client_id = "5131047478-9dn4qc3m7su443o44iurio48hv2g607t.apps.googleusercontent.com"
        redirect_uri = "https://chrisauth-166416.appspot.com/OAuth"
        grant_type = "authorization_code"
        payload = {"grant_type": grant_type,
                   "code": code,
                   "client_id": client_id,
                   "client_secret": client_secret,
                   "redirect_uri": redirect_uri
                   }
        payload = urllib.urlencode(payload)
        result3 = urlfetch.fetch(url, payload, method='POST')
        result4 = json.loads(result3.content)
        access_token = result4['access_token']
        header = {'Authorization': "Bearer " + access_token}
        url2 = "https://www.googleapis.com/plus/v1/people/me"
        result5 = urlfetch.fetch(url2, headers=header)
        data = json.loads(result5.content)
        throwHTML = "<html><head><title>OAuth 2.0 Demo</title>\
                    <link rel=\"stylesheet\" type=\"text/css\" href=\"www/css/style.css\">\
                    </head><body><p></p><p></p>\
                    <h1>Welcome to Chris' OAuth 2.0 Demo Page v1.11</h1>\
                    <h2>Where Authorizations Are Made Every Day!</h2>\
                    <h3><a href=\"/\">Log Out</a></h3>"
        self.response.write(throwHTML)
        self.response.write("<p>" + "User's Name: " + data['displayName'] + "</p>")
        self.response.write("<h3><a href=" + data['url'] + ">" + data['url'] + "</a></h3>")
        self.response.write("<p>" + "State originally sent: " + state + "</p>")
        self.response.write("<p>" + "State received back: " + result2[0].currState + "</p>")
        self.response.write("</body></html>")

app = webapp2.WSGIApplication([
    ('/OAuth', OAuthHandler)
], debug=True)
