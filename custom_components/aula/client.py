"""Aula client"""
import logging
import requests
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from urllib.parse import urljoin

_LOGGER = logging.getLogger(__name__)

class Client:
    def __init__(self, selenium, username, password):
        self._selenium = selenium
        self._username = username
        self._password = password        
        self._cookies = {}

    def login(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('whitelisted-ips')
        chrome_options.add_argument('headless')
        chrome_options.add_argument('no-sandbox')

        try:
            # Check selenuim connection
            r = requests.get(urljoin(self._selenium, 'wd/hub/status'))
            r.raise_for_status()

            with webdriver.Remote(command_executor=urljoin(self._selenium, 'wd/hub'), desired_capabilities=DesiredCapabilities.CHROME, options=chrome_options) as driver:
                
                driver.implicitly_wait(5)
                driver.get("https://aula.dk")
                
                driver.find_element_by_css_selector(".uni-login").click()
                driver.find_element_by_id("username").send_keys(self._username + Keys.RETURN)
                driver.find_element_by_css_selector("[type=password]").send_keys(self._password)
                driver.find_element_by_css_selector("[type=submit]").click()

                time.sleep(5) #TODO: Wait for page/cookie instead
                _LOGGER.debug("Login complete")

                self._cookies = driver.get_cookies()
                driver.close()
        except WebDriverException:
            _LOGGER.error('Webdriver error')
        except requests.exceptions.HTTPError as errh:
            _LOGGER.error('Sellenuim http error: %s', errh)
        except requests.exceptions.ConnectionError as errc:
            _LOGGER.error('Sellenuim error connecting: %s', errc)
        except requests.exceptions.Timeout as errt:
            _LOGGER.error("Sellenuim timeout error: %s", errt)
        except requests.exceptions.RequestException as err:
            _LOGGER.error("OOps: error: %s", err)

    def update_data(self):
        _LOGGER.debug("UPDATE DATA")

        s = requests.Session()
        for cookie in self._cookies:
            s.cookies.set(cookie['name'], cookie['value'])       
        
        is_logged_in = requests.get("https://www.aula.dk/api/v11/?method=profiles.getProfilesByLogin", cookies=s.cookies).json()["status"]["message"] == "OK"
        _LOGGER.debug("is_logged_ind? " + str(is_logged_in))
        

        if not is_logged_in:
            self.login()
            for cookie in self._cookies:
                s.cookies.set(cookie['name'], cookie['value'])

        self._daily_overview = []
        self._week_plan = []
        self._profiles = requests.get("https://www.aula.dk/api/v11/?method=profiles.getProfilesByLogin", cookies=s.cookies).json()["data"]["profiles"]
        
        self._children = []
        for profile in self._profiles:
            for child in profile["children"]:
                self._children.append(child)

        for i, child in enumerate(self._children):       
            self._daily_overview.append(requests.get("https://www.aula.dk/api/v11/?method=presence.getDailyOverview&childIds[]=" + str(child["id"]), cookies=s.cookies).json()["data"][0])

        #TODO: Week plan
        #total_weeks = 4
        #now = datetime.datetime.now()
        #from_date = (now - datetime.timedelta(days = (now).weekday())).strftime("%Y-%m-%d")
        #to_date = (now + datetime.timedelta(days = (7 * total_weeks) - (now).weekday())).strftime("%Y-%m-%d")
        #week_plan = requests.get("https://www.aula.dk/api/v11/?method=presence.getPresenceTemplates&filterInstitutionProfileIds[]=" + str(child_id) + "&fromDate=" + from_date + "&toDate=" + to_date, cookies=s.cookies).json()#["data"]["presenceWeekTemplates"][0]

                

        return True