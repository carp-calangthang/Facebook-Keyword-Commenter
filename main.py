import os
import json
import random
import subprocess
from colorama import Fore, Style
from multiprocessing import Process
from module.find_comments_v2 import login_and_find_posts
from module.comments import open_browser_with_cookie

os.system("cls")

def get_c_user_from_cookie(cookie):
    start_index = cookie.find("c_user=")
    if start_index != -1:
        end_index = cookie.find(";", start_index)
        if end_index == -1:
            end_index = None
        c_user_value = cookie[start_index + len("c_user="):end_index]
        print(c_user_value)
        return c_user_value
    else:
        return None

def run_login_function_with_cookie(cookie, browser_name, wait_time, wait_find_post):
    
    c_user = get_c_user_from_cookie(cookie)
    if c_user is not None:
        browser_name_with_c_user = f"{browser_name}: {c_user}"
        print(f"{browser_name_with_c_user}" + Fore.GREEN + ": Starting...")
        print('----------------------------------------------------------------')
        open_browser_with_cookie(cookie, browser_name_with_c_user, wait_time, wait_find_post)
    else:
        print(Fore.CYAN + f"{browser_name_with_c_user}" + Fore.GREEN + f"Can't get id of cookie!: {cookie}")

if __name__ == "__main__":

    with open('./data/cookies.txt', "r") as cookie_file:
        cookies = cookie_file.readlines()
        
    browser_name = "User"
    
    processes = []
    
    wait_time = int(input("Enter the waiting time after each comment is posted (Second): "))
    wait_find_post = int(input("Enter the waiting time to find new posts (Second): "))
    print('----------------------------------------------------------------')
    keyword = input("Enter the keyword to search for posts: ")
    totalposts = int(input("Enter the number of posts you want to search for: "))

    while True:
        login_and_find_posts(keyword, totalposts)
        for cookie in cookies:
            login_cookie = cookie.strip()
                        
            process = Process(target=run_login_function_with_cookie, args=(login_cookie, browser_name, wait_time, wait_find_post))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

        with open('./data/cookies.txt', "w") as ck:
            ck.writelines(cookies)
            
        with open('./data/urls.txt', 'w') as urls_file:
            urls_file.writelines("")
