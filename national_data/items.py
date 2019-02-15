# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NationalDataItem(scrapy.Item):
    '''ajax抓取，都是json数据, 在此不做抽取，原样保存'''
    json_data = scrapy.Field()
    name = scrapy.Field()