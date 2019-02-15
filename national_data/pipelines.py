# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import logging


logger = logging.getLogger(__name__)

class DataToJsonPipeline(object):
    def process_item(self, item, spider):
        #目录，去掉末尾的文件名
        file_dir = './数据/' + '/'.join(item['name'].split('/')[:-1])
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        #文件名
        file_name = item['name'].split('/')[-1] + '.json'
        #将item写入文件
        path = file_dir + '/' + file_name
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf8') as f:
                f.write(item['json_data'])
            logger.info('{} 已成功保存！'.format(path))
        else:
            #文件名重复，存在错误
            logger.error('文件名已存在，可能是重复下载或其他问题，请检查！')
            raise IOError
        return item
