import os
import time
import random
from colorama import Fore, Style
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

def open_browser_with_cookie(cookies_value, proccess_name, wait_time, wait_find_post):
    
    script_path = os.path.abspath(__file__) 
    src_directory = os.path.dirname(script_path)
    used_file_path = os.path.join(src_directory, '..', 'data', 'used_urls.txt')
    urls_file_path = os.path.join(src_directory, '..', 'data', 'urls.txt')
    content_file_path = os.path.join(src_directory, '..',  'data', 'comment.txt')
    used_path = os.path.abspath(used_file_path)
    content_path = os.path.abspath(content_file_path)
    images_file_path = os.path.join(src_directory, '..',  'data', 'images')
    images_path = os.path.abspath(images_file_path)
    
    with open(content_path, 'r', encoding='utf-8') as content_file:
        comment_content = content_file.readline()
        
    image_files = [f for f in os.listdir(images_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--disable-notifications");
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get('https://mbasic.facebook.com/')
    
    cookie_string = cookies_value
    
    cookie_pairs = cookie_string.strip().split("; ")
    for cookie in cookie_pairs:
        key, value = cookie.split("=", 1)
        driver.add_cookie({"name": key, "value": value, "domain": ".facebook.com"})
    
    driver.refresh()
    
    used_urls = set()

    with open(used_path, 'a+') as used_file:
        used_urls.update(line.strip() for line in used_file)

        with open(urls_file_path, 'r') as file:
            urls = file.readlines()

            for url in urls:
                start_fbid = url.find("fbid=") + len("fbid=")
                end_fbid = url.find("&", start_fbid)
                id_fbid = url[start_fbid:end_fbid] if end_fbid != -1 else url[start_fbid:]

                id_set = None

                if "set=pcb" in url:
                    start_set = url.find("set=pcb.") + len("set=pcb.")
                    end_set = url.find("&", start_set)
                    id_set = url[start_set:end_set] if end_set != -1 else url[start_set:]
                elif "set=a" in url:
                    start_set = url.find("set=a.") + len("set=a.")
                    end_set = url.find("&", start_set)
                    id_set = url[start_set:end_set] if end_set != -1 else url[start_set:]

                if id_fbid in used_urls or (id_set is not None and id_set in used_urls):
                    continue

                if id_set is not None:
                    used_urls.add(id_set)

                used_urls.add(id_fbid)

                with open(used_path, 'r') as check_url_file:
                    check_urls = check_url_file.readlines()
                    
                    if url not in check_urls:
                        used_file.write(url.strip() + '\n')
            
                driver.get(url)
                time.sleep(2)
                
                try:
                    cookie_die = driver.find_element(By.XPATH, "//*[contains(text(), 'You must log in first.')]")
                    print(Fore.CYAN + f"{proccess_name}:" + Fore.GREEN + "The account has been locked!")
                    print('----------------------------------------------------------------')
                    break
                except:
                    pass
                
                try:
                    error_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Trang bạn yêu cầu không thể hiển thị ngay bây giờ')]")
                    time.sleep(5)
                    continue
                except:
                    pass
                
                try:
                    comment_block = driver.find_element(By.XPATH, "//div[contains(text(), 'To protect the community from spam, we limit the number of comments')]")
                    print(Fore.CYAN + f"{proccess_name}:" + Fore.GREEN + " Commenting is blocked!")
                    print('----------------------------------------------------------------')
                    break
                except:
                    pass
                
                try:
                    comment_box = driver.find_element(By.NAME, 'view_photo')
                    comment_box.click()
                    time.sleep(2)
                    if not image_files:
                        print(Fore.CYAN + f"{proccess_name}:" + Fore.RED + "There are no images in the folder!")
                        comment_textarea = driver.find_element(By.NAME, 'comment_text')
                        comment_textarea.send_keys(comment_content)
                    else:
                        image_input = driver.find_element(By.NAME, 'photo')
                        comment_textarea = driver.find_element(By.NAME, 'comment_text')
                        for image_file in image_files:
                            image_file_path = os.path.join(images_path, image_file)
                            comment_textarea.send_keys(comment_content)
                            image_input.send_keys(image_file_path)
                            
                    time.sleep(2)
                except:
                    continue
                    
                try:
                    comment_button = driver.find_element(By.XPATH, '//input[@value="Bình luận"]').click()
                    print(Fore.CYAN + f"{proccess_name}:" + Fore.GREEN + f" Comment has been posted on the post: {url}")
                    print('----------------------------------------------------------------')
                    time.sleep(2)
                except:
                    comment_button = driver.find_element(By.XPATH, '//input[@value="Comment"]').click()
                    print(Fore.CYAN + f"{proccess_name}:" + Fore.GREEN + f" Comment has been posted on the post: {url}")
                    print('----------------------------------------------')
                    time.sleep(2)
                                        
                try:
                    block_account = driver.find_element(By.XPATH, "//h2[text()='You have been blocked']")
                    print(Fore.CYAN + f"{proccess_name}:" + Fore.GREEN + " Commenting is blocked!")
                    print('----------------------------------------------------------------')
                    break
                except:
                    pass
                    
                time.sleep(wait_time)
        
    time.sleep(5)
    
    with open(urls_file_path, 'r+') as url_file:
        content = url_file.read()
        url_file.seek(0)
        url_file.truncate()
    
    print(Fore.CYAN + f"{proccess_name}:" + Fore.GREEN + " Close the program!")
    print('-----------------------------------------------------------------')

    driver.quit()
    
    print(Fore.CYAN + f"{proccess_name}:" + Fore.GREEN + f" Wait for {wait_find_post} seconds to find new posts....")
    time.sleep(wait_find_post)
