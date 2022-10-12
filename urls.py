import time
import requests
import logging


def get(url):
    try:
        return requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        print(e)
        logging.error(e)
        time.sleep(5)
        return get(url)


def get_user_url():
    # keeps asking user for a valid URL until one is provided
    url_is_valid = False
    while not url_is_valid:
        user_url = input("Please enter a treaty search url from https://iea.uoregon.edu/base-agreement-list: ")
        if "https://iea.uoregon.edu/base-agreement-list" in user_url:
            user_url_is_valid = True
            return user_url
        else:
            print("Invalid URL")


def update_url(user_url, page_num):
    # checks each page of search for treaties based on user URL
    if '?' in user_url:
        updated_url = f'{user_url}&page={page_num}'
    else:
        updated_url = f'{user_url}?page={page_num}'
    if page_num == 0:
        updated_url = user_url
    return updated_url
