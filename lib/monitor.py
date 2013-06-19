#!/usr/bin/env python

#
#  monitor.py
#
#  For details and documentation:
#  https://github.com/inkling/pdresolver
#
#  Copyright 2013 Inkling Systems, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import sys
import time
import json
import logging
import requests
import services
import traceback

CONF_FILE = "/etc/pdresolver/conf.json"
LOG_FILE = "/var/log/inkling/pdresolver.log"

# PagerDuty
SERVICES_URL = "https://%s.pagerduty.com/api/v1/services"
INCIDENTS_URL = "https://%s.pagerduty.com/api/v1/incidents"
OPEN_INCIDENTS_URL = "https://%s.pagerduty.com/api/v1/incidents?" \
                     "status=triggered,acknowledged"

log = logging.getLogger()
log.setLevel(logging.INFO)

# Turn off annoying Requests logging
logging.getLogger('requests').setLevel(logging.WARNING)


class Monitor(object):
    def __init__(self, **kwargs):
        self.interval = kwargs['interval']
        self.keys = dict((k.lower(), v) for k, v in
                         json.load(open(kwargs['conf_file'], 'r')).iteritems())

        self.api_key = self.option('api_key', kwargs, self.keys)
        self.requester_id = self.option('requester_id', kwargs, self.keys)
        self.subdomain = self.option('subdomain', kwargs, self.keys)
        self.headers = {"Authorization": "Token token=%s" % self.api_key,
                        "Content-Type": 'application/json'}

        self.services = dict((service.__name__.lower(),
                              service(self.keys[service.__name__.lower()]))
                             for service in self.__get_services())

    def option(self, name, set_vals, keys):
        if set_vals.get(name, False):
            return set_vals[name]
        else:
            return keys['pagerduty'][name]

    def __get_services(self):
        for s in services.__all__:
            module = getattr(services, s)
            for obj in dir(module):
                if obj.lower() == s.lower():
                    yield getattr(module, obj)
                    break

    def get_open_incidents(self):
        resp = requests.get(OPEN_INCIDENTS_URL % self.subdomain,
                            headers=self.headers)
        resp.raise_for_status()
        return resp.json()['incidents']

    def resolve(self, incident):
        log.info("Resolving incident #%s on PagerDuty...", incident['id'])
        data = {
            'incidents': [{'id': incident['id'], 'status': 'resolved'}],
            'requester_id': self.requester_id,
        }
        resp = requests.put(INCIDENTS_URL % self.subdomain,
                            data=json.dumps(data),
                            headers=self.headers)
        resp.raise_for_status()
        if resp.json()['incidents'][0]['status'] == "resolved":
            log.info("Resolved incident #%s!", incident['id'])
        else:
            raise ValueError("Incident %s not resolved." % incident['id'])

    def watch(self):
        log.info("Watching pagerduty for incidents.")
        while True:
            try:
                self.check_and_resolve_incidents()
            except:
                log.error(traceback.format_exc())
            time.sleep(self.interval)

    def check_and_resolve_incidents(self):
        for incident in self.get_open_incidents():
            service_name = incident['service']['name'].lower()
            if service_name in self.services:
                service = self.services[service_name]
                if service.incident_is_occurring(incident):
                    log.info("Incident %s currently occurring on '%s'.",
                             incident['id'], service_name)
                else:
                    log.info("Incident %s is not resolved on '%s'. Resolving...",
                             incident['id'], service_name)
                    self.resolve(incident)
                    log.info("Resolved incident %s triggered by %s.",
                             incident['id'], service_name)


def main(args):
    fileHandler = logging.FileHandler(args.log_file)
    fileHandler.setFormatter(logging.Formatter('[%(asctime)-15s] %(message)s'))
    log.addHandler(fileHandler)
    log.addHandler(logging.StreamHandler(sys.stdout))
    try:
        Monitor(**args.__dict__).watch()
    except:
        log.error(traceback.format_exc())
        raise
