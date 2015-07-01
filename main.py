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
import os
import logging
from APNSWrapper import *
import binascii
import ssl

app = Flask(__name__)

record = False

logging.getLogger().setLevel(logging.DEBUG)

@app.route('/')
def startClient():
  return "Hello, BobieChenRocks!"

@app.route('/nicoleHBD')
def nicoleHBD():
  wrapper = APNSNotificationWrapper('nicole-apns.p12', True)

  # Bobie5: fd00a202 bc14239e f9d1135a 575513b4 83a4333b e001d443 90001987 09c7dae0
  deviceToken = binascii.unhexlify('fd00a202bc14239ef9d1135a575513b483a4333be001d4439000198709c7dae0')

  message = APNSNotification()
  message.token(deviceToken)
  message.alert("aloha apns")
  message.badge(1)

  wrapper.append(message)
  wrapper.notify()

  return "endpoint nicoleHBD"
