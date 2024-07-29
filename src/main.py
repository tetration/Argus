import urllib.request
import time
import requests
import os
import logging
from dotenv import load_dotenv
import sys

# Create the directory to store logs if it doesn't exist already
if not os.path.exists('logs'):
    os.mkdir('logs')
# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('LOG') == '1' else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/{time.strftime('%Y_%m_%d__%H_%M', time.localtime(time.time()))}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger() # Starts logging everything

# Function to check and create .env file if it doesn't exist
def check_and_create_env_file(file_path='.env'):
    if not os.path.exists(file_path):
        logger.warning("No .env file found! Generating one...")
        with open(file_path, 'w') as env_file:
            env_file.write("TELEGRAM_BOT_TOKEN=123456789:ABCDEF1234567890abcdef1234567890ABC\n")
            env_file.write("CHAT_ID=-1234567890123\n")
            env_file.write("DEBUG_MODE=1\n")
            env_file.write("LOG=1\n")
            env_file.write('WEBSITES_TO_CHECK="https://github.com"\n')
            env_file.write("max_attempts=3\n")
            env_file.write("retry_interval=60\n")
            env_file.write("retry_delay=60\n")
            env_file.write("keep_warning_about_retries=FALSE\n")
            env_file.write("status_report_interval=3600\n")
            env_file.write("send_status_report=TRUE\n")
            env_file.write("maximum_retries=10\n")
        logger.warning(f"{file_path} created with default values.")
    else:
        logger.warning(f"{file_path} already exists. Trying to load it...")

# Load the .env file
def load_environment_variables(file_path='.env'):
    check_and_create_env_file(file_path)
    load_dotenv(file_path)
    logger.info(f"Environment variables succesfully loaded from {file_path}.")


def send_msg(text):
    if os.getenv('DEBUG_MODE') != "1":  # messages wont be sent to your telegram bot if you are not using debug mode
        token = TELEGRAM_BOT_TOKEN
        chat_id = CHAT_ID
        url_req = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"

        try:
            # Make the request to the Telegram API
            response = requests.get(url_req)
        
            # Check for success
            if response.status_code == 200:
                logger.info("Message successfully sent through Telegram's API ")
            else:
                logger.error(f"Failed to send message through Telegram's APP: {response.status_code}, {response.reason}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message: {e}")
    else:
        logger.debug("Message wasn't sent since DEBUG_MODE is enabled on the .env file")

def check_websites(websites="https://google.com", max_attempts=3, retry_interval=60, retry_delay=60, status_report_interval=3600, maximum_retries=10, send_status_report='TRUE'): #Status Report Interval 600 is equal to 10 minutes in real life for 1 hour change it to 3600
    attempts_dict_websites = {website: 0 for website in websites}
    accessible_websites = set()
    last_report_time = time.time()
    logger.info(f"Creating attempts dict of websites: {attempts_dict_websites}")
    while True:
        logger.info(f"current attempts dict website: {attempts_dict_websites}")
        for website in websites[:]:
            attempts = attempts_dict_websites.get(website, 0)
            if attempts >= max_attempts:
                logger.error(f"Failed to access {website} after {max_attempts} attempts. {website} will now be considered inacessible")
                if website in accessible_websites:
                    send_msg(f"Failed to access {website} after {max_attempts} attempts. {website} will now be considered inacessible")
                    accessible_websites.remove(website)
                continue

            try:
                response = urllib.request.urlopen(website)
                if response.getcode() ==200:
                    logger.info(f"{website} is accessible, status code: {response.getcode()}")
                    if website in attempts_dict_websites:
                        attempts_dict_websites[website] = 0
                    else :
                        attempts_dict_websites.add()
                    if website not in accessible_websites:
                        accessible_websites.add(website)
            except urllib.error.URLError as e:
                logger.error(f"Attempt {attempts + 1} for {website} failed: {e.reason}")
                attempts_dict_websites[website] = attempts_dict_websites[website] + 1
                if website in accessible_websites and attempts_dict_websites[website] == max_attempts:
                    accessible_websites.remove(website)
                    logger.error(f"Failed to access {website} after {max_attempts} attempts. {website} will now be considered inacessible")
                    send_msg(f"Failed to access {website} after {max_attempts} attempts. {website} will now be considered inacessible")
            except Exception as e:
                logger.error(f"An error occurred with {website}: {e}")
                attempts_dict_websites[website] = attempts_dict_websites[website] + 1
                if website in accessible_websites and attempts_dict_websites[website] == max_attempts:
                    accessible_websites.remove(website)
                    logger.error(f"Failed to access {website} after {max_attempts} attempts. {website} will now be considered inacessible")
                    send_msg(f"Failed to access {website} after {max_attempts} attempts. {website} will now be considered inacessible")

        time.sleep(retry_interval)

        current_time = time.time()
        if current_time - last_report_time >= status_report_interval and send_status_report=='TRUE':
            logger.info(f"Status report at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}:")
            send_msg(f"Status report at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}:")
            currentAcessibleWebistes=len(accessible_websites)
            currentUnreachablewebsites = sum(1 for attempts in attempts_dict_websites.values() if attempts >= max_attempts)

            logger.info(f"Accessible websites:{currentAcessibleWebistes}")
            send_msg(f"Accessible websites:{currentAcessibleWebistes}")
            for site in accessible_websites:
                logger.info(f" - {site}")
                send_msg(f" - {site}")
            logger.info(f"Inacessible websites:{currentUnreachablewebsites}")
            send_msg(f"Inacessible websites:{currentUnreachablewebsites}")
            for site, attempts in attempts_dict_websites.items():
                if attempts == max_attempts:
                    logger.info(f" - {site}")
                    send_msg(f" - {site}")
            last_report_time = current_time
        # At least one website has surpassed the maximum number of attempts.
        logger.info("No websites left to check. Moving to retry loop for unreachable websites.")
        if any(attempts >= max_attempts for attempts in attempts_dict_websites.values()):
            retries = 0
            while any(attempts >= max_attempts for attempts in attempts_dict_websites.values()):
                retries = retries +1
                for website, attempts in list(attempts_dict_websites.items()):
                    if attempts_dict_websites[website] == max_attempts:
                        try: 
                                response = urllib.request.urlopen(website)
                                logger.info(f"Looks like {website} is now accessible again, status code: {response.getcode()}")
                                send_msg(f"Looks like {website} is now accessible again, status code: {response.getcode()}")
                                attempts_dict_websites[website] = 0
                                accessible_websites.add(website)
                        except urllib.error.URLError as e:
                            logger.error(f"Retry for {website} failed: {e.reason}")
                            if os.getenv('keep_warning_about_retries')=="TRUE": send_msg(f"Retry for {website} failed: {e.reason}")
                        except ValueError as e:
                            logger.error(f"Retry for {website} failed due to ValueError: {e}")
                            if os.getenv('keep_warning_about_retries')=="TRUE": send_msg(f"Retry for {website} failed due to ValueError: {e}")
                        except Exception as e:
                            logger.error(f"An error occurred with {website}: {e}")
                            if os.getenv('keep_warning_about_retries')=="TRUE": send_msg(f"Retry for {website} failed: {e.reason}")
                    time.sleep(retry_delay)
                if retries <= maximum_retries:# maximum retries will 
                    current_unreachable_websites = ', '.join(website for website, attempts in attempts_dict_websites.items() if attempts >= max_attempts)
                    logger.warning(f"Superseded maximum retries attempts for currently unreachable websites: {current_unreachable_websites}. Continuing to check other websites.")
                    break

                current_time = time.time()
                if current_time - last_report_time >= status_report_interval and send_status_report=='TRUE':
                    logger.info(f"Status report at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}:")
                    currentAcessibleWebistes=len(accessible_websites)
                    logger.info(f"Accessible websites:{currentAcessibleWebistes}")
                    send_msg(f"Accessible websites:{currentAcessibleWebistes}")
                    for site in accessible_websites:
                        logger.info(f" - {site}")
                    if all(attempts != max_attempts for attempts in attempts_dict_websites.values()):
                        logger.info("Currently there are no inacessible websites, looks like everything is healthy!")
                        send_msg("Currently there are no inacessible websites, looks like everything is healthy!")
                        break
                    else :
                        logger.info(f"Inacessible websites:{currentUnreachablewebsites}")
                        send_msg(f"Inacessible websites:{currentUnreachablewebsites}")
                        for site, attempts in attempts_dict_websites.items():
                            if attempts == max_attempts:
                                logger.info(f" - {site}")
                                send_msg(f" - {site}")
                    last_report_time = current_time


        else:
            logger.warning("No unreachable websites remain for retrying. Continuing to check the remaining websites.")

# Try to Load Environment Varibles
load_environment_variables()

# Telegram Bot Token and Chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')  # Replace with your Telegram group chat ID

# List of websites to check
websites_to_check =os.getenv('WEBSITES_TO_CHECK').split(',')
# Run the check
check_websites(websites_to_check, int(os.getenv('max_attempts')), int(os.getenv('retry_interval')), int(os.getenv('retry_delay')), int(os.getenv('status_report_interval')), int(os.getenv('maximum_retries')), os.getenv('send_status_report'))
