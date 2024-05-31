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
    if os.getenv('DEBUG_MODE')!="1": # messages wont be sent to your telegram bot if you are not using debug mode
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


def check_websites(websites, max_attempts=int(os.getenv('max_attempts')), retry_interval=int(os.getenv('retry_interval')), retry_delay=int(os.getenv('retry_delay')), status_report_interval=int(os.getenv('status_report_interval')), maximum_retries=int(os.getenv('maximum_retries')), send_status_report=os.getenv('send_status_report') ): #Status Report Interval 600 is equal to 10 minutes in real life for 1 hour change it to 3600
    attempts_dict_websites = {website: 0 for website in websites}
    accessible_websites = set()
    last_report_time = time.time()
    print(f"attempts dict of websites: {attempts_dict_websites}")
    while True:
        print(f"attempts dict website: {attempts_dict_websites}")
        for website in websites[:]:
            attempts = attempts_dict_websites.get(website, 0)
            if attempts >= max_attempts:
                print(f"Failed to access {website} after {max_attempts} attempts. {websites} will now be considered inacessible")
                send_msg(f"Failed to access {website} after {max_attempts} attempts. {websites} will now be considered inacessible")
                if website in accessible_websites:
                    accessible_websites.remove(website)
                continue

            try:
                response = urllib.request.urlopen(website)
                if response.getcode() ==200:
                    print(f"{website} is accessible, status code: {response.getcode()}")
                    if website in attempts_dict_websites:
                        attempts_dict_websites[website] = 0
                    else :
                        attempts_dict_websites.add()
                    if website not in accessible_websites:
                        accessible_websites.add(website)
            except urllib.error.URLError as e:
                print(f"Attempt {attempts + 1} for {website} failed: {e.reason}")
                attempts_dict_websites[website] = attempts_dict_websites[website] + 1
                if website in accessible_websites and attempts_dict_websites[website] == max_attempts:
                    accessible_websites.remove(website)
                    print(f"Failed to access {website} after {max_attempts} attempts. {websites} will now be considered inacessible")
                    send_msg(f"Failed to access {website} after {max_attempts} attempts. {websites} will now be considered inacessible")
            except Exception as e:
                print(f"An error occurred with {website}: {e}")
                attempts_dict_websites[website] = attempts_dict_websites[website] + 1
                if website in accessible_websites and attempts_dict_websites[website] == max_attempts:
                    accessible_websites.remove(website)
                    print(f"Failed to access {website} after {max_attempts} attempts. {websites} will now be considered inacessible")
                    send_msg(f"Failed to access {website} after {max_attempts} attempts. {websites} will now be considered inacessible")

        time.sleep(retry_interval)

        current_time = time.time()
        if current_time - last_report_time >= status_report_interval and send_status_report=='TRUE':
            print(f"Status report at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}:")
            send_msg(f"Status report at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}:")
            currentAcessibleWebistes=len(accessible_websites)
            currentUnreachablewebsites = sum(1 for attempts in attempts_dict_websites.values() if attempts >= max_attempts)

            print(f"Accessible websites:{currentAcessibleWebistes}")
            send_msg(f"Accessible websites:{currentAcessibleWebistes}")
            for site in accessible_websites:
                print(f" - {site}")
                send_msg(f" - {site}")
            print(f"Inacessible websites:{currentUnreachablewebsites}")
            send_msg(f"Inacessible websites:{currentUnreachablewebsites}")
            for site, attempts in attempts_dict_websites.items():
                if attempts == max_attempts:
                    print(f" - {site}")
                    send_msg(f" - {site}")
            last_report_time = current_time
        # At least one website has surpassed the maximum number of attempts.
        print("No websites left to check. Moving to retry loop for unreachable websites.")
        if any(attempts >= max_attempts for attempts in attempts_dict_websites.values()):
            retries = 0
            while any(attempts >= max_attempts for attempts in attempts_dict_websites.values()):
                retries = retries +1
                for website, attempts in list(attempts_dict_websites.items()):
                    if attempts_dict_websites[website] == max_attempts:
                        try: 
                                response = urllib.request.urlopen(website)
                                print(f"Looks like {website} is now accessible again, status code: {response.getcode()}")
                                send_msg(f"Looks like {website} is now accessible again, status code: {response.getcode()}")
                                attempts_dict_websites[website] = 0
                                accessible_websites.add(website)
                        except urllib.error.URLError as e:
                            print(f"Retry for {website} failed: {e.reason}")
                            send_msg(f"Retry for {website} failed: {e.reason}")
                        except ValueError as e:
                            print(f"Retry for {website} failed due to ValueError: {e}")
                            send_msg(f"Retry for {website} failed due to ValueError: {e}")
                        except Exception as e:
                            print(f"An error occurred with {website}: {e}")
                            send_msg(f"Retry for {website} failed: {e.reason}")
                    time.sleep(retry_delay)
                if retries <= maximum_retries:# maximum retries will 
                    current_unreachable_websites = ', '.join(website for website, attempts in attempts_dict_websites.items() if attempts >= max_attempts)
                    print(f"Superseded maximum retries attempts for currently unreachable websites: {current_unreachable_websites}. Continuing to check other websites.")
                    break

                current_time = time.time()
                if current_time - last_report_time >= status_report_interval and send_status_report=='TRUE':
                    print(f"Status report at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}:")
                    currentAcessibleWebistes=len(accessible_websites)
                    print(f"Accessible websites:{currentAcessibleWebistes}")
                    send_msg(f"Accessible websites:{currentAcessibleWebistes}")
                    for site in accessible_websites:
                        print(f" - {site}")
                    if all(attempts != max_attempts for attempts in attempts_dict_websites.values()):
                        print("Currently there are no inacessible websites, looks like everything is healthy!")
                        send_msg("Currently there are no inacessible websites, looks like everything is healthy!")
                        break
                    else :
                        print(f"Inacessible websites:{currentUnreachablewebsites}")
                        send_msg(f"Inacessible websites:{currentUnreachablewebsites}")
                        for site, attempts in attempts_dict_websites.items():
                            if attempts == max_attempts:
                                print(f" - {site}")
                                send_msg(f" - {site}")
                    last_report_time = current_time


        else:
            print("No unreachable websites remain for retrying. Continuing to check the remaining websites.")

# List of websites to check
websites_to_check =os.getenv('WEBSITES_TO_CHECK').split(',')

# Run the check
check_websites(websites_to_check)
