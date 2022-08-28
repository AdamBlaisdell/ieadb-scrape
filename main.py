from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException
import requests
import csv
import time

# install imports Terminal command line:
# pip install requests beautifulsoup4 langdetect


def get(url):
    try:
        return requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        print(e)
        time.sleep(5)
        return get(url)


# keeps asking user for a valid URL until one is provided
user_url = ""
user_url_is_valid = False
while not user_url_is_valid:
    user_url = input("Please enter a treaty search url from https://iea.uoregon.edu/base-agreement-list: ")
    if "https://iea.uoregon.edu/base-agreement-list" in user_url:
        user_url_is_valid = True
    else:
        print("Invalid URL")


csv_file = input("Please enter a file name for csv output: ")

# tracks number of pages and treaties
page_num = 0
row = 0

# data is stored in a .csv file
with open(csv_file + '.csv', 'w', newline='', encoding='utf-8-sig') as f:
    # create text file for logging
    log = open(csv_file + '_log.txt', 'w', newline='')
    log.write(f'URL: {user_url} \n')

    # write the column titles for the file
    the_writer = csv.writer(f)
    the_writer.writerow(['ID', 'Text'])

    # loops until quit()
    while True:
        # checks each page of search for treaties based on user URL
        if '?' in user_url:
            new_user_url = f'{user_url}&page={page_num}'
        else:
            new_user_url = f'{user_url}?page={page_num}'
        if page_num == 0:
            new_user_url = user_url
        page = get(new_user_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        page_links = soup.find_all('a', href=True)

        # if view-empty div or 'page not found' is found, then page is blank, exit program
        titles = soup.find_all("title")
        view_empty_divs = soup.find_all("div", {"class": "view-empty"})
        for title in titles:
            if 'Page not found' in title.get_text() or len(view_empty_divs) > 0:
                console_output = f'Page {page_num + 1} not found! {row} total treaties were parsed. Exiting program.'
                print(console_output)
                log.write(console_output)
                log.close()
                f.close()
                exit()

        treaties_parsed_on_page = 0
        for item in page_links:
            if 'Treaty Text**' in item:
                textID = item.get('href').replace('/treaty-text/', '')
                treaty_text_link = 'https://iea.uoregon.edu' + item.get('href')
                sub_page = get(treaty_text_link)
                soup = BeautifulSoup(sub_page.content, 'html.parser')
                main_div = soup.find_all("div", {"class": "content clearfix"})

                for x in main_div:
                    pars = x.find_all('p')

                output = ''
                for x in pars:
                    # filters out source links and special characters
                    if 'Source: ' not in x.get_text() and "\ufeff" not in x.get_text():
                        output += x.get_text() + ' '
                try:
                    if detect(output) == 'en':
                        the_writer.writerow([textID, output])
                        row += 1
                        treaties_parsed_on_page += 1
                        console_output = f'From page {page_num + 1}, added row {row}, treaty ID: {textID}'
                        print(console_output)
                        log.write(console_output + '\n')
                except LangDetectException:
                    row += 1
                    treaties_parsed_on_page += 1
                    console_output = f'From page {page_num + 1} row {row} treaty ID: {textID}' \
                                     f' NOT ADDED: Empty page or language error'
                    print(console_output)
                    log.write(console_output + '\n')
        console_output = f'--------------------------------------\n' \
                         f'Page {page_num + 1} complete: {treaties_parsed_on_page} treaties were parsed.\n'
        print(console_output)
        log.write(console_output + '\n')
        page_num += 1
