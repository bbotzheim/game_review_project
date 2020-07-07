# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class GameItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    platform = scrapy.Field()
    genres = scrapy.Field()
    release_date = scrapy.Field()
    ESRB_rating = scrapy.Field()
    summary = scrapy.Field()
    average_user_score = scrapy.Field()
    metascore = scrapy.Field()
    developer = scrapy.Field()
    publisher = scrapy.Field()

class ReviewItem(scrapy.Item):
    title = scrapy.Field()
    platform = scrapy.Field()
    username = scrapy.Field()
    score = scrapy.Field()
    date = scrapy.Field()
    review_text = scrapy.Field()
    critic_flag = scrapy.Field()