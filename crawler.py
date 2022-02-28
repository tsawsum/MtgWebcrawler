import requests
from bs4 import BeautifulSoup
import urllib3
import urllib.request
import urllib.parse
import http.cookiejar
import os
import re
import shutil  # clearly all of these useless imports indicate an arduous process
from lxml import html


session = requests.Session()
completed_sets = []


def login():
    response = session.get('https://www.mtggoldfish.com/login')
    page = html.fromstring(response.content)
    # equivalent to making a soup object
    try:
        auth_token = page.xpath('//form[@action="/auth/identity/callback"]/input[@name="authenticity_token"]')[0].attrib['value']
    except Exception:
        print("LOGIN POSSIBLE ERROR")
    # equivalent to soup.findall with action callback, and an input authenticity token.
    login_data = {'utf8': '✓', 'authenticity_token': auth_token, 'override_origin': '', 'auth_key': 'tsawsum@icloud.com', 'password': 'Kabukisam2', 'commit': 'Log+In'}
    url = 'https://www.mtggoldfish.com/auth/identity/callback'
    session.post(url, data=login_data)

    # Checks if logged in
    soup = BeautifulSoup(session.get('https://www.mtggoldfish.com').text, features="html.parser")
    login_text = soup.find_all('a', class_='nav-link dropdown-toggle')[-1].string.strip()
    if login_text == 'Login':
        print('NOT logged in')
    elif login_text == 'Account':
        print('Logged in')
    else:
        print('What the fuck')


# def login():
#     # control shift i in chrome (gets network tab). Try logging in. Will see the post and get requests.
#     # post request has url
#     url = 'https://www.mtggoldfish.com/auth/identity/callback'
#     # use inspect on the input and then name='___"
#
#     source_code = session.get(url)
#     plain_text_code = source_code.text
#     # need to convert to a bs4 object
#     soup = BeautifulSoup(plain_text_code, features="html.parser")
#     login_data = {'auth_key': 'tsawsum@icloud.com', 'password': 'Kabukisam2', 'authenticity_token', }
#     session.get()
#     if len(session.post(url, data=login_data).text) > 20:
#         print('Login failed')


def set_spider(folder):
    url = 'https://www.mtggoldfish.com/prices/select'
    source_code = session.get(url)
    plain_text_code = source_code.text
    # need to convert to a bs4 object
    soup = BeautifulSoup(plain_text_code, features="html.parser")

    # get the relevant sets
    for link in soup.find(class_='priceList-selectMenu priceList-setMenu priceList-setMenu-Pioneer show').findAll('a'):
        title = link.string
        href = link.get('href')
        set_name = str(href[6:])
        if str(href[:6]) == "/sets/":
            href = 'https://www.mtggoldfish.com' + href
            # print(title)
            # print(href)
            print(set_name)
            if not set_name in completed_sets:
                card_finder(href, folder + set_name + "/")


def card_finder(set_url, folder):
    source_code = session.get(set_url)
    plain_text_code = source_code.text

    soup = BeautifulSoup(plain_text_code, features="html.parser")
    # get the cards individually
    # for link in soup.find(class_='card_name').findAll('a'): # Just for testing
    count = 0
    for link in soup.find(class_='table-responsive').findAll('a'):
        title = link.string

        href = link.get('href')  # separated for no reason at all here
        split_list = href.split("/")
        card_name = "/" + split_list[-1]

        href = 'https://www.mtggoldfish.com' + href + '#paper'

        if not os.path.exists(folder + card_name + '.csv'):
            count += 1
            if count % 5 == 0:
                print(count)
            card_price_downloader(href, folder, card_name)


def card_price_downloader(card_url, folder, card_name):
    source_code = session.get(card_url)
    plain_text_code = source_code.text

    soup = BeautifulSoup(plain_text_code, features="html.parser")
    if soup.find(class_='price-history-download-container') is not None:
        for link in soup.find(class_='price-history-download-container').findAll('a'):
            title = link.string
            href = link.get('href')  # separated for no reason at all here
            href = 'https://www.mtggoldfish.com' + href
            # The download button in theory
            # name = ""
            # i = 0
            # while href[i] != '%':
            #     i += 1
            # while href[i] != "/":
            #     i = i - 1
            #     name = href[i] + name
            # print(name)

            if not os.path.exists(folder):
                os.makedirs(folder)
            try:
                # May not work on mac.
                # Using requests so as to maintain the same cookies
                response = session.get(href, allow_redirects=True)
                if not os.path.exists(folder + card_name + '.csv'):
                    print(card_name)
                    with open(folder + card_name + '.csv', 'wb') as f:
                        f.write(response.content)  # shutil.copyfileobj(response.content, f)
            except Exception:
                print("bad link download")
    else:
        print("Card does not have download link")


login()
set_spider('C://Users//12077//OneDrive//Desktop//MtgWebcrawler/')

#
# def card_finder(item_url, folder):
#     source_code = requests.get(item_url)
#     plain_text_code = source_code.text
#     # Check if it's the right map
#     if 'World War II v5 1942 Second Edition' in plain_text_code:
#         # Find number of pages
#         soup = BeautifulSoup(plain_text_code, features="html.parser")
#         try:
#             last_page = list(soup.findAll('li', {'class': 'page'}))[-2]
#             num_pages = int(list(last_page.children)[1].string)
#         except IndexError:
#             # It doesn't show the total number of pages when there is only 1 page
#             # which throws this exception
#             num_pages = 1
#
#         # Loop through each page
#         savegame_urls = list()
#         page = 1
#         while page <= num_pages:
#             url = item_url + '/?lang=en-US&page=' + str(page)
#             source_code = requests.get(url)
#             plain_text_code = source_code.text
#             # Get the index of all of the savegame extensions
#             savegame_idx = [m.start() for m in re.finditer('.tsvg', plain_text_code)]
#             # Find the start of the url by looking for " at the start
#             for idx in savegame_idx:
#                 i = idx
#                 while plain_text_code[i] != '"' and plain_text_code[i] != '>':
#                     i -= 1
#                 if plain_text_code[i] == '"':
#                     savegame_urls.append('https://forums.triplea-game.org' + plain_text_code[i + 1:idx + 5])
#             page += 1
#
#         # Save each file to the folder
#         if not os.path.exists(folder):
#             os.makedirs(folder)
#         for i in range(len(savegame_urls)):
#             try:
#                 # This does not verify on a mac because its dumb.
#                 urllib.request.urlretrieve(savegame_urls[i], folder + str(i) + '.tsvg')
#             except:
#                 pass
#         return True
#     else:
#         return False
#
#
# forum_spider(2, 'Folder/To/Save/Files/In/')
