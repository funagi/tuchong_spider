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
	def __init__(self, url, num_of_pic):
		self.url = url
		self.num_of_pic = int(num_of_pic)
		self.author = ''
		self.site_id = ''
		self.api = ''
		self.today = ''

	## get html content of an url
	def get_content(self, url):
		content = ''
		try:
			content = urlopen(url).read()
		except Exception as e:
			log.error(e)
			log.error('download %s error' % (url))

		return content

	def init(self):
		soup = bs(self.get_content(self.url), 'html.parser')

		profile = soup.find("div", attrs={"class":"profile-name"})
		self.author = profile.h2.get_text().strip()

		post_collages = soup.find("div", attrs={"class":"post-collages"})
		self.site_id = post_collages.get('data-site-id')

		self.today = time.strftime("%Y-%m-%d")
		self.api = 'http://tuchong.com' + '/rest/sites/%s/posts/%s?limit=%s' %(self.site_id, self.today, self.num_of_pic)

	## get posts url list of each post
	def parse_posts(self, posts_json_str):
		parsed_json = json.loads(posts_json_str)
		posts = parsed_json['posts']
		posts_info = []
		for post in posts:
			info = {'url': post['url'],
					'num': post['image_count'],
					'id': post['post_id']}
## 			info['url'] = post['url']
## 			info['num'] = post['image_count]'
## 			info['id'] = post['post_id]'
			posts_info.append(info)
		return posts_info

	## get pics url list
	def parse_post(self, post_url):
		html = self.get_content(post_url)
## 		sys.stdout.write(html)
		soup = bs(html, 'html.parser')
		pics = []
		for pic in soup.find_all("img", attrs = {"class":"img-responsive copyright-contextmenu"}):
			pics.append(pic.get('src'))

		log.debug(pics)
		return pics
		
	#Save image of img_url with index as file name in the folder
	def save_img(self, url, post_id, index):
		img = urlopen(url).read()

		path = 'photo' + os.sep + self.author
		if not os.path.exists(path):
			os.makedirs(path)
		target = path + os.sep + str(post_id) + '_' + str(index) + '.jpg'

		out = open(target, 'wb')
		out.write(img)
		out.close()

		log.info('saving picture %s' % (target))

	#spider entrance
	def start(self):
		log.info('Start Collecting the most recent %s photos from: %s' % (self.num_of_pic, self.url))

		## set private fields
		self.init()

		log.debug(self.api)

		posts_json = self.get_content(self.api)
## 		sys.stdout.write(posts)
		posts = self.parse_posts(posts_json)
		log.debug(posts)

		total = 0
		for post in posts:
			pics = self.parse_post(post['url'])
			i = 0
			for pic in pics:
				self.save_img(pic, post['id'], i)
				i = i + 1
				total = total + 1
			log.info('saved %s pics for post %s' % (str(i), str(post['id'])))
		log.info('total pics: %s' % (str(total)))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'tuchong spider')
	parser.add_argument('-u', action = 'store', dest = 'url', default = 'https://lucici.tuchong.com', type = str, help = 'site url')
	parser.add_argument('-n', action = 'store', dest = 'num', default = 1, type = int, help = 'pic num')
	arg = parser.parse_args()

	spider = Tuchong_Spider(arg.url, arg.num)
	spider.start()

	sys.exit(0)

