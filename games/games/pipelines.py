# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exporters import CsvItemExporter
from scrapy import signals
from pydispatch import dispatcher

def item_type(item):
    # The CSV file names are used (imported) from the scrapy spider.
    return type(item)

class GamesPipeline(object):
    # For simplicity, I'm using the same class def names as found in the,
    # main scrapy spider and as defined in the items.py
    fileNamesCsv = ['GameItem','ReviewItem']

    def __init__(self):
        self.files = {}
        self.exporters = {}
        dispatcher.connect(self.spider_opened, signal=signals.spider_opened)
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

    def spider_opened(self, spider):
        self.files = dict([ (name, open(name+'.csv','wb')) for name in self.fileNamesCsv ])
        for name in self.fileNamesCsv:
            self.exporters[name] = CsvItemExporter(self.files[name])
            if name == 'GameItem':
                self.exporters[name].fields_to_export = [
                    'url', 'title', 'platform', 'genres', 'release_date', 'ESRB_rating',
                    'summary', 'average_user_score', 'metascore', 'developer', 'publisher'
                ]
                self.exporters[name].start_exporting()
            if name == 'ReviewItem':
                self.exporters[name].fields_to_export = [
                    'title', 'platform', 'username', 'score',
                    'date', 'review_text', 'critic_flag'
                ]
                self.exporters[name].start_exporting()

    def spider_closed(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]

    def process_item(self, item, spider):
        typesItem = item_type(item)
        if typesItem in set(self.fileNamesCsv):
            self.exporters[typesItem].export_item(item)
        return item
