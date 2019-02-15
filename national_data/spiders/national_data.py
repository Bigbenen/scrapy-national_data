# -*- coding: utf-8 -*-
import scrapy
from ..items import NationalDataItem
import json
import time


class NationalDataSpider(scrapy.Spider):
    name = 'national_data'
    allowed_domains = ['data.stats.gov.cn']
    #start_urls = ['http://data.stats.gov.cn/']
    #月度数据 起点
    base_url = 'http://data.stats.gov.cn/easyquery.htm'


    def gettime(self):
        return int(round(time.time()) * 1000)

    def start_requests(self):
        key = {
            'id' : 'zb',
            'dbcode' : 'hgyd',
            'wdcode' : 'zb',
            'm' : 'getTree'
            }
        #请求月度数据总目录
        self.logger.debug('月度数据总目录...生成请求')
        yield scrapy.FormRequest(url=self.base_url, formdata=key, callback=self.parse_tree)

    def parse_tree(self, response):
        '''据观察，月度数据每个指标至少是二级/三级标题，此方法负责请求一级标题及其他非末级标题'''
        #self.logger.debug(response.text)
        trees = json.loads(response.text)
        for tree in trees[-1:]:
            name = tree.get('name')
            key = {
                'id': tree.get('id'),
                'dbcode': tree.get('dbcode'),
                'wdcode': tree.get('wdcode'),
                'm': 'getTree'
            }

            self.logger.debug('<{}>...生成请求'.format(name))
            yield scrapy.FormRequest(url=self.base_url, formdata=key, callback=self.parse_tree_end,
                                         meta={'name':name})


    def parse_tree_end(self, response):
        '''此方法负责请求最末级标题'''
        #self.logger.debug(response.text)
        last_name = response.meta.get('name')
        items = json.loads(response.text)
        for item in items:
            name = item.get('name')
            #构造末级标题请求参数
            key = {
                'm': 'QueryData',
                'dbcode' : item.get('dbcode'),
                'rowcode' : 'zb',
                'colcode' : 'sj',
                'wds' : '[]',
                'dfwds' : json.dumps(
                            [{"wdcode": "{}".format(item.get('wdcode')),
                            "valuecode": "{}".format(item.get('id'))}]
                                    ),
                'k1' : str(self.gettime())
            }
            #若该标题非末级标题，在parse_item中会用此参数重新构造请求
            key_not_end = {
                'id': item.get('id'),
                'dbcode': item.get('dbcode'),
                'wdcode': item.get('wdcode'),
                'm': 'getTree'
            }

            self.logger.debug('<{}>...生成请求'.format(last_name + '/' + name))
            yield scrapy.FormRequest(self.base_url, formdata=key, callback=self.parse_item,
                                     meta={'name':last_name + '/' + name, 'key_not_end':key_not_end})

    def parse_item(self, response):
        '''此方法负责解析最末级标题数据'''
        last_name = response.meta.get('name')
        data = json.loads(response.text)
        # 有些二级结构中的某些二级标题，其下面还会有三级标题，一开始被当作二级结构处理，无法得到正确数据，在此处需要检验
        #若数据正确
        if issubclass(type(data), dict) and data.get('returncode') == 200:
            self.logger.debug('成功获取到<{}>的数据'.format(last_name))
            item = NationalDataItem()
            # ajax抓取，都是json数据, 在此不做抽取，原样保存
            item['json_data'] = response.text
            item['name'] = last_name
            yield item
        #若数据错误，很可能是该级标题下还有子标题，重新发起请求
        elif issubclass(type(data), dict) and data.get('returncode') != 200:
            key = response.meta.get('key_not_end')
            self.logger.debug('获取<{}>数据失败，发现其子标题，重新生成请求...'.format(last_name))
            yield scrapy.FormRequest(self.base_url, formdata=key, callback=self.parse_tree_end,
                                     meta={'name':last_name})
        #其他原因导致但数据错误
        else:
            print(type(data), data)
            self.logger.error('获取<{}>发生错误，请检查\n'.format(last_name))
            #raise some exception