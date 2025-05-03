import asyncio
import requests
import time
import logging
import configparser
import sys

from pubSubClient import PubSubClient

from telegramClient import TelegramClient

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


class ProductCheckerKeywords:
    def __init__(self, keywords: list[str], false_friends: dict[str, list[str]], validity_keyword: str, ignore_lines: list[str]):
        self.check_keywords = set(keywords)
        self.false_friends = false_friends
        self.validity_keyword = validity_keyword
        self.ignore_lines = ignore_lines

class ProductChecker:
    def __init__(self, pub_sub_client, telegram_client, check_url, check_interval_secs, found_cooldown_secs, product_checker_keywords):
        self.pub_sub_client = pub_sub_client
        self.telegram_client = telegram_client
        self.check_url = check_url
        self.check_interval_secs = check_interval_secs
        self.found_cooldown_secs = found_cooldown_secs
        self.keywords = product_checker_keywords

    def clean_text(self, text):
        text = text[text.find('<body'):]
        text = text.lower().replace('-', ' ').replace('_', ' ')
        text = '\n'.join([line for line in text.split('\n')
                          if all([ignore not in line for ignore in self.keywords.ignore_lines])])
        if self.keywords.validity_keyword in text:
            logger.info('Looks valid.')
        else:
            logger.warning('Looks maybe invalid?')
        return text

    async def check_for_products(self):
        check_keywords = self.keywords.check_keywords
        false_friends = self.keywords.false_friends
        logger.info("Checking for products...")
        text = self.clean_text(requests.get(self.check_url).text)

        found_words = [kw for kw in check_keywords if kw in text]
        found_words.extend([real for real, falses in false_friends.items()
                            if text.count(real) > sum([text.count(false) for false in falses])])

        if found_words:
            logger.info(f"Products found: {found_words}")
            payload = f"Products maybe available: {' & '.join(found_words)}. \n See {self.check_url}"
            send_telegram = asyncio.create_task(self.telegram_client.send_message(payload))
            send_mail = asyncio.create_task(self.pub_sub_client.publish_to_topic(payload))
            await send_telegram
            await send_mail
            time.sleep(self.found_cooldown_secs)

        else:
            logger.info("No products found. Will check again...")
        time.sleep(self.check_interval_secs)

def main():
    config = configparser.ConfigParser()
    config_file = 'config.ini'
    if sys.argv[1]:
        config_file = sys.argv[1]
    config.read(config_file)
    check_url = config['DEFAULT']['CHECK_URL']
    check_interval_secs = int(config['DEFAULT']['CHECK_INTERVAL_SECS'])
    found_cooldown_secs = int(config['DEFAULT']['FOUND_COOLDOWN_SECS'])
    project_id = config['DEFAULT']['PROJECT_ID']
    topic_id = config['DEFAULT']['TOPIC_ID']
    check_keywords = config['DEFAULT']['KEYWORDS'].split(',')
    false_friend_input = config['DEFAULT']['FALSE_FRIEND_KEYWORDS'].split(',')
    validity_keyword = config['DEFAULT']['VALIDITY_KEYWORD']
    ignore_lines = config['DEFAULT']['IGNORE_LINES'].split(',')
    telegram_token = config['DEFAULT']['TELEGRAM_TOKEN']
    telegram_group = config['DEAFULT']['TELEGRAM_CHAT']

    false_friend_keywords = {false_friend_input[i]: [false_friend_input[i + 1]]
                             for i in range(0, len(false_friend_input) - 1, 2)}

    telegram_client = TelegramClient(telegram_token, telegram_group)
    pub_sub_client = PubSubClient(project_id, topic_id)
    keywords = ProductCheckerKeywords(check_keywords, false_friend_keywords, validity_keyword, ignore_lines)
    product_checker = ProductChecker(pub_sub_client, telegram_client, check_url, check_interval_secs, found_cooldown_secs, keywords)

    while True:
        asyncio.run(product_checker.check_for_products())

if __name__ == "__main__":
    main()