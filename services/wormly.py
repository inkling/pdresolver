#
#  wormly.py
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

import logging
import requests
log = logging.getLogger(__name__)

import sys
import os
sys.path.append(os.path.split(os.getcwd())[0])

import json

from lib.service import Service

# Wormly
WORMLY_ERROR_SUBJECT = "Detected Error on "
WORMLY_IGNORE = " has Recovered"
WORMLY_URL_PREFIX = "https://api.wormly.com/?key=%s&response=json"


class Wormly(Service):
    @property
    def hosts(self):
        resp = requests.get((WORMLY_URL_PREFIX % self.keys['api_key'])
                            + "&cmd=getHostStatus")
        resp.raise_for_status()
        return dict([(blob['name'], blob) for blob in resp.json()['status']])

    def wormly_is_reporting_downtime_on(self, s):
        log.info("Checking Wormly status of '%s'...", s)
        host = self.hosts.get(s, False)
        if not host:
            raise RuntimeError("Could not find service '%s' in Wormly!" % s)
        if not host['uptimemonitored'] and not host['healthmonitored']:
            raise ValueError("'%s' is not currently being monitored." % s)
        return host['uptimeerrors'] or host['healtherrors']

    def incident_is_occurring(self, incident):
        subject = incident['trigger_summary_data']['subject']
        if WORMLY_IGNORE in subject or not WORMLY_ERROR_SUBJECT in subject:
            return False
        service = subject.replace(WORMLY_ERROR_SUBJECT, '').strip()
        return self.wormly_is_reporting_downtime_on(service)

if __name__ == '__main__':
    """
    This is a simple way to test your integration with wormly via command line.
    It just checks to make sure you can do API calls.
    """
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('service', type=str)
    args = parser.parse_args()
    
    with open(os.getcwd() + '/../conf.json') as conf:
        keys = dict((k.lower(), v) for k, v in json.load(conf).iteritems())
        w = Wormly(keys['wormly'])
        print w.wormly_is_reporting_downtime_on(args.service)

