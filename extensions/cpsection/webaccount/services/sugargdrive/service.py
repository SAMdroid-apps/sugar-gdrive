# Copyright (C) 2014, Ignacio Rodriguez <ignacio@sugarlabs.org>
# Thx to Martin Abente Lahaye <martin.abente.lahaye@gmail.com>
# Based on Facebook code
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import os
import logging
import sys
from sugar3 import env

GOOGLE_API = os.path.join(env.get_profile_path(), 'extensions', 'webservice')
sys.path.append(GOOGLE_API)

from gi.repository import Gtk
from gi.repository import WebKit2 as WebKit

from jarabe.webservice import accountsmanager
from cpsection.webaccount.web_service import WebService
from oauth2client.client import OAuth2WebServerFlow


class WebService(WebService):
    CLIENT_ID = "79915831092-oavi9geds5iokcn8c9okeediu92udi94.apps." \
        "googleusercontent.com"
    CLIENT_SECRET = "KfvpSENuGzrafcTFI4iXxj6g"
    REDIRECT_URI = "https://www.sugarlabs.org"
    REDIRECT_TOKEN = "https://www.sugarlabs.org/?code="
    OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
    TOKEN_FILE = os.path.join(env.get_profile_path(), 'gdrive_settings')

    def __init__(self):
        self._account = accountsmanager.get_account('sugargdrive')
        self.authorize_url = None

    def get_icon_name(self):
        return 'computer'

    def config_service_cb(self, widget, event, container):
        wkv = WebKit.WebView()
        url = self._get_auth_url()
        wkv.load_uri(url)
        logging.debug(url)
        wkv.grab_focus()
        wkv.connect('load-changed', self.__load_changed_cb)

        for c in container.get_children():
            container.remove(c)

        scrolled = Gtk.ScrolledWindow()
        scrolled.add(wkv)

        container.add(scrolled)
        container.show_all()

    def _get_auth_url(self):
        self._flow = OAuth2WebServerFlow(self.CLIENT_ID, self.CLIENT_SECRET,
                self.OAUTH_SCOPE, self.REDIRECT_URI)

        self.authorize_url = self._flow.step1_get_authorize_url()
        return self.authorize_url

    def __load_changed_cb(self, view, event):
        uri = view.get_uri()
        if uri is None:
            return

        if uri.startswith(self.REDIRECT_TOKEN):
            token = str(uri[32:]).strip()

            # I have the power.
            credentials = self._flow.step2_exchange(token)
            if os.path.exists(self.TOKEN_FILE):
                os.remove(self.TOKEN_FILE)

            data = credentials.to_json()
            f = open(self.TOKEN_FILE, 'w')
            f.write(data)
            f.close()

def get_service():
    return WebService()
