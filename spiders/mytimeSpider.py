# This script allows you to quickly crawl pages based off of the sitemap(s) for any given domain.  The XmlXPathSelector was not doing it for me nor was the XmlItemExporter this code is by far the fastest and easiest way I have found to crawl a site based off of the URLs listed in the sitemap.
 
import urllib2
import os
import re

from scrapy.contrib.loader import ItemLoader
from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy import log
from scrapy.utils.response import body_or_str
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from mytime.items import MytimeItem

PCOUNT = 0
 
class MytimeSpider(BaseSpider):
	name = "mytime"
	allowed_domains=["www.mytime.de"]
	start_urls = ["http://www.mytime.de/sitemap.xml"]
	#rules=[Rule(SgmlLinkExtractor(allow=(r'http://www.mytime.de/Heim_und_Garten/Wohnen_und_Einrichten/Beleuchtung/Innenbeleuchtung/Koziol_Pendelleuchte_JOSEPHINE_M_milchweiss_0302010257.html'))),]
 
	def parse(self, response):
		nodename = 'loc'
		text = body_or_str(response)
		r = re.compile(r"(<%s[\s>])(.*?)(</%s>)" % (nodename, nodename), re.DOTALL)
		for match in r.finditer(text):
			url = match.group(2)
			if url != '':
			#if url == 'http://www.mytime.de/Haushalt/Kueche/Kuechenkleingeraete/Eismaschinen/Bestron_DHY_1705_Eismaschine-_gruen_0810951088.html' or url == 'http://www.mytime.de/Suesswaren_und_Knabbereien/Suessgebaeck/Waffeln_und_Waffelmischungen/Findeisen_Original_Waffel-Eistueten_4502020624.html' or url == 'http://www.mytime.de/Schreibwaren/Schreiben_und_Zeichnen/Fineliner/Stabilo_OHPen_universal_permanent_Folienschreiber_superfein_gruen_4510050990.html' or url =='http://www.mytime.de/Schreibwaren/Ordnen-_Archivieren_und_Organisieren/Schreibtisch-Utensilien/Casio_XR-9X1_Schriftband_9mm_Black_Ink_clear_4510050962.html' or url =='http://www.mytime.de/Schreibwaren/Schreiben_und_Zeichnen/Farbstifte_und_Filzstifte/Stabilo_Trio_Scribbi_Fasermaler_gruen_4510050924.html' or url=='http://www.mytime.de/Suesswaren_und_Knabbereien/Knabbereien/Nuesse_und_Knabbermischungen/Jeden_Tag_Cashew-Kerne_geroestet_und_gesalzen_4502020587.html' or url== 'http://www.mytime.de/Suesswaren_und_Knabbereien/Knabbereien/Nuesse_und_Knabbermischungen/Seeberger_Blanchierte_Mandeln_Honig_und_Salz_4502111669.html':
				yield Request(url, callback=self.parse_page)
 
	def parse_page(self, response):
		global PCOUNT 
		response = response.replace(body=response.body.replace('<br />', '\n'))
		response = response.replace(body=response.body.replace('<br/>', '\n'))
		response = response.replace(body=response.body.replace('<br>', '\n'))
		#hxs = HtmlXPathSelector(response)
		sel = Selector(response)
		current_url = response.url
		sites = sel.xpath('//div[@class="articleDetail"]')
		#item = MytimeItem()
		il = ItemLoader(item=MytimeItem())
		for site in sites:
			image_urls = site.xpath('//ul[@class="product-images"]/li/a/img/@src').extract()
			image_file = image_urls[0].split('/')[-1]
			small_image_file = image_file
			thumbnail_file = image_file
			gallery_file = ';'
			for img in image_urls:
				image_name = img.split('/')[-1]
				image_url = 'http://d2jdyzt6tc17s.cloudfront.net/products/images2/' + image_name 
				gallery_file += '/' + image_name + ';' 
				self.download(image_url, image_name)
			#print gallery_file
			product_name = site.xpath('//h1[@id="product-name"]/text()').extract()[0].encode('utf-8')
			
			p_name = " ".join(product_name.split())
			p_price = site.xpath('//td/input[@id="product-price"]/@value').extract()[0].encode('utf-8')
			p_special_price = p_price
			p_image = image_file
			p_small_image = small_image_file
			p_thumbnail = thumbnail_file
			p_gallery = gallery_file.strip(';')
			p_sku = site.xpath('//td/input[@name="product-id"]/@value').extract()[0].encode('utf-8')
			p_artikelnummer = (image_file.split('.')[0]).split('_')[0]
			
			
			crawl_url = current_url.split('//')[1]
			leftindex = crawl_url.find('/')+1
			righttindex = crawl_url.rfind('/')
			
			p_categories = crawl_url[leftindex:righttindex]
			
			p_details = ''
			p_nahrwerte = ''
			p_zutaten_allergene = ''
			p_inverkehrbringer = ''
			
			il.add_value('name',p_name)
			il.add_value('price',p_price)
			il.add_value('special_price',p_special_price)
			il.add_value('image',p_image)
			il.add_value('small_image',p_small_image)
			il.add_value('thumbnail',p_thumbnail)
			il.add_value('gallery',p_gallery)
			il.add_value('sku',p_sku)
			il.add_value('artikelnummer',p_artikelnummer)
			il.add_value('categories',p_categories)
			
			
			product_details_text_1_key = site.xpath('//div[@id="product_details_text" and @detail_id="1"]/div/div/div/div/div/div[@class="details_left"]/text()').extract()
			product_details_text_1_value = site.xpath('//div[@id="product_details_text" and @detail_id="1"]/div/div/div/div/div/div[@class="details_right"]/text()').extract()
			#print len(product_details_text_1_value)
			#print product_details_text_1_value
			details_text_1_key = map(lambda str:str.strip(),product_details_text_1_key)
			details_text_1_value = map(lambda str:str.strip(),product_details_text_1_value)
			details_text_1_key = filter(None,details_text_1_key)
			details_text_1_value = filter(None,details_text_1_value)
			product_details_text_1 = dict(zip(details_text_1_key, details_text_1_value))
			p_details = product_details_text_1
			
			product_details_text_3_key = site.xpath('//div[@id="product_details_text" and @detail_id="3"]/div/div/div/div/div/div[@class="details_left"]/text()').extract()
			product_details_text_3_value = site.xpath('//div[@id="product_details_text" and @detail_id="3"]/div/div/div/div/div/div[@class="details_right"]/text()').extract()
			
			#print len(product_details_text_3_value)
			#print product_details_text_3_value
			details_text_3_key = map(lambda str:str.strip(),product_details_text_3_key)
			details_text_3_value = map(lambda str:str.strip(),product_details_text_3_value)
			details_text_3_key = filter(None,details_text_3_key)
			details_text_3_value = filter(None,details_text_3_value)
			product_details_text_3 = dict(zip(details_text_3_key, details_text_3_value))
			
			product_details_text_3_allergene_key = site.xpath('//table[@class="allergentab"]/tr/td/span[@class="allergenleft"]/text()').extract()
			product_details_text_3_allergene_value = site.xpath('//table[@class="allergentab"]/tr/td/span[@class="allergenright"]/text()').extract()
			#print product_details_text_3_allergene_key
			#print product_details_text_3_allergene_value
			
			details_text_3_allergene_key = map(lambda str:str.strip(),product_details_text_3_allergene_key)
			details_text_3_allergene_value = map(lambda str:str.strip(),product_details_text_3_allergene_value)
			details_text_3_allergene_key = filter(None,details_text_3_allergene_key)
			details_text_3_allergene_value = filter(None,details_text_3_allergene_value)
			product_details_text_3_allergene = dict(zip(details_text_3_allergene_key, details_text_3_allergene_value))

			product_details_text_3['Allergene'] = product_details_text_3_allergene
			p_zutaten_allergene = product_details_text_3
			
			#print product_details_text_3_allergene
			
			product_details_text_4_key = site.xpath('//div[@id="product_details_text" and @detail_id="4"]/div/div/div/div/div/div[@class="details_left"]/text()').extract()
			product_details_text_4_value = site.xpath('//div[@id="product_details_text" and @detail_id="4"]/div/div/div/div/div/div[@class="details_right"]/text()').extract()
			
			#print len(product_details_text_4_value)
			#print product_details_text_4_key
			#print product_details_text_4_value
			details_text_4_key = map(lambda str:str.strip(),product_details_text_4_key)
			details_text_4_value = map(lambda str:str.strip(),product_details_text_4_value)
			details_text_4_key = filter(None,details_text_4_key)
			details_text_4_value = filter(None,details_text_4_value)
			product_details_text_4 = dict(zip(details_text_4_key, details_text_4_value))
			p_inverkehrbringer = product_details_text_4
			
			product_details_text_2_key = site.xpath('//table[@id="nutrients"]/tr/td[2]/text()').extract()
			product_details_text_2_value = site.xpath('//table[@id="nutrients"]/tr/td[3]/text()').extract()
			
			#print len(product_details_text_2_value)
			#print product_details_text_2_key
			#print product_details_text_2_value
			details_text_2_key = map(lambda str:str.strip(),product_details_text_2_key)
			details_text_2_value = map(lambda str:str.strip(),product_details_text_2_value)
			details_text_2_key = filter(None,details_text_2_key)
			details_text_2_value = filter(None,details_text_2_value)
			product_details_text_2 = dict(zip(details_text_2_key[1:], details_text_2_value))
			if(len(product_details_text_2)>0):
				product_details_text_2['N\xe4hrwertangaben'] = 'je 100 g'
			p_nahrwerte = product_details_text_2
			
			il.add_value('details',p_details)
			il.add_value('nahrwerte',p_nahrwerte)
			il.add_value('zutaten_allergene',p_zutaten_allergene)
			il.add_value('inverkehrbringer',p_inverkehrbringer)	
			
			#categories = crawl_url[leftindex:righttindex]
			#product_details = site.xpath('//div[@id="product_details"]').extract()[0].encode('utf-8')
			#product_details_text = site.xpath('//div[@id="product_details_text"]').extract()
			
			#item['title'] = site.xpath('//h1[@class="entry-title"]/text()').extract()
			#item['articleby'] = site.xpath('//div[@class="entry-content"]/p[@style="text-align: right;"]/text()').extract()
			#item['article'] = site.xpath('//div[@class="entry-content"]/blockquote').extract()

			#self.download(image_url, image_name)
			PCOUNT += 1
			print 'Aready crawl products count:', PCOUNT
		return il.load_item()
 
	def download(self, site, name):
		savePath = '/home/digger/mytime/images/'+name
		try:
			u = urllib2.urlopen(site)
			r = u.read()
			#savePath = '/home/digger/mytime/images/'+name
			print 'Download...', savePath  
            		downloadFile = open(savePath, 'wb')  
            		downloadFile.write(r)  
            		u.close()  
            		downloadFile.close()
		except:
			print savePath, 'can not download.'
# Snippet imported from snippets.scrapy.org (which no longer works)
# author: wynbennett
# date  : Jun 21, 2011
 
