# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MytimeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
	artikelnummer = scrapy.Field()
	sku = scrapy.Field()
	name = scrapy.Field()
	price = scrapy.Field()
	special_price = scrapy.Field()
	categories = scrapy.Field()
	image = scrapy.Field()
	small_image = scrapy.Field()
	thumbnail = scrapy.Field()
   	gallery = scrapy.Field()
	details = scrapy.Field()
	nahrwerte = scrapy.Field()
	zutaten_allergene = scrapy.Field()
	inverkehrbringer = scrapy.Field()
	
	#stock = scrapy.Field()
	#categories = scrapy.Field()
	#otheroptions = scrapy.Field()
	#description = scrapy.Field()
    #pass
	
	
