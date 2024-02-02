import os
import re
import time
import json
import urllib.parse
from selenium import webdriver
from colorama import Fore, Style
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
    urls_path = os.path.abspath(url_file_path)
    
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    options.add_argument("--disable-notifications");
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.facebook.com")
    
    with open('./data/cookies.txt', "r") as cookie_file:
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
    id_list = []

    while len(raw_url) < totalposts:
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        links = driver.find_elements(By.CSS_SELECTOR, "a")
        
        for link in links:
            url = link.get_attribute("href")
            if url is not None and "photo/?fbid" in url:
                raw_url.append(url)

        for check_url in raw_url:
            pcb_start = check_url.find("pcb.")
            a_start = check_url.find("a.")
            cft_end = check_url.find("__cft")       

            if pcb_start == -1 and a_start == -1 or cft_end == -1:
                continue

            set_start = pcb_start if pcb_start != -1 else a_start
            fbid = check_url[set_start + 4:cft_end]

            if fbid not in url_list:
                id_list.append(fbid)
                url_parts = urllib.parse.urlsplit(check_url)
                final_url = url_parts._replace(netloc="mbasic.facebook.com").geturl()
                url_list.append(final_url)
                
            a_urls = []
            pcb_urls = []
            for match_url in url_list:
                if "&set=a." in match_url:
                    a_urls.append(match_url)
                elif "&set=pcb." in match_url:
                    pcb_urls.append(match_url)
                    
    with open(urls_path, 'a') as url_file:
        for a_match_url in a_urls:
            print(a_match_url + '\n')
            url_file.writelines(a_match_url + '\n')  
        
        unique_ids = set()
        set_post = []
        for pbc_match_url in pcb_urls:            
            driver.get(pbc_match_url)
            post_links = driver.find_elements(By.CSS_SELECTOR, "a[href]")
            for post_link in post_links:
                get_post = post_link.get_attribute("href")
                if "story.php?story" in get_post:
                    set_post.append(get_post)
                    for handle_url in set_post:
                        id_start = handle_url.find("&id=")
                        id_end = handle_url.find("&", id_start + 1)
                        extracted_id = handle_url[id_start:id_end]                        
                        if id_start != -1 and id_end != -1 and extracted_id not in unique_ids:
                            unique_ids.add(extracted_id)
                            url_file.writelines(handle_url + '\n')
            
    print("---------------------------------------------------")
    print("Đã chuyển đổi theo yêu cầu...")
    print("Bắt đầu seeding...")
    print("---------------------------------------------------")
           
    time.sleep(5)
    
    driver.close()
    
    print(Style.RESET_ALL)