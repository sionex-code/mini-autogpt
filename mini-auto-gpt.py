
if __name__ == '__main__':  
    from ast import Break
    from lib2to3.pgen2.token import NEWLINE
    import undetected_chromedriver.v2 as uc
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    import json
    import os
    from tkinter import Tk
    import time
    import core
    import psutil
    import re
    import hashlib
    import pandas as pd
    import urllib.parse
   # import translators as ts
    #import translators.server as tss
    import html
    from html.parser import HTMLParser
    import requests
    import random
    import bs4 as bs

    def get_chat_response(query):
            try:
                url = "http://{add your server address}/chat"
                form_data = {"q": query}
                response = requests.post(url, data=form_data)

                return response.text
            except:
                return "pp:"
            

    main_prompt = """ Your decisions must always be made independently without seeking user assistance. Play to your strengths as an LLM and pursue simple strategies with no legal complications.

    GOALS:
    1. Find the bitcoin current price and what analyist think what will bitcoin do in may 2023 and what will be the price of bitcoin in may 2023

    Constraints:
    1. No user assistance
    2. Exclusively use the commands listed in double quotes e.g. "command name"

    Commands:
    1. Google Search: "google", args: "input": "<search>"
    2. Browse Website: "browse_website", args: "url": "<url>", "question": "<what_you_want_to_find_on_website>"
    3. Task Complete (Shutdown): "task_complete", args: "reason": "<reason>"
  

    Important Rules: 
    1. do not repeat json 
    2. do not output extra text outside json
    3. your output is only limited to json

    You should only respond in JSON format as described below
    Response Format: 
    {
        "thoughts": {
            "text": "thought",
            "speak": "thoughts summary to say to user",
        },
        "command": {"name": "command name", "args": {"arg name": "value"}},
    }
    """


    options = uc.ChromeOptions()
    options.user_data_dir = "c:\\temp\\profile"
    driver = uc.Chrome(options=options,use_subprocess=False)

    def google_search(query):
        driver.get('https://www.google.com/search?q='+query)
        # get the source of the page
        html = driver.page_source
        # parse the html using beautiful soup and store in variable `soup`
        soup = bs.BeautifulSoup(html, 'html.parser')
        # get all the links 
        links = soup.find_all('a')

        # get the href attribute of all the links
        links = [link.get('href') for link in links]

        # filter out None values and links containing 'google.com' or 'youtube.com' also remove link if length is less than 5 or if it doesn't start with http
        links = [link for link in links if link is not None and 'google.com' not in link and 'youtube.com' not in link and len(link) > 5 and link.startswith('http')]

        # remove the duplicate links
        links = list(set(links))

        # get only first 12 links   
        links = links[:12]

        return links

    def browse_website(url):
        driver.get(url)
        # get the source of the page
        html = driver.page_source
        # parse the html using beautiful soup and store in variable `soup`
        soup = bs.BeautifulSoup(html, 'html.parser')

        # get the domain name of the url without protocol
        domain = urllib.parse.urlparse(url).netloc

        # get all the links except the links containing domain name and youtube, facebook, twitter, instagram and also it should not be None
        links = soup.find_all('a')

        links = list({link.get('href') for link in links if link.get('href') is not None and domain not in link.get('href') and all(social_site not in link.get('href') for social_site in ['youtube.com', 'facebook.com', 'twitter.com', 'instagram.com']) and len(link.get('href')) >= 5})[:15]

     

        # get all the paragraphs and list text from url via beautiful soup

        paragraphs = soup.find_all('p')
        paragraphs = [paragraph.text for paragraph in paragraphs]

        # if paragraph len is greater than 700 characters then trim it to 700 characters
        paragraphs = [paragraph for paragraph in paragraphs]

        
        # get all the ul li text from url via beautiful soup

        ul_li = soup.find_all('li')
        ul_li = [li.text for li in ul_li]

        # remove ul li text if length is less than 5 
        ul_li = [li for li in ul_li if len(li) > 5]

        # make ul li a string 

        ul_li = " ".join(ul_li)
        
        # make links a string

        links = " ".join(links)

        # now combine the paragraphs and ul_li 

        paragraphs = " ".join(paragraphs)

        # TRIM paragraphs to 700 characters

        paragraphs = paragraphs[:700]

        text = paragraphs + " [some list items]=  " + ul_li + "[Links from this page]= " + links

        return text
        
        
    def extract_json_with_command(long_string):
        json_pattern = r'\{.*?\}'
        json_strings = re.findall(json_pattern, long_string, re.DOTALL)

        valid_jsons = []
        for json_str in json_strings:
            try:
                data = json.loads(json_str)
                if 'command' in data and data['command']:
                    valid_jsons.append(data)
            except json.JSONDecodeError:
                continue

        return valid_jsons if valid_jsons else False
    def process_json(json_data):
        # Load the JSON data
        data = json.loads(json_data)

        # Access the values
        thoughts_text = data["thoughts"]["text"]
        #thoughts_reasoning = data["thoughts"]["reasoning"]
       # thoughts_plan = data["thoughts"]["plan"]
        #thoughts_criticism = data["thoughts"]["criticism"]
        thoughts_speak = data["thoughts"]["speak"]
        command_name = data["command"]["name"]
       
        command_args = data["command"]["args"]

        arg_name_value = data["command"]["args"]
        
        # return all values as a tuple
        return (thoughts_text, thoughts_speak, command_name, command_args, arg_name_value)

    def send_get_request(url):
                response = requests.get(url)
                
                if response.status_code == 200:
                    print("GET request successful")
                else:
                    print(f"GET request failed with status code {response.status_code}")

    def command_processor(command,command_args): 
        if (str(command) == 'google'):  
            all_links = google_search(command_args['input'])
                # concatinate links by new line and make it string
            links = '\n'.join([str(link) for link in all_links])

            return "Here is google search result links what to do next?: " + links
        if (str(command) == 'browse_website'):
            result_data = browse_website(command_args['url'])
            return "after browsing the webiste i found the following text and descriptions and links: " + result_data


    def start_small_auto_gpt():
        send_get_request("http://{add your server address}/reset") # reset the chatbot 
        goal = "Write a detailed 2000 words review on latest gaming keyboard amazon, read reviews product details and write it like human and write the post to a file"
        # replace goal in main prompt with goal 
        curprompt = main_prompt.replace("[goal]", goal)
        # remove new lines from curprompt 

        result = get_chat_response(curprompt)

        # verify if the result is valid json
        valid = False
        try:
            json.loads(result)
            valid = True
        except:
            while True:
                extra = ""
                result = get_chat_response(extra + " only output a proper json only, do not add any extra text")
                try:
                    json.loads(result)
                    valid = True
                    break
                except:
                    start_small_auto_gpt() # reset and try again
                    pass 

        # just in case 

        if valid: 
            thoughts_text, thoughts_speak, command_name, command_args, arg_name_value = process_json(result)

           
            while True: 
                next_command = command_processor(command_name,command_args)
                # if next_command contains <!doctype html> 
                while "<!doctype html>" in next_command:
                    next_command = command_processor(command_name,command_args)
                    time.sleep(10)

               

                thoughts_text, thoughts_speak, command_name, command_args, arg_name_value = process_json(get_chat_response(next_command))
                time.sleep(2)
        
    start_small_auto_gpt()            
               
