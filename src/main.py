import urllib.request
import time
import requests
import os
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv('.env')

# Telegram Bot Token and Chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')  # Replace with your Telegram group chat ID

def send_msg(text):
    if os.getenv('DEBUG_MODE')!=1: # messages wont be sent to your telegram bot if you are not using debug mode
        token = TELEGRAM_BOT_TOKEN
        chat_id = CHAT_ID
        url_req = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"

        # Make the request to the Telegram API
        response = requests.get(url_req)
    
        # Check for success
        if response.status_code == 200:
            print("Message sent successfully")
        else:
            print(f"Failed to send message: {response.status_code}, {response.reason}")


def check_websites(websites, max_attempts=3, retry_interval=5, retry_delay=60, status_report_interval=600):
    unreachable_websites = {}
    accessible_websites = set()
    last_report_time = time.time()
    #instantiate log logic
    if os.getenv('LOG')==1: #checks if logging is enabled
        old_stdout = sys.stdout
        log_file = open("message.log","w")
        sys.stdout = log_file

    while True:
        for website in websites[:]:
            attempts = unreachable_websites.get(website, 0)
            if attempts >= max_attempts:
                print(f"Failed to reach the server: {website} after {attempts} attempts")
                send_msg(f"Failed to reach the server: {website} after {attempts} attempts")
                websites.remove(website)
                continue

            try:
                response = urllib.request.urlopen(website)
                print(f"{website} is accessible, status code: {response.getcode()}")
                if website in unreachable_websites:
                    del unreachable_websites[website]
                accessible_websites.add(website)
            except urllib.error.URLError as e:
                print(f"Attempt {attempts + 1} for {website} failed: {e.reason}")
                unreachable_websites[website] = attempts + 1
                if website in accessible_websites:
                    accessible_websites.remove(website)
            except Exception as e:
                print(f"An error occurred with {website}: {e}")
                if website in accessible_websites:
                    accessible_websites.remove(website)

            time.sleep(retry_interval)

        current_time = time.time()
        if current_time - last_report_time >= status_report_interval:
            print(f"Status report at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}:")
            send_msg(f"Status report at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}:")
            print("Accessible websites:")
            send_msg("Accessible websites:")
            for site in accessible_websites:
                print(f" - {site}")
                send_msg(f" - {site}")
            print("Inacessible websites:")
            send_msg("Inacessible websites:")
            for site in unreachable_websites:
                print(f" - {site}")
                send_msg(f" - {site}")
            last_report_time = current_time

        if not websites:
            print("No websites left to check. Moving to retry loop for unreachable websites.")
            while unreachable_websites:
                for website, attempts in list(unreachable_websites.items()):
                    try:
                        response = urllib.request.urlopen(website)
                        print(f"{website} is now accessible, status code: {response.getcode()}")
                        send_msg(f"{website} is now accessible, status code: {response.getcode()}")
                        del unreachable_websites[website]
                        websites.append(website)
                        accessible_websites.add(website)
                    except urllib.error.URLError as e:
                        print(f"Retry for {website} failed: {e.reason}")
                    except Exception as e:
                        print(f"An error occurred with {website}: {e}")

                    time.sleep(retry_delay)

                current_time = time.time()
                if current_time - last_report_time >= status_report_interval:
                    print(f"Status report at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}:")
                    print("Accessible websites:")
                    for site in accessible_websites:
                        print(f" - {site}")
                    last_report_time = current_time

                if not unreachable_websites:
                    print("All previously unreachable websites are now accessible.")
                    break

        else:
            print("Continuing to check the remaining websites.")

# List of websites to check
websites_to_check =os.getenv('WEBSITES_TO_CHECK').split(',')

# Run the check
check_websites(websites_to_check)
