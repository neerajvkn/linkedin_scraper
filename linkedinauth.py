import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import pickle
import json

def launchBrowser():
    with open('config.json') as config_file:
        conf = json.load(config_file)
    chromedriver = conf['chrome_path']
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options, executable_path=chromedriver)
    return driver
driver = launchBrowser()

def check_if_file_exist_and_delete(filename):
    try:
        os.remove(filename)
    except OSError:
        pass

def login_to_linkedin(username, password):
    cookie_name = f"{username}.pkl"
    check_if_file_exist_and_delete(cookie_name)
    try:
        login_url = 'https://www.linkedin.com/'
        driver.get(login_url)
        driver.implicitly_wait(3)
        username_f = driver.find_element(By.ID, 'session_key')
        pwd_f = driver.find_element(By.ID, 'session_password')
        login_button = driver.find_element(By.XPATH, '//form/button[1]')
        username_f.send_keys(username)
        pwd_f.send_keys(password)
        login_button.click()

        '''
        a wait of 20 sec is added in case a captcha comes and user needs to solve it
        '''
        try:
            driver.implicitly_wait(20)
            '''
            Checks if search box element is there to confirm login, if not it throws an error which is caught by exception.
            '''
            searchbox = driver.find_element(By.ID,("global-nav-typeahead"))
            pickle.dump( driver.get_cookies() , open(cookie_name,"wb"))
            return "Success"
        except Exception as e:
            return "Login Error"

    except Exception as e:
        return e