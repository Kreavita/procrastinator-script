import os,sys,time
from selenium.webdriver.common.keys import Keys
from selenium import common as sel
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import config

# maybe restrict caught Exceptions: except (sel.exceptions.NoSuchElementException, sel.exceptions.WebDriverException):

def lf_tu(driver):
    try:
        driver.find_element_by_name("j_username").send_keys(config.TUD_USER)
        driver.find_element_by_name("j_password").send_keys(config.TUD_PASS)
        driver.find_element_by_name("_eventId_proceed").click()
        driver.find_element_by_name("_eventId_proceed").click()
        time.sleep(2)
        return True
    except:
        print("login-flow: TU login failed")
        return False

def lf_opal(driver):
    try:
        driver.get("https://bildungsportal.sachsen.de/opal/home/")
        
        driver.find_element_by_id("id13").click()
        driver.find_element_by_xpath("//select[@name='content:container:login:shibAuthForm:wayfselection']/option[text()='TU Dresden']").click()
        driver.find_element_by_name("content:container:login:shibAuthForm:shibLogin").click()

        lf_tu(driver)
        return True
    except:
        print("login-flow: OPAL login failed")
        return False

def lf_bbb(driver):
    lf_tu(driver)

    try: driver.find_element_by_name("username").send_keys(config.NAME)
    except: print("login-flow: BigBlueButton: stream name skipped")
    
    try: driver.find_element_by_class_name("submit_btn").click()
    except: print("login-flow: BigBlueButton: stream name submit skipped")
    
    try:
        driver.find_element_by_class_name("icon-bbb-listen").click()
        return True
    except:
        print("login-flow: BigBlueButton login failed")
        return False   

def lf_zoom(driver):
    try:
        driver.get("https://zoom.us/signin")
        driver.find_element_by_id("email").send_keys(config.ZOOM_EMAIL)
        driver.find_element_by_id("password").send_keys(config.ZOOM_PASS)
        driver.find_element_by_xpath("//div[@class='controls']/div[@class='signin']").click()
        input("login-flow: solve the captcha, then press Enter here")
        #time.sleep(2)
        return True
    except:
        print("login-flow: Zoom login failed")
        return False 

def lf_zoom_mtg(driver):
    try:
        name_in = driver.find_element_by_id("inputname")
        name_in.click()
        
        name_in.send_keys(Keys.CONTROL + "a");
        name_in.send_keys(Keys.DELETE);
        
        name_in.send_keys(config.NAME)
        input("login-flow: solve the captcha, then press Enter here")
        
        try: 
            driver.find_element_by_id("joinBtn").click()
            driver.find_element_by_id("wc_agree1").click()
            still_waiting = 0
        
            while still_waiting in range(0, 20):
                try:
                    driver.find_element_by_xpath("//button[contains(@class, 'zm-btn--lg')]").click()
                    still_waiting = -1
                except:
                    time.sleep(1)
                    still_waiting = still_waiting + 1
        
        except: print("login-flow: Zoom meeting join failed - skipping...")
        
        return True
    except:
        print("login-flow: Zoom Meeting login failed")
        return False 
