#!/usr/bin/python
#encoding: utf-8

'''
A spider for collecting pictures of a specified author of TuChong Site
Based on https://github.com/annieqt/Tuchong-Spider
Author: Eric Wang
'''

import os
import sys
import time
import string
import json
import logging
from pprint import pprint as pretty
import argparse
from platform import python_version
if python_version()[0] < '3':
	from urllib import urlopen
else:
	from urllib.request import urlopen
from bs4 import BeautifulSoup as bs

## debug, info, warnning, error, critical
logging.basicConfig(level = logging.DEBUG, format = "%(levelname)s %(asctime)s [%(filename)s][%(lineno)d][%(funcName)s] %(message)s")
log = logging.getLogger()

class Tuchong_Spider:
	def __init__(self, url, num):
		if url.endswith('/'):
			url = url[:-1]
		self.url = url
		self.num = num
		self.author = ''

	## get html content of an url
	def get_content(self, url):
		content = ''
		try:
			content = urlopen(url).read()
		except Exception as e:
			log.error(e)
			log.error('download %s error' % (url))

		return content

	## get pics url list
	def parse_post(self, post_url):
		html = self.get_content(post_url)
		'''
		html content ex:
		<img src="https://photo.tuchong.com/990878/f/13914842.jpg" class="img-responsive copyright-contextmenu" data-copyright="&copy;版权所有" alt="" />
		<img src="https://photo.tuchong.com/990878/f/13914843.jpg" class="img-responsive copyright-contextmenu" data-copyright="&copy;版权所有" alt="" />
		'''
		soup = bs(html, 'html.parser')
		pics = []
		for pic in soup.find_all("img", attrs = {"class":"img-responsive copyright-contextmenu"}):
			pics.append(pic.get('src'))

		author = soup.find('meta', attrs = {'name':'author'})['content']
		self.author = author

		log.info('post %s contains %d pics' % (post_url, len(pics)))
		return pics
		
	#Save image of img_url with index as file name in the folder
	def save_img(self, url, post_id, index):
		path = 'photo' + os.sep + self.author
		if not os.path.exists(path):
			os.makedirs(path)
		target = path + os.sep + str(post_id) + '_' + str(index) + '.jpg'
		log.info('saving picture %s' % (target))

		img = urlopen(url).read()
		out = open(target, 'wb')
		out.write(img)
		out.close()

	#spider entrance
	def start_site(self):
		log.info('Collecting the most recent %s post(s) from site %s' % (self.num, self.url))

		## get author and site_id
		soup = bs(self.get_content(self.url), 'html.parser')

		profile = soup.find("div", attrs={"class":"profile-name"})
		self.author = profile.h2.get_text().strip()

		post_collages = soup.find("div", attrs={"class":"post-collages"})
		site_id = post_collages.get('data-site-id')

		## get posts info
		today = time.strftime("%Y-%m-%d")
		api = 'http://tuchong.com' + '/rest/sites/%s/posts/%s?limit=%s' %(site_id, today, self.num)
		posts_json_str = self.get_content(api)
		'''
		a json string, contains the folloing fields
		{
			'posts':[
						{
							"post_id":"13736674",
							"url":"http:\/\/lucici.tuchong.com\/13736674\/",
							"site_id":"990878",
							"author_id":"990878",
							"published_at":"2016-11-18 18:43:24",
							"favorites":224,
							"comments":31,
							"title":"\u300a\u5f13\u00b7\u72ac\u591c\u53c9\u00b7\u6854\u6897\u300b\u5b88\u671b\u7248",
							"image_count":16,
							"images":[
								{"img_id":13914842,"user_id":990878,"title":"001","excerpt":"","width":2500,"height":1442},
								....
							],
							'site':{
							}
						}
			]
		}
		'''
		parsed_json = json.loads(posts_json_str)
		posts = parsed_json['posts']

		total = 0
		for post in posts:
			pics = self.parse_post(post['url'])
			i = 0
			for pic in pics:
				self.save_img(pic, post['post_id'], i)
				i = i + 1
				total = total + 1
			log.info('saved %s pics for post %s' % (str(i), str(post['post_id'])))
		log.info('total pics: %s' % (str(total)))

	def start_post(self):
		log.info('Collecting all photos from post: %s' % (self.url))

		post_id = self.url.split('/')[-1]

		i = 0
		pics = self.parse_post(self.url)
		for pic in pics:
			self.save_img(pic, post_id, i)
			i = i + 1
		log.info('total pics: %s' % (str(i)))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'tuchong spider')
	parser.add_argument('-t', action = 'store', dest = 'type', default = 'site', type = str, help = 'url type: site|post')
	parser.add_argument('-u', action = 'store', dest = 'url', default = 'https://lucici.tuchong.com', type = str, help = 'url')
	parser.add_argument('-n', action = 'store', dest = 'num', default = 1, type = int, help = 'num of posts, used when type is site')
	arg = parser.parse_args()

	spider = Tuchong_Spider(arg.url, arg.num)
	if arg.type == "site":
		spider.start_site()
	elif arg.type == "post":
		spider.start_post()
	else:
		log.fatal('%s not supported' % (arg.type))

	sys.exit(0)

