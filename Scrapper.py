#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import re
import sys
import time
import urllib
from urllib.error import HTTPError, URLError

import bs4
import requests
import tqdm


# In[ ]:


def get_source(page_url):
    soup = bs4.BeautifulSoup(urllib.request.urlopen(page_url), "lxml")
    title = soup.find(id="firstHeading").text
    tmp = soup.find("script").text.split("proofreadpage_source_href")

    if (len(tmp) == 1):
        return page_url, title

    else:
        page_url = "https://fr.wikisource.org" + tmp[1].split()[1].split('"')[1]
        page_url = page_url[:-1]
        return page_url, title


# In[ ]:


def remove_dups(file):
    uniques = set()
    with open(file, "r", encoding="utf8") as f:
        for link in tqdm.tqdm(f.readlines()):
            page, _ = get_source(link)
            uniques.add('/'.join(page.split('/')[4:]).strip())
    with open(file, 'w+') as f:
        for item in uniques:
            f.write("https://fr.wikisource.org/wiki/%s\n" % item)


# In[ ]:


def get_pages_url(source_url):
    pages = []
    try:
        soup = bs4.BeautifulSoup(urllib.request.urlopen(source_url), "lxml")
    except URLError:
        pages.append("Non scrappable")
        return pages
    for a in soup.findAll('a', {'class':['prp-pagequality-3 quality3', 'prp-pagequality-4 quality4']}):
        pages.append("https://fr.wikisource.org/" + a['href'])
    if not pages:
        return [source_url]
    return pages


# In[ ]:


def get_content_page(url):
    if url == "Non scrappable":
        text = "Non scrappable"
        return text
    else:
        res = urllib.request.urlopen(url)
        wiki = bs4.BeautifulSoup(res, "lxml")
        elems = wiki.select('p')
        text = ""
        for elem in elems:
            text += re.sub(r"\n", " ", elem.getText())
            text += "\n"
        text = re.sub(r"(\[\d+\])+", "", text)
        return text


# In[ ]:


def get_content_pages(urls):
    content = ""
    pbar = tqdm.tqdm(urls)
    soup = bs4.BeautifulSoup(urllib.request.urlopen(urls[0]), "lxml")
    title = soup.find(id="firstHeading").text
    for url in pbar:
        content += get_content_page(url) + " "
        pbar.set_description("Processing %s" % url.split('/')[-2])
    return content, title


# In[ ]:


def save_to_file(text, title):
    f = '":.*<>|/\\?'
    for char in f:
        if char in title:
            title = title.replace(char, " ")
    if not os.path.exists('Raw text Sciences'):
        os.makedirs('Raw text Sciences')
    with open(os.path.join('Raw text Sciences', title + ".txt"), "w", encoding="utf8") as file:
        file.write(text)
    return


# In[ ]:


if __name__ == "__main__":
    # You can comment out this first line if the URL list is clean already (no dups).
    remove_dups("UrlListSciences.txt")
    f = open("UrlListSciences.txt", "r")
    lines = f.readlines()
    f.close()
    for line in lines:
        livre, titre = get_content_pages(get_pages_url(line))
        save_to_file(livre, titre)

