"""Aula client"""
import logging
import requests
import time
import datetime
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

_LOGGER = logging.getLogger(__name__)

class Client:
    def __init__(self, username, password):
        self._username = username
        self._password = password    
        self._session = None    

    def login(self):
        self._session = requests.Session()
        response = self._session.get('https://login.aula.dk/auth/login.php?type=unilogin')
        
        user_data = { 'username': self._username, 'password': self._password }
        redirects = 0
        success = False
        url = ''
        while success == False and redirects < 10:
            html = BeautifulSoup(response.text, 'lxml')
            url = html.form['action']
            post_data = {}
            for input in html.find_all('input'):
                if(input.has_attr('name') and input.has_attr('value')):
                    post_data[input['name']] = input['value']
                    for key in user_data:
                        if(input.has_attr('name') and input['name'] == key):
                            post_data[key] = user_data[key]


            response = self._session.post(url, data = post_data)
            if response.url == 'https://www.aula.dk:443/portal/':
                success = True
            redirects += 1
        
        self._profiles = self._session.get("https://www.aula.dk/api/v11/?method=profiles.getProfilesByLogin").json()["data"]["profiles"]
        self._session.get("https://www.aula.dk/api/v11/?method=profiles.getProfileContext&portalrole=guardian")
        _LOGGER.debug("LOGIN: " + str(success))

    def update_data(self):
        is_logged_in = False
        if self._session:
            response = self._session.get("https://www.aula.dk/api/v11/?method=profiles.getProfilesByLogin").json()
            is_logged_in = response["status"]["message"] == "OK"
        
        _LOGGER.debug("is_logged_ind? " + str(is_logged_in))
        
        if not is_logged_in:
            self.login()

        self._children = []
        for profile in self._profiles:
            for child in profile["children"]:
                self._children.append(child)
        
        self._daily_overview = {}
        for i, child in enumerate(self._children):      
            response = self._session.get("https://www.aula.dk/api/v11/?method=presence.getDailyOverview&childIds[]=" + str(child["id"])).json()
            if len(response["data"]) > 0:
                self._daily_overview[str(child["id"])] = response["data"][0]

        #TODO: Week plan
        #total_weeks = 4
        #now = datetime.datetime.now()
        #from_date = (now - datetime.timedelta(days = (now).weekday())).strftime("%Y-%m-%d")
        #to_date = (now + datetime.timedelta(days = (7 * total_weeks) - (now).weekday())).strftime("%Y-%m-%d")
        #week_plan = requests.get("https://www.aula.dk/api/v11/?method=presence.getPresenceTemplates&filterInstitutionProfileIds[]=" + str(child_id) + "&fromDate=" + from_date + "&toDate=" + to_date, cookies=s.cookies).json()#["data"]["presenceWeekTemplates"][0]

        return True