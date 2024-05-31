# Argus Bot
![Argus](https://github.com/tetration/Argus/assets/2152854/c793ba95-494e-4444-8ce7-cf1b92e2f4e8)

Argus Bot is a Python script designed to monitor the accessibility of a list of websites. Named after Argus Panoptes from Greek mythology, who had many eyes to watch over everything, this bot continuously checks if websites are up and sends notifications if any become unreachable. It also provides periodic status reports.

## Features
- Checks the accessibility of a list of websites.
- Retries unreachable websites a configurable number of times.
- Sends notifications via Telegram when websites become unreachable or accessible again.
- Provides periodic status reports.
- Configurable logging to file and console.

## Requirements
- Python Python 3.10.6 (Tested Under this version)
- Required Python packages: `requests`, `python-dotenv`, `urllib`

## Setup
1. Clone this repository or download the script.

2. Install the required Python packages:
    ```bash
    pip install requests python-dotenv
    ```

3. Create a `.env` file in the same directory as the script with the following content:
    ```env
    TELEGRAM_BOT_TOKEN=your_telegram_bot_token
    CHAT_ID=your_telegram_chat_id
    DEBUG_MODE=0
    LOG=1
    WEBSITES_TO_CHECK=https://example1.com,https://example2.com
    max_attempts=3
    retry_interval=5
    retry_delay=60
    status_report_interval=600
    maximum_retries=10
    send_status_report=TRUE
    ```
    Additional explanations:
    - In the example above the status_report_interval is set to 600 which means every 10 minutes the bot will send a report to the group chat or chat in the Telegram App about the website(As long as send_status_report is set to true)

    Replace the placeholders with your actual values:
    - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token.
    - `CHAT_ID`: Your Telegram chat ID.
    - `DEBUG_MODE`: Set to `1` to enable debug mode (disables Telegram messages).
    - `LOG`: Set to `1` to enable logging to log file.
    - `WEBSITES_TO_CHECK`: Comma-separated list of websites to monitor.
    - `max_attempts`: Maximum number of attempts before marking a website as unreachable.
    - `retry_interval`: Time (in seconds) between checks for each website.
    - `retry_delay`: Time (in seconds) between retries for unreachable websites.
    - `status_report_interval`: Time (in seconds) between status reports.
    - `maximum_retries`: Maximum number of retries for unreachable websites.
    - `send_status_report`: Set to `TRUE` to enable status reports(If disabled the bot will only warn when a website is unreachable).

4. Run the script:
    ```bash
    python argus_bot.py
    ```

## How It Works
1. **Initialization**:
    - Loads environment variables from the `.env` file.
    - Configures logging based on the environment settings.
    - Initializes the list of websites to check and sets up the attempts dictionary.

2. **Website Checking Loop**:
    - Continuously checks the accessibility of each website.
    - If a website is accessible, it logs the status and resets the attempt count for that website.
    - If a website is not accessible, it increments the attempt count and logs the error.
    - If a website reaches the maximum number of attempts, it is marked as inaccessible, and a notification is sent.

3. **Status Reporting**:
    - Periodically sends status reports to the configured Telegram chat.
    - Reports the number of accessible and inaccessible websites.

4. **Retry Loop**:
    - Retries checking unreachable websites until they become accessible or the maximum number of retries is reached.
    - Sends notifications when a previously unreachable website becomes accessible again.

## Logging
- Logs are stored in the `logs` directory, with each log file named based on the current timestamp.
- Both file and console logging are supported, and can be configured via the `.env` file.

## Debug Mode
- When `DEBUG_MODE` is set to `1`, the bot will not send messages to Telegram but will log all activities.
- Useful for testing and development purposes.

## Example `.env` File
```env
TELEGRAM_BOT_TOKEN=123456789:ABCDEF1234567890abcdef1234567890ABC
CHAT_ID=-1234567890123
DEBUG_MODE=0
LOG=1
WEBSITES_TO_CHECK=https://example1.com,https://example2.com
max_attempts=3
retry_interval=5
retry_delay=60
status_report_interval=600
maximum_retries=10
send_status_report=TRUE
