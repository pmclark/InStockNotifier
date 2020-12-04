import json
import platform
import random
import sys
import webbrowser
from datetime import datetime
from os import getenv, system
from pprint import pprint
from time import sleep
from urllib.request import Request, urlopen

import requests
from dotenv import load_dotenv
from selenium import webdriver

platform = platform.system()
PLT_WIN = "Windows"
PLT_LIN = "Linux"
PLT_MAC = "Darwin"

# Set up environment variables and constants. Do not modify this unless you know what you are doing!
load_dotenv()
USE_DISCORD_HOOK = False
DISCORD_WEBHOOK_URL = getenv('DISCORD_WEBHOOK_URL')
ALERT_DELAY = int(getenv('ALERT_DELAY'))
MIN_DELAY = int(getenv('MIN_DELAY'))
MAX_DELAY = int(getenv('MAX_DELAY'))
OPEN_WEB_BROWSER = getenv('OPEN_WEB_BROWSER') == 'true'

with open('sites.json', 'r') as f:
    sites = json.load(f)

# Discord Setup
if DISCORD_WEBHOOK_URL:
    USE_DISCORD_HOOK = True
    print('Enabled Discord Web Hook.')

# Platform specific settings
print("Running on {}".format(platform))
if platform == PLT_WIN:
    from win10toast import ToastNotifier
    toast = ToastNotifier()


def alert(site):
    product = site.get('name')
    print("{} IN STOCK".format(product))
    print(site.get('url'))
    if OPEN_WEB_BROWSER:
        webbrowser.open(site.get('url'), new=1)
    os_notification("{} IN STOCK".format(product), site.get('url'))
    discord_notification(product, site.get('url'))
    sleep(ALERT_DELAY)


def os_notification(title, text):
    if platform == PLT_MAC:
        system("""
                  osascript -e 'display notification "{}" with title "{}"'
                  """.format(text, title))
        system('afplay /System/Library/Sounds/Glass.aiff')
        system('say "{}"'.format(title))
    elif platform == PLT_WIN:
        toast.show_toast(title, text, duration=5)
    elif platform == PLT_LIN:
        # Feel free to add something here :)
        pass

def discord_notification(product, url):
    if USE_DISCORD_HOOK:
        data = {
            "content": "{} in stock at {}".format(product, url),
            "username": "In Stock Alert!"
        }
        result = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(data), headers={"Content-Type": "application/json"})
        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))

def requests_library(url):
    headers = {
        'Host': 'www.bestbuy.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    response = requests.get(url, headers=headers, timeout=30)
    html = response.text
    return html

def urllib_get(url):
    # for regular sites
    # Fake a Firefox client
    request = Request(url)
    # request.add_header('User-Agent', 'Mozilla/5.0')
    request.add_header('Host', 'www.bestbuy.com')
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0')
    request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    request.add_header('Accept-Language', 'en-US,en;q=0.5')
    request.add_header('Accept-Encoding', 'gzip, deflate, br')
    request.add_header('Connection', 'keep-alive')
    request.add_header('Upgrade-Insecure-Requests', '1')
    page = urlopen(request, timeout=30)
    pprint(page.info())
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    #if platform == PLT_LIN:
        # Nov 30, 2020 Status:
        # I was having issues connecting to some sites (such as Micro Center) because I think
        # the website can tell it isn't an actual user connecting through a web browser. This might involve changing the
        # headers in the request, similar to what is being done in commented line 85. The best way to figure out what
        # headers to add might be to try and echo what the chrome browser is sending vs what is being sent by
        # the request using the urllib library (line 85) or what is being done by the headless selenium chrome
        # webdriver on line 103. I'm also not sure if selenium allows you to add headers.
        #
        # I think trying to run in headless mode using the chrome web driver either adds or removes header(s) that other
        # sites see as a non-legitimate browser. I *think* running the chrome web driver without the "--headless"
        # argument might be causing the box to run out of memory. Running without "--headless" using the windows
        # chromedriver works fine with Micro Center's website (not sure about Best Buy). One way to see if this is an
        # issue might be to either run a virtual linux machine on my PC or try running the linux chromedriver on my
        # raspberry pi(which might have more memory than the EC2 box but not sure).
        # chromeOptions = webdriver.ChromeOptions()
        # chromeOptions.add_argument("start-maximized")
        # chromeOptions.add_argument("disable-infobars")
        # chromeOptions.add_argument("--disable-extensions")
        # chromeOptions.add_argument("--disable-gpu")
        # chromeOptions.add_argument("--disable-dev-shm-usage")
        # chromeOptions.add_argument("--no-sandbox")
        # chromeOptions.add_argument("--headless")
        # chromeOptions.add_argument("--remote-debugging-port=9222")
        # driver = webdriver.Chrome(executable_path='/home/ubuntu/git/InStockNotifier/chromedriver',
        #                           options=chromeOptions)
        # driver.get(url)
        # html = driver.page_source
        # driver.close()
    return html
    # else:
    #     return ""


def is_test():
    try:
        if sys.argv[1] == 'test':
            alert(sites[2])
            print("Test complete, if you received notification, you're good to go.")
            return True
    except:
        return False


def main():
    search_count = 0

    exit() if is_test() else False

    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Starting search {} at {}".format(search_count, current_time))
        search_count += 1
        for site in sites:
            if site.get('enabled'):
                print("\tChecking {}...".format(site.get('name')))

                try:
                    # html = urllib_get(site.get('url'))
                    html = requests_library(site.get('url'))

                except Exception as e:
                    print("\t\tConnection failed...")
                    print("\t\t{}".format(e))
                    continue
                keyword = site.get('keyword')
                alert_on_found = site.get('alert')
                index = html.upper().find(keyword.upper())
                if alert_on_found and index != -1:
                    alert(site)
                elif not alert_on_found and index == -1:
                    alert(site)

                base_sleep = 1
                total_sleep = base_sleep + random.uniform(MIN_DELAY, MAX_DELAY)
                sleep(total_sleep)


if __name__ == '__main__':
    main()
