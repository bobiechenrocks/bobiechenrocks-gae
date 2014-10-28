#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from flask import Flask, request, render_template
from twilio.util import TwilioCapability
import twilio.twiml
import os
import yaml
import logging

app = Flask(__name__)

record = False

logging.getLogger().setLevel(logging.DEBUG)

@app.route('/callDispatch', methods=['GET', 'POST'])
def callDispatch():
  """ This method routes calls from/to client                """
  """ Rules: 1. Call from PSTN has empty to_number, figure   """
  """           out the realm from the account               """
  """        2. to_number starting with client: calls client """
  to_number = request.values.get('to_number')
  resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
  
  resp += "<Response>"
  
  if to_number == None:
      resp += "<Say>Thanks for using the sample application, Please specify outgoing destination and call again later. Good bye.</Say>"
  else:
      resp += "<Dial"
      if record:
          resp += "record=\"true\""
      resp += " callerId=\""
      resp += request.values.get('From')
      resp += "\">"

      resp += "<Client>"
      resp += to_number[7:]
      resp += "</Client>"
      
      resp += "</Dial>"
          
      '''
      if to_number.startswith("client:"):
          resp += "<Client>"
          resp += to_number[7:]
          resp += "</Client>"
      elif to_number.startswith("sip:"):
          resp += "<Sip>"
          resp += to_number
          resp += "</Sip>"
      elif to_number.startswith("conf:"):
          resp += "<Conference>"
          resp += to_number[5:]
          resp += "</Conference>"
      else:  
          resp += to_number
      '''
          
  resp += "</Response>"
  logging.debug(resp)
  return resp

@app.route('/')
def startClient():
  """ Twilio JS token generation, client name is per configuration"""
  params = getParamsFromRealm(request.values.get('realm'))
  if request.values.get('chunderw'):
    params['chunderw'] = request.values.get('chunderw')
  if request.values.get('javascript'):
    params['twiliojs'] = request.values.get('javascript')
  if request.values.get('client'):
    params['client'] = request.values.get('client')
  if request.url.startswith('https'):
    params['secureSignaling'] = True
  else:
    params['secureSignaling'] = False
  if request.values.get('securesignaling'):
    params['secureSignaling'] = request.values.get('securesignaling')
  capability = TwilioCapability(params['account_sid'], params['auth_token'])
  capability.allow_client_outgoing(params['app_sid'])
  capability.allow_client_incoming(params['client'])
  token = capability.generate(expires=3600)
  return render_template('client.html', token = token, **params)

def get_config():
  config_file = open('config.yaml')
  config = yaml.load(config_file)
  config_file.close()
  return config

def getParamsFromRealm(realm):
  config = get_config()
  if realm == 'prod':
    return config[0]
  elif realm == 'stage':
    return config[2]
  elif realm in {'ie', 'br', 'jp', 'sg', 'au', 'ie1'}:
    params = config[0]
    params['chunderw'] = 'chunderw0.' + realm + '.twilio.com'
    return params
  else:
    return config[1]

def getParamsFromAccount(account):
  config = get_config()
  if config[0]['account_sid'] == account:
    return config[0]
  elif config[1]['account_sid'] == account:
    return config[1]
  else:
    return config[2]
    
def get_typed_args(args):
    d = {}
    for key, val in args.items():
        try:
            # make things like True and False word right
            # also disallow all access to any builtin symbols/functions
            d[key] = eval(val, {"__builtins__": {'True':True, 'False':False}}, {})
        except (SyntaxError, NameError):
            d[key] = val
    return d

@app.route('/token')
def token():
  """ Twilio iOS/Android SDK token generation, client name as per request """
  client = request.values.get('client')
  typed_args = get_typed_args(request.args)
  allow_outbound = typed_args.get('allow_outbound')
  try:
    expires = int(request.values.get('expires'))
  except (TypeError, ValueError):
    expires = 3600
  params = getParamsFromRealm(request.values.get('realm'))
  capability = TwilioCapability(params['account_sid'], params['auth_token'])
  if allow_outbound:
    capability.allow_client_outgoing(params['app_sid'])
  if client != None:
    capability.allow_client_incoming(client)
  return capability.generate(expires = expires)

@app.route('/ohsip', methods=['GET', 'POST'])
def ohsip():
  """ This is the ohsip application """
  """ For API call, we play a one minute long file """
  resp = twilio.twiml.Response()
  number = request.values.get('number')
  if number == None:
    resp.play("https://api.twilio.com/cowbell.mp3");
    logging.debug(resp.toxml())
    return resp.toxml()
  test = request.values.get('SipHeader_X-OhSIP-Servlet')
  if test == 'OutgoingCallReject':
    resp.reject()
  else:
    timeLimit = request.values.get('timeLimit')
    callerId = request.values.get('callerId')
    if number.startswith("client:"):
      resp.dial(callerId=callerId, timeLimit=timeLimit).client(number[7:])
    else:
      resp.dial(callerId=callerId, timeLimit=timeLimit).number(number)
  logging.debug('Test case: ' + str(test) + ', response: ' + resp.toxml())
  return resp.toxml()

# original webapp2 codes
'''
import webapp2

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
'''