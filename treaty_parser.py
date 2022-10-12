from bs4 import BeautifulSoup
import urls
from langdetect import detect, LangDetectException
import logging

console_output = ""


def page_is_empty(page_content):
    # if view-empty div or 'page not found' is found, then page is blank, exit program
    titles = page_content.find_all("title")
    view_empty_divs = page_content.find_all("div", {"class": "view-empty"})
    for title in titles:
        if 'Page not found' in title.get_text() or len(view_empty_divs) > 0:
            return True


def parse_treaty_link(link):
    paragraphs = ""
    output = ""
    if 'Treaty Text**' in link:
        treaty_text_link = 'https://iea.uoregon.edu' + link.get('href')
        sub_page = urls.get(treaty_text_link)
        sub_page_content = BeautifulSoup(sub_page.content, 'html.parser')
        main_div = sub_page_content.find_all("div", {"class": "content clearfix"})

        for x in main_div:
            paragraphs = x.find_all('p')

        output = ''
        for x in paragraphs:
            # filters out source links and special characters
            if 'Source: ' not in x.get_text() and "\ufeff" not in x.get_text():
                output += x.get_text() + ' '
    return output
