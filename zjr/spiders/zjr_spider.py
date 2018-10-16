# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import logging 
import requests
import re

class ZjrSpider(scrapy.Spider):
    name = 'bbs'
    data = ['161', '106', '177', '204', '120', '216', '205']
    start_urls = ['http://bbs.fobshanghai.com/forum-'+data[0]+'-1.html']
    basic_url = 'http://bbs.fobshanghai.com/'
    max_index = 40

    index = 1

    def get_proxy(self):
        return requests.get("http://proxy_pool:5010/get/").content

    def del_proxy(self, hostip):
        requests.get("http://proxy_pool:5010/delete/?proxy={}".format(hostip))
    
    def start_requests(self):
        for url in self.start_urls:
            proxy = str(self.get_proxy(), encoding='utf-8')
            yield scrapy.Request(url=url, callback=self.parse, meta={'proxy':'http://'+proxy, 'hostip':proxy, 'me_url':url})

    def parse(self, response):
        self.index += 1
        soup = BeautifulSoup(response.text, 'html5lib')
        # 判断代理是否被封
        if len(soup.find_all('a', href=re.compile('ip\.'))) == 1:
            self.del_proxy(response.meta['hostip'])
            proxy = str(self.get_proxy(), encoding='utf-8')
            yield scrapy.Request(url=response.meta['me_url'], callback=self.parse, meta={'proxy':'http://'+proxy, 'hostip':proxy, 'me_url':response.meta['me_url']})
        titles = soup.find_all('td', class_='f_title')
        authors = soup.find_all('td', class_='f_author')
        times = soup.find_all('td', class_='f_last')
        if len(titles) == len(authors) and len(times) == len(authors):
            for i in range(len(titles)):
                # yield {"title":titles[i].a.text,
                #          "author":authors[i].a.text,
                #          "last time": times[i].a.text,
                #          "file_id": titles[i].a['href'].split('-')[1]}
                proxy = str(self.get_proxy(), encoding='utf-8')
                url = self.basic_url + titles[i].a['href']
                yield scrapy.Request(url=url, callback=self.parse_item, meta={'proxy': "http://"+proxy, 'hostip':proxy, 'me_url':url})
        next_html = ''
        tmp = soup.find_all('a', 'p_redirect')
        if self.index <= self.max_index:
            next_html = self.start_urls[0][:self.start_urls[0].rfind('-')+1] + str(self.index) + '.html'
            proxy = str(self.get_proxy(), encoding='utf-8')
            yield scrapy.Request(next_html, callback=self.parse, meta={'proxy': "http://"+proxy, 'hostip':proxy, 'me_url':next_html})
            
    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html5lib')
        # 判断代理是否被封
        if len(soup.find_all('a', href=re.compile('ip\.'))) == 1 or soup.find('form') is None:
            self.del_proxy(response.meta['hostip'])
            proxy = str(self.get_proxy(), encoding='utf-8')
            yield scrapy.Request(url=response.meta['me_url'], callback=self.parse, meta={'proxy':'http://'+proxy, 'hostip':proxy, 'me_url':response.meta['me_url']})
        only_one_page = False
        cur_page, max_page = 0, 0
        tmp_url = ''
        if soup.find('a', class_='p_pages') is None:
            only_one_page = True
        if not only_one_page:
            cur_page, max_page = map(int,soup.find('a', class_='p_pages').text.split('\xa0')[1].split('/'))
            cur_page += 1
        if cur_page == 2 or only_one_page: tmp_url = response.url.split('-')[-3]
        else: tmp_url = response.url.split('=')[-3].split('&')[0]
        tmp = soup.find('form').find_all('div', recursive=False)
        for item in tmp:
            author = item.table.tbody.tr.find_all('td', recursive=False)[0].find_all('a', recursive=False)[1].text
            content = item.find('div', class_='t_msgfont')
            if content is None: 
                content = '这个作者被禁言了'
                continue
            elif content.text.strip() == '': 
                content = '作者回复的是表情-_-'
                continue
            elif author == '':
                continue
            else: 
                content = content.text
                content = content.replace('\xa0', '')
                content = content.replace(' ', '')
                content = content.replace('\n', '')
            time = item.find_all('div', class_='right')[1].next_sibling.next_sibling.text.split('\n')[3][4:-1]
            yield  {"author": author,
                    "content": content,
                    "time": time,
                    "file_id": tmp_url}
        if soup.find('a', class_='p_pages') is not None:
            if cur_page < max_page:
                proxy = str(self.get_proxy(), encoding='utf-8')
                url = 'http://bbs.fobshanghai.com/viewthread.php?tid='+tmp_url+'&extra=&page=' + str(cur_page)
                yield scrapy.Request('http://bbs.fobshanghai.com/viewthread.php?tid='+tmp_url+'&extra=&page=' + str(cur_page), callback=self.parse_item, \
                        meta={'proxy':'http://'+proxy, 'hostip': proxy, 'me_url':url})
                
