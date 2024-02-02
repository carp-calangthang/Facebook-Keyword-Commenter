import os
import re
import time
import json
import urllib.parse
from colorama import Fore, Style
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

def login_and_find_posts(keyword, totalposts):
    
    print("---------------------------------------------------")
    print("Đợi tìm các bài viết mới...")
    print("---------------------------------------------------")
        
    script_path = os.path.abspath(__file__) 
    src_directory = os.path.dirname(script_path)
    url_file_path = os.path.join(src_directory, '..', 'data', 'urls.txt')
    cookies_file_path = os.path.join(src_directory, '..', 'data', 'cookies.txt')
    cookies_path = os.path.abspath(cookies_file_path)
    
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    options.add_argument("--disable-notifications");
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.facebook.com")
    
    with open(cookies_path, "r") as cookie_file:
        raw = cookie_file.readlines()
        
        for cookie in raw:
            login_cookie = cookie.strip()
            cookie_pairs = login_cookie.strip().split("; ")
            for cookie in cookie_pairs:
                key, value = cookie.split("=", 1)
                driver.add_cookie({"name": key, "value": value, "domain": ".facebook.com"})
    
    driver.get(f"https://www.facebook.com/search/posts?q={keyword}&filters=eyJycF9jcmVhdGlvbl90aW1lOjAiOiJ7XCJuYW1lXCI6XCJjcmVhdGlvbl90aW1lXCIsXCJhcmdzXCI6XCJ7XFxcInN0YXJ0X3llYXJcXFwiOlxcXCIyMDI0XFxcIixcXFwic3RhcnRfbW9udGhcXFwiOlxcXCIyMDI0LTFcXFwiLFxcXCJlbmRfeWVhclxcXCI6XFxcIjIwMjRcXFwiLFxcXCJlbmRfbW9udGhcXFwiOlxcXCIyMDI0LTEyXFxcIixcXFwic3RhcnRfZGF5XFxcIjpcXFwiMjAyNC0xLTFcXFwiLFxcXCJlbmRfZGF5XFxcIjpcXFwiMjAyNC0xMi0zMVxcXCJ9XCJ9IiwicmVjZW50X3Bvc3RzOjAiOiJ7XCJuYW1lXCI6XCJyZWNlbnRfcG9zdHNcIixcImFyZ3NcIjpcIlwifSJ9")
    time.sleep(1)
    driver.get(f"https://www.facebook.com/search/posts?q={keyword}&filters=eyJycF9jcmVhdGlvbl90aW1lOjAiOiJ7XCJuYW1lXCI6XCJjcmVhdGlvbl90aW1lXCIsXCJhcmdzXCI6XCJ7XFxcInN0YXJ0X3llYXJcXFwiOlxcXCIyMDI0XFxcIixcXFwic3RhcnRfbW9udGhcXFwiOlxcXCIyMDI0LTFcXFwiLFxcXCJlbmRfeWVhclxcXCI6XFxcIjIwMjRcXFwiLFxcXCJlbmRfbW9udGhcXFwiOlxcXCIyMDI0LTEyXFxcIixcXFwic3RhcnRfZGF5XFxcIjpcXFwiMjAyNC0xLTFcXFwiLFxcXCJlbmRfZGF5XFxcIjpcXFwiMjAyNC0xMi0zMVxcXCJ9XCJ9In0%3D")
    raw_url = []
    url_list = []

    while len(raw_url) < totalposts:
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        links = driver.find_elements(By.CSS_SELECTOR, "a")
        
        for link in links:
            url = link.get_attribute("href")
            if url is not None and "photo/?fbid" in url:
                raw_url.append(url)
                for mbasic_url in raw_url:
                    final_url = re.sub(r'www\.facebook\.com', 'mbasic.facebook.com', mbasic_url)
                    url_list.append(final_url)

        with open(url_file_path, 'r') as file:
            checked_fbid_values = [re.search(r'fbid=(\d+)', line.strip()).group(1) for line in file if re.search(r'fbid=(\d+)', line.strip())]
            checked_set_a_values = [re.search(r'set=a\.(\d+)', line.strip()).group(1) for line in file if re.search(r'set=a\.(\d+)', line.strip())]
            checked_set_pcb_values = [re.search(r'set=a\.(\d+)', line.strip()).group(1) for line in file if re.search(r'set=pcb\.(\d+)', line.strip())]
            checked_urls = [line.strip() for line in file]
            
        check_new_urls = []
        
        for url in url_list:
            fbid_match = re.search(r'fbid=(\d+)', url)
            set_a_match = re.search(r'set=a\.(\d+)', url)
            set_pcb_match = re.search(r'set=pcb\.(\d+)', url)

            if fbid_match:
                fbid_value = fbid_match.group(1)
                if fbid_value not in checked_fbid_values:
                    if set_a_match:
                        set_a_value = set_a_match.group(1)
                        if set_a_value not in checked_set_a_values:
                            if url not in checked_urls:
                                check_new_urls.append(url)
                                checked_fbid_values.append(fbid_value)
                                checked_set_a_values.append(set_a_value)
                                checked_urls.append(url)
                                
                elif set_pcb_match:
                    set_pcb_value = set_pcb_match.group(1)
                    if set_pcb_value not in checked_set_pcb_values:
                        if url not in checked_urls:
                            driver.get(url)
                            post_links = driver.find_elements(By.CSS_SELECTOR, "a[href]")
                            for post_link in post_links:
                                get_post = post_link.get_attribute("href")
                                if "story.php?story" in get_post:
                                    check_new_urls.append(get_post)
                                    checked_fbid_values.append(fbid_value)
                                    checked_set_pcb_values.append(set_pcb_value)
                                    checked_urls.append(get_post)
                                    print(get_post)
        
        if check_new_urls:
            with open(url_file_path, 'a') as file:
                for new_url in check_new_urls:
                    file.write(new_url + '\n')

            print("Quạc quạc quạc quạc quạc 🐧!")
        else:
            print("Gâu gâu gâu gâu gâu 🐕!")
            
    print("---------------------------------------------------")
    print("Đã chuyển đổi theo yêu cầu...")
    print("Bắt đầu seeding...")
    print("---------------------------------------------------")
           
    time.sleep(5)
    
    driver.close()
    
    print(Style.RESET_ALL)