# Utility webapp for starting VM and sending email with attachment from GCS
# 
# Author : daisuky-jp


import os
import httplib2
import logging
import json
import cloudstorage
from googleapiclient import discovery
from google.appengine.api import memcache
from google.appengine.api import mail
from oauth2client.contrib.appengine import AppAssertionCredentials
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/')
def hello():
    """default message"""
    return 'You came to experimental web application which will do nothing.'

@app.route('/vm/start')
def start_vm():
    """Start VM instance"""
    credentials = AppAssertionCredentials(scope='https://www.googleapis.com/auth/compute')
    http = credentials.authorize(httplib2.Http())
    compute = discovery.build('compute','v1',http=http)
    # Start the VM!
    zone = os.environ.get('ZONE')
    inst = os.environ.get('INST')
    proj = os.environ.get('PROJ')
    result = compute.instances().start(instance=inst,zone=zone,project=proj).execute()

    logging.debug(result)
    # return json.dumps(result, indent=4)
    return result["insertTime"]

@app.route('/sendmail', methods=['GET'])
def sayhello():
    """ Just say hello for GET request """
    return 'No action is evoked.'

@app.route('/sendmail', methods=['POST'])
def send2kind():
    """ Send email w/ attachment"""
    if 'X-Goog-Resource-State' in request.headers:
        resource_state = request.headers['X-Goog-Resource-State']
        if resource_state == 'exists':
            logging.info('Add message received.')
            add_obj = request.json
            bucket = add_obj['bucket']
            objname = add_obj['name']
            logging.info('%s/%s %s', bucket, objname, resource_state)
            # call to send email w/ attachment from the bucket
            cloudstorage_file = cloudstorage.open('/' + bucket + '/' + objname)
            recpaddr = os.environ.get('TOAD')
            sendaddr = os.environ.get('FRAD')
            logging.info('Sending to:' + recpaddr + ' from:' + sendaddr)
            mail.send_mail(sender=sendaddr,
                       to=recpaddr,
                       subject="Sending" + objname,
                       body="Sending mobi file",
                       attachments=[(objname, cloudstorage_file.read())])
            return objname + ' is added and sent to kindle'
        else:
            logging.info('Other state notification.'+resource_state)
            return 'Other state notification.'
    else:
        logging.info('Other post.')
        return 'Not correct request.'

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


