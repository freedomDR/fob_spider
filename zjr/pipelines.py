# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs
import csv

class ZjrPipeline(object):

    def __init__(self):
        self.file = open('./data/data.csv', 'a', newline='')
        # self.csv_write = csv.writer(self.file, dialect='excel')
        pass

    def process_item(self, item, spider):
        # file_id = item.pop('file_id')
        # self.file = codecs.open('./data/'+file_id+'.json', 'a', encoding='utf-8')
        # line = json.dumps(dict(item), ensure_ascii=False)+'\n'
        # self.file.write(line)
        # self.file.close()
        tmp = []
        for k, v in item.items():
            tmp.append(v)
        tmp.pop() #帖子ID暂时不要
        # self.csv_write.writerow(tmp)
        self.file.write(','.join(tmp)+'\n')
        return item

    def spider_closed(self, spider):
        self.file.close()
        pass
