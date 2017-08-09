"""------------------------------------------------------------------------------
Welcome to the HarborMaster API main.py file.  Also see app.yaml.
See https://boatslipsbychris.appspot.com/ for documentation on using the API.

GENERAL CITATION: Code adapted from various lectures and Materials as professed
by Mr. Justin Wolford, Oregon State University and the various Google NDB
CLient Library online documentation pages.  See within for additional citations.

Developer Notes:
Manage instances: https://console.cloud.google.com/appengine/versions
Manage entities:  https://console.cloud.google.com/datastore/entities
Debug: https://console.cloud.google.com/errors
------------------------------------------------------------------------------"""
import webapp2, json
from datetime import datetime
from google.appengine.ext import ndb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

MAX_SLIPS = 100
MAX_BOATS = 100

def getSlipNum():
    """ Returns a slip number starting at 1 and auto increments thereafter.
    NO RESET ON PROGRAM RE-DEPLOY - only on deleting Slip entities. """
    query = Slip.query()
    results = query.fetch(limit = MAX_SLIPS)
    temp = 0
    for result in results:
        if result.number > temp:
            temp = result.number
    slipNum = temp
    slipNum += 1
    return slipNum


def test4ValidEntity(id):
    """ Returns the key or None. """
    object = None
    try:
        object = ndb.Key(urlsafe=id).get()
    except Exception, e:
        if e.__class__.__name__ == ProtocolBufferDecodeError:
            object = None
    return object


class Boat(ndb.Model):
    """ Models an individual Boat entity. """
    id = ndb.StringProperty()
    name = ndb.StringProperty()
    type = ndb.StringProperty()
    length = ndb.IntegerProperty()
    at_sea = ndb.BooleanProperty()


class BoatHandler(webapp2.RequestHandler):
    """ Handles instantiation, deletion, and mutation of a Boat entity.
        Returns json formatted string. """
    def post(self):
        """ Instantiates a new boat object and returns json string with its details. """
        parent_key = ndb.Key(Boat, "parent_boat")
        boat_data = json.loads(self.request.body)
        new_boat = Boat(id=None, name=boat_data['name'], type=boat_data['type'],
                        length=boat_data['length'], at_sea=True, parent=parent_key)
        new_boat.put()
        new_boat.id = '/Boat/' + new_boat.key.urlsafe()
        new_boat.put()
        boat_dict = new_boat.to_dict()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(boat_dict))
       
    def get(self, id=None):
        """ Returns json string with Boat entity details by id. 
        CITATION: Adapted from https://github.com/googlecloudplatform/datastore-ndb-python/issues/143 """
        if id:
            boat = test4ValidEntity(id)
            if boat == None:
                self.response.set_status(404)
            else:
                boat_dict = boat.to_dict()
                self.response.headers['Content-Type'] = 'application/json'
                self.response.write(json.dumps(boat_dict))

    def delete(self, id=None):
        """ Deletes a Boat entity.  """
        if id:
            boat = test4ValidEntity(id)
            if boat == None:
                self.response.set_status(404)
            else:
                if boat.at_sea == False:
                    query = Slip.query(Slip.current_boat == boat.id)
                    result = query.fetch(limit = 1)
                    for match in result:
                        match.current_boat = None
                        match.arrival_date = None
                        match.put()
                    boat.key.delete()
                    self.response.write("Boat has been deleted!")                        
                else:
                    boat.key.delete()
                    self.response.write("Boat has been deleted!")

    def patch(self, id=None):
        """ Mutates user supplied Boat entity properties by id.
        Un-addressed properties remain. """
        if id:
            boat = test4ValidEntity(id)
            if boat == None:
                self.response.set_status(404)
            else:
                boat_data = json.loads(self.request.body)
                if 'name' in boat_data:
                    boat.name = boat_data['name']
                if 'type' in boat_data:
                    boat.type = boat_data['type']
                if 'length' in boat_data:
                    boat.length = boat_data['length']
                boat.put()
                boat_dict = boat.to_dict()
                self.response.headers['Content-Type'] = 'application/json'
                self.response.write(json.dumps(boat_dict))

    def put(self, id=None):
        """ Mutates user supplied Boat entity properties by id. Un-addressed properties,
        where allowed, become None (null). Returns updated Boat entity json string. """
        if id:
            boat = test4ValidEntity(id)
            if boat == None:
                self.response.set_status(404)
            else:
                boat_data = json.loads(self.request.body)
                if 'name' in boat_data:
                    boat.name = boat_data['name']
                else:
                    boat.name = None
                if 'type' in boat_data:
                    boat.type = boat_data['type']
                else:
                    boat.type = None
                if 'length' in boat_data:
                    boat.length = boat_data['length']
                else:
                    boat.length = None
                boat.put()
                boat_dict = boat.to_dict()
                self.response.headers['Content-Type'] = 'application/json'
                self.response.write(json.dumps(boat_dict))


class ViewAllBoats(webapp2.RequestHandler):
    def get(self):
        """ Returns an array of json objects representing all Boat entities.
        CITATION: Adapted from http://stackoverflow.com/questions/33025095/pulling-data-from-datastore
        -and-converting-it-in-json-in-pythongoogle-appengine """
        query = Boat.query()
        results = query.fetch(limit = MAX_BOATS)
        boat_dicts = []
        for match in results:
            boat_dicts.append({'id': match.id, 'name': match.name, 'type': match.type,
                               'length': match.length, 'at_sea': match.at_sea })
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(boat_dicts))


class Slip(ndb.Model):
    """ Models an individual Slip """
    id = ndb.StringProperty()
    number = ndb.IntegerProperty()
    current_boat = ndb.StringProperty()
    arrival_date = ndb.StringProperty()
    departure_history = ndb.StringProperty()
    departure_date = ndb.StringProperty()
    departed_boat = ndb.StringProperty()
    

class SlipHandler(webapp2.RequestHandler):
    """ Handles instantiation, deletion, and mutation of a Slip entity.
    Returns json formatted string.
    CITATION: Adapted from http://stackoverflow.com/questions/16333296/how-do-you-create-nested-dict-in-python """
    def post(self):
        parent_key = ndb.Key('Slip', "parent_slip")
        slip_data = json.loads(self.request.body)
        list = []
        new_slip = Slip(id=None, number=getSlipNum(), current_boat=None, arrival_date=None,
                        departure_history=None, departure_date=None, departed_boat=None, parent=parent_key)
        new_slip.put()
        new_slip.id =  '/Slip/' + new_slip.key.urlsafe()
        new_slip.put()
        slip_dict = new_slip.to_dict()
        slip_dict['departure_history'] = {}
        slip_dict['departure_history']['departure_date'] = new_slip.departure_date
        slip_dict['departure_history']['departed_boat'] = new_slip.departed_boat
        del slip_dict['departed_boat'], slip_dict['departure_date']
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(slip_dict))

    def get(self, id=None):
        """ Returns json string with Slip entity details by id. """
        if id:
            slip = test4ValidEntity(id)
            if slip == None:
                self.response.set_status(404)
            else:
                slip_dict = slip.to_dict()
                slip_dict['departure_history'] = {}
                slip_dict['departure_history']['departure_date'] = slip.departure_date
                slip_dict['departure_history']['departed_boat'] = slip.departed_boat
                del slip_dict['departed_boat'], slip_dict['departure_date']
                self.response.headers['Content-Type'] = 'application/json'
                self.response.write(json.dumps(slip_dict))

    def delete(self, id=None):
        """ Deletes a Slip entity. If slip was occupied, returns that Boat entity's json string. """
        if id:
            slip = test4ValidEntity(id)
            if slip == None:
                self.response.set_status(404)
            else:
                if slip.current_boat != None:
                    """ Tests for a Boat "docked" in slip to be deleted. if found, sets the
                    Boat entity at_sea property to True and deletes the slip. """
                    boat_dict = None
                    query = Boat.query(Boat.at_sea == False)
                    results = query.fetch(limit = MAX_BOATS)
                    for match in results:
                        if slip.current_boat == match.id:
                            match.at_sea = True
                            match.put()
                    slip.key.delete()
                    self.response.write("Slip has been deleted!")
                else:
                    slip.key.delete()
                    self.response.write("Slip has been deleted!")

    def patch(self, id=None):
        """ Mutates user supplied Slip entity properties by id. Un-addressed 
        properties remain. Returns updated Slip entity json string. """
        if id:
            slip = test4ValidEntity(id)
            if slip == None:
                self.response.set_status(404)
            else:
                slip_data = json.loads(self.request.body)
                if 'number' in slip_data:
                    """ Test for Slip number already taken. """
                    query = Slip.query()
                    results = query.fetch(limit = MAX_SLIPS)
                    if slip.number in results:
                        slip.number = getSlipNum()
                    else:
                        slip.number = slip_data['number']
                if 'current_boat' in slip_data:
                    if slip.current_boat == None:
                        slip.current_boat = slip_data['current_boat']
                    else:
                        """ Query for the Boat and change at_sea to False. """
                        query = Boat.query(Boat.id == slip_data['current_boat'])
                        result = query.fetch(limit = 1)
                        if 'at_sea' in result:
                            result.at_sea = False
                        slip.current_boat = slip_data['current_boat']
                if 'arrival_date' in slip_data:
                    slip.arrival_date = slip_data['arrival_date']
                if 'departed_boat' in slip_data:
                    slip.departed_boat = slip_data['departed_boat']
                if 'departure_date' in slip_data:
                    slip.departure_date = slip_data['departure_date']
                slip.put()
                slip_dict = slip.to_dict()
                del slip_dict['departure_history']
                self.response.headers['Content-Type'] = 'application/json'
                self.response.write(json.dumps(slip_dict))

    def put(self, id=None):
        """ Mutates user supplied Slip entity properties by id. Un-addressed properties,
        where allowed, become None (null). Returns updated Slip entity json string. """
        if id:
            slip = test4ValidEntity(id)
            if slip == None:
                self.response.set_status(404)
            else:
                slip_data = json.loads(self.request.body)
                if 'number' in slip_data:
                    """ Test for requested Slip number already in use. """
                    query = Slip.query()
                    results = query.fetch(limit = MAX_SLIPS)
                    for match in results:
                        if slip_data['number'] == match.number:
                            slip.number = getSlipNum()
                        else:
                            slip.number = slip_data['number']
                if 'current_boat' in slip_data:
                    if slip.current_boat == None:
                        slip.current_boat = slip_data['current_boat']
                    else:
                        """ Query for the Boat and change at_sea to False. """
                        query = Boat.query(Boat.id == slip_data['current_boat'])
                        result = query.fetch(limit = 1)
                        if 'at_sea' in result:
                            result.at_sea = False
                        slip.current_boat = slip_data['current_boat']
                else:
                    slip.current_boat = None
                if 'arrival_date' in slip_data:
                    slip.arrival_date = slip_data['arrival_date']
                else:
                    slip.arrival_date = None
                if 'departed_boat' in slip_data:
                    slip.departed_boat = slip_data['departed_boat']
                else:
                    slip.departed_boat = None
                if 'departure_date' in slip_data:
                    slip.departure_date = slip_data['departure_date']
                else:
                    slip.departure_date = None
                slip.put()
                slip_dict = slip.to_dict()
                del slip_dict['departure_history']
                self.response.headers['Content-Type'] = 'application/json'
                self.response.write(json.dumps(slip_dict))


class ViewAllSlips(webapp2.RequestHandler):
    """ Returns a nested array of json strings representing all Slip entities. """
    def get(self):
        query = Slip.query()
        results = query.fetch(limit = MAX_SLIPS)
        aList = []
        for match in results:
            aSlip = {'id': match.id,
                     'number': match.number,
                     'current_boat': match.current_boat,
                     'arrival_date': match.arrival_date,
                     'departure_history': {
                         'departure_date': match.departure_date,
                         'departed_boat': match.departed_boat}
                     }
            aList.append(aSlip)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(aList))

        
class DockOps(webapp2.RequestHandler):
    """ Manage a Boat Arrival. Returns json of affected Slip details or 403 if occupied. """
    def put(self, id=None):
        if id:
            boat2bDocked = test4ValidEntity(id)
            if boat2bDocked == None:
                self.response.set_status(404)
            else:
                requestBody = json.loads(self.request.body)
                query = Slip.query(Slip.number == requestBody['number'])
                result = query.fetch()
                for match in result:
                    if match.current_boat == None:
                        match.current_boat = boat2bDocked.id
                        match.arrival_date = requestBody['arrival_date']
                        match.put()
                        slip_dict = match.to_dict()
                        boat2bDocked.at_sea = False
                        boat2bDocked.put()
                        self.response.headers['Content-Type'] = 'application/json'
                        self.response.write(json.dumps(slip_dict))
                    else:
                        self.response.set_status(403)

    def patch(self, id=None):
        """ Manage a Boat Departure. Returns json of affected Slip details or ignores if requested
        departure Boat ID does not match requested Slip's current_boat ID. """
        if id:
            boat2Depart = test4ValidEntity(id)
            if boat2Depart == None:
                self.response.set_status(404)
            else:
                requestBody = json.loads(self.request.body)
                query = Slip.query(Slip.number == requestBody['number'])
                result = query.fetch(limit = 1)
                for match in result:
                    if match.current_boat == boat2Depart.id and match.number == requestBody['number']:
                        boat2Depart.at_sea = True
                        boat2Depart.put()
                        match.current_boat = None
                        match.arrival_date = None
                        match.departure_date = requestBody['departure_date']
                        match.departed_boat = boat2Depart.id
                        match.put()
                        slip_dict = match.to_dict()
                        del slip_dict['departure_history']
                        self.response.headers['Content-Type'] = 'application/json'
                        self.response.write(json.dumps(slip_dict))
                    else:
                        self.response.set_status(400)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Welcome to the HarborMaster API.\n\n')
        self.response.out.write(datetime.now())
        self.response.write('\n\nThis is the main HarborMaster API documentation page!\n\n')

""" Adds PATCH method to webapp2. """
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

# Routes and their Handlers.
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/Boat', BoatHandler),
    ('/Boat/', BoatHandler),
    ('/Boat/(.*)', BoatHandler),
    ('/Boat/Boat', BoatHandler),
    ('/Boat/Boat/', BoatHandler),    
    ('/Boat/Boat/(.*)', BoatHandler),
    ('/AllBoats', ViewAllBoats),
    ('/DockOps/Boat/(.*)', DockOps),
    ('/Slip', SlipHandler),
    ('/Slip/', SlipHandler),
    ('/Slip/(.*)', SlipHandler),
    ('/Slip/Slip', SlipHandler),
    ('/Slip/Slip/', SlipHandler),
    ('/Slip/Slip/(.*)', SlipHandler),
    ('/AllSlips', ViewAllSlips)
], debug=True)
