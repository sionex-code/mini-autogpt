import undetected_chromedriver.v2 as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import flask 
from flask import g
import pyperclip
import bs4 as bs 



# process html using beautiful soup 
def process_html(html):
    # create a beautiful soup object
    soup = bs.BeautifulSoup(html, 'html.parser')
    # loop through html tags 
    for tag in soup.find_all():
        # if code tag then get the plain text 
        if tag.name == "code":
            plain_text = tag.get_text() 
        

    return str(soup)


APP = flask.Flask(__name__)
#CORS(APP, origins='http://ask.test') # for local cross origin requests :D 

path = os.path.dirname(os.path.abspath(__file__))
#chrome starting
options = uc.ChromeOptions()
options.user_data_dir = "c:\\temp\\profile"
#options.add_argument("--headless")
#options.add_argument("--disable-extensions")
driver = uc.Chrome(options=options,use_subprocess=True)




def open_chat_gpt():
        url = "https://chat.openai.com/chat"
        driver.get(url)

def get_input_box():
    # with selenium selenium return the textarea elemenent
    input_box = driver.find_element(By.TAG_NAME,"textarea")
    # return the textarea element
    return input_box


def is_logged_in():
    return get_input_box() is not None

def responsez(): 
    while True:
        try:
            time.sleep(1)
            form = driver.find_element(By.CSS_SELECTOR, "form")
            # Wait for the element containing the text "Regenerate Response" to be visible
            button = form.find_element(By.CSS_SELECTOR,"div[class='flex w-full items-center justify-center gap-2']")
            # get button html text
            button_text = button.text
    
            # if button_text to lower is regenerate response then return false 
            if button_text.lower() == "regenerate response":
                    page_elements = driver.find_elements(By.CSS_SELECTOR, "div[class*='markdown']")
                    last_element = page_elements.pop()

                    # return html of last element
                    return process_html(last_element.text)
        except:
            pass 

    #button = driver.find_element(By.CSS_SELECTOR, "textarea ~ button")
    #is_loading = not button.is_enabled()
    #return is_loading

def send_message(message):
    # set message to clipboard 
    pyperclip.copy(message)
    box = get_input_box()
    box.click()

    # send ctrl + v to paste the message
    box.send_keys(Keys.CONTROL, 'v')
    #box.send_keys(message)

    box.send_keys(Keys.ENTER)


def get_last_message():
    pass 

def regenerate_response(driver):
    try_again_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Try again')]")
    if try_again_button is not None:
        try_again_button.click()
    return try_again_button

def get_reset_button(driver):
    reset_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Reset thread')]")
    return reset_button

@APP.route("/chat", methods=["POST"]) # using POST instead of GET
def chat():
    message = flask.request.form.get("q") # using form instead of args to get POST data
    print("Sending message: ", message)
    send_message(message)
    response = responsez()
    print("Response: ", response)
    return response



@APP.route("/regenerate", methods=["GET"])
def regenerate():
    print("Regenerating response")
    if regenerate_response() is None:
        return "No response to regenerate"
    response = get_last_message()
    print("Response: ", response)
    return response

@APP.route("/reset", methods=["GET"])
def reset():
    print("Resetting chat")
    # refresh the page
    driver.get("https://chat.openai.com/chat")
    return "Chat thread reset"

@APP.route("/restart", methods=["GET"])
def restart():
    global driver
    driver.quit()
    driver = uc.Chrome(options=options,use_subprocess=False)
    driver.get("https://chat.openai.com/chat")
    return "API restart!"


def start_browser():
    driver.get("https://chat.openai.com/chat")
    if not is_logged_in():
        print("Please log in to OpenAI Chat")
        print("Press enter when you're done")
        input()
    else:
        print("Logged in")
       
        APP.run(host='localhost', port=5002)

if __name__ == "__main__":
    start_browser()

