# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
import logging
import requests


logger = logging.getLogger(__name__)

class MyUserAgentDownloaderMiddleware():

    def __init__(self, useragent_list):
        self.ua_list = useragent_list

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawler.settings.get('USER_AGENT_LIST')
        )

    def process_request(self, request, spider):
        random_ua = random.choice(self.ua_list)
        request.headers['User-Agent'] = random_ua
        #logger.debug('{} set User-Agent = {}'.format(request.url, request.headers['User-Agent']))
        #logger.debug('{} cookies: {}'.format(request.url, request.headers.get('Cookie', None)))
        return None

class ProxyMiddleware():
    def __init__(self, proxy_url):
        self.logger = logging.getLogger(__name__)
        self.proxy_url = proxy_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawler.settings.get('PROXY_URL')
        )

    def get_random_proxy(self):
        try:
            r = requests.get(self.proxy_url)
            if r.status_code == 200:
                proxy = r.text
                #self.logger.debug('获得代理 {}'.format(proxy))
                return proxy
        except requests.ConnectionError:
            return False

    def process_request(self, request, spider):
        #默认使用代理，重试才会用本机ip
        retry_times = request.meta.get('retry_times')
        if not retry_times or retry_times < 2:
            proxy = self.get_random_proxy()
            #proxy = '1.1.1.1:1111'
            if proxy:
                uri = 'http://{}'.format(proxy)
                request.meta['proxy'] = uri
                self.logger.debug('使用代理<{}>请求{}'.format(request.meta['proxy'], request.url))
            else:
                #这里可以自定义error并raise
                self.logger.error('获取代理失败！')
        else:
            #清除之前设置的代理，默认使用本机ip
            request.meta['proxy'] = None
            self.logger.debug('使用本机请求{}'.format(request.url))
        return None


