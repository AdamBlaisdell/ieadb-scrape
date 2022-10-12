from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException
import urls
import treaty_parser
import csv
import logging

# install imports Terminal command line:
# pip install requests beautifulsoup4 langdetect

user_url = urls.get_user_url()
logging.info(f'URL: {user_url}')
csv_name = input("Please enter a file name for csv output: ")
logging.basicConfig(level=logging.INFO, filename=csv_name + "_log.log", filemode='w',
                    format='%(asctime)s %(levelname)s %(message)s ', datefmt='%m/%d/%y %I:%M:%S %p')

# tracks number of pages and treaties
page_num = 0
row = 0

# data is stored in a .csv file
with open(csv_name + '.csv', 'w', newline='', encoding='utf-8-sig') as f:

    # write the column titles for the file
    the_writer = csv.writer(f)
    the_writer.writerow(['ID', 'Text'])

    # loops until quit()
    while True:

        new_user_url = urls.update_url(user_url, page_num)
        page = urls.get(new_user_url)
        page_content = BeautifulSoup(page.content, 'html.parser')

        # if view-empty div or 'page not found' is found, then page is blank, exit program
        if treaty_parser.page_is_empty(page_content):
            console_output = f'Page {page_num + 1} not found! {row} total treaties were parsed. Exiting program.'
            print(console_output)
            logging.info(console_output)
            f.close()
            exit()

        page_links = page_content.find_all('a', href=True)

        treaties_parsed_on_page = 0
        for link in page_links:
            treaty_text = treaty_parser.parse_treaty_link(link)
            treaty_id = link.get('href').replace('/treaty-text/', '')

            try:
                if treaty_text and detect(treaty_text) == 'en':
                    the_writer.writerow([treaty_id, treaty_text])
                    row += 1
                    treaties_parsed_on_page += 1
                    console_output = f'From page {page_num + 1}, added row {row}, treaty ID: {treaty_id}'
                    print(console_output)
                    logging.info(console_output)
            except LangDetectException as e:
                row += 1
                treaties_parsed_on_page += 1
                console_output = f'From page {page_num + 1} row {row} treaty ID: {treaty_id}' \
                                 f' NOT ADDED: Empty page or language error'
                print(console_output)
                logging.debug(console_output)
        console_output = f'--------------------------------------\n' \
                         f'Page {page_num + 1} complete: {treaties_parsed_on_page} treaties were parsed.'
        print(console_output)
        logging.info(console_output)
        page_num += 1
