import argparse
import getpass
import json
import netrc
import os
import platform
import re
import requests
import shutil
import sys
import tarfile
import time
from bs4 import BeautifulSoup

#from sqlalchemy.exc import DBAPIError
#from .models import (
#    DBSession,
#    MyModel,
#    )

class CourseraApi(object):
    """
    Class to download content (videos, lecture notes, ...) from coursera.org for
    use offline.

    https://github.com/dgorissen/coursera-dl
    """

    BASE_URL =    'http://class.coursera.org/%s'
    LOGIN_URL =   'https://accounts.coursera.org/api/v1/login'
    TIMEOUT = 60

    DEFAULT_PARSER = "lxml"

    def __init__(self,username,password):
        """Requires your coursera username and password.
        You can also specify the parser to use (defaults to lxml), see http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser
        """
        self.username = username
        self.password = password
        self.logged_in = False
        self.session = requests.Session()

    def login(self):
        url = 'https://class.coursera.org/crypto-2012-003/lecture/4'
        res = self.session.get(url, timeout=self.TIMEOUT)
        res.close()

        # get the csrf token
        if 'csrf_token' not in self.session.cookies:
            raise Exception("Failed to find csrf cookie")

        # call the authenticator url
        LOGIN_FORM = {'email': self.username, 'password': self.password}
        self.session.headers['Referer'] = 'https://www.coursera.org'
        self.session.headers['X-CSRFToken'] = self.session.cookies.get('csrf_token')
        self.session.cookies['csrftoken'] = self.session.cookies.get('csrf_token')

        res = self.session.post(self.LOGIN_URL, data=LOGIN_FORM, timeout=self.TIMEOUT)
        if res.status_code == 401:
            raise Exception("Invalid username or password")
        res.close()

        # check if we managed to login
        if 'CAUTH' not in self.session.cookies:
            raise Exception("Failed to authenticate as %s" % self.username)

        self.logged_in = True

    def listing(self):
        r = self.session.get('https://www.coursera.org/maestro/api/topic/list2')
        return r.json()

    def listingCombined(self):
        if not self.logged_in:
            self.login()

        r = self.session.get('https://www.coursera.org/maestro/api/topic/list2_combined')
        return r.json()