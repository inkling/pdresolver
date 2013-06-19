#
#  service.py
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
log = logging.getLogger(__name__)

class Service(object):
    """The superclass of all pdresolver services.
    Subclasses must implement the "incident_is_occurring" method.
    """
    def __init__(self, keys):
        self.keys = keys

    def incident_is_occurring(self, pd_incident):
        """Takes in pd_incident (dict) and returns True if the phenomenon that
        caused that incident to occur is still occurring.
        """
        raise NotImplementedError()
