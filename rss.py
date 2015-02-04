#!/usr/bin/python
"""
IRC-RSS-PyBot v1
Leopold von Niebelschuetz-Godlewski

Very simple IRC bot that announces RSS feeds.
"""
import HTMLParser, feedparser, re

max_size = 454

RSS_FEEDS = """
http://rss.packetstormsecurity.com/news
http://www.reddit.com/r/netsec/.rss
http://www.reddit.com/r/securityCTF/.rss
http://rss.packetstormsecurity.com/files
https://ctftime.org/event/list/upcoming/rss/
"""

try:
	feeds = [feed.strip() for feed in open(".rssfeeds").readlines() if feed]
except:
	feeds = [feed.strip() for feed in RSS_FEEDS.split('\n') if feed]
	for feed in RSS_FEEDS.split('\n'):
		if feed:
			link = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", feed)
			print feed
			if link:
				link = link[0]
				open(".rssfeeds", 'a').write(link+'\n')

strip_byte  = re.compile(r"[\x90-\xff]")
strip_html  = re.compile(r"<.*?>")
utf_convert = HTMLParser.HTMLParser()

def get_alerts():
	alerts = []
	try:
		oldrss = open(".oldrss").read()
	except:
		open(".oldrss",'w').write('')
		oldrss = ''
	for feed in feeds:
		try:
			RSS    = feedparser.parse(feed)
			posts  = [post for post in RSS.entries]
		except:
			alerts.append("Error trying to parse RSS feed: %s" % feed)
			continue

		for post in posts:
			if post.title.encode('utf8') not in oldrss:
				if post.link:
					link = '[' + post.link + ']'
				else:
					link = "Link is unavailable."
				if post.title:
					title = post.title + ":"
				else:
					title = "Title is unavailable."
				if post.description:
					description = post.description
				else:
					description = "Description is unavailable."
				msg = "%s %s %s" % (link, title, description)
				msg = msg.replace(' \n\n', ' ').replace('\n\n', ' ').replace('\n', ' ')
				msg = strip_html.sub('', msg) #strips HTML tags
				msg = strip_byte.sub('', msg) #strips raw bytes
				msg = utf_convert.unescape(msg) #translates UTF encoded strings to ASCII
				if len(msg) > max_size:
					index = 0
					while 1:
						if not len(msg): break
						pmsg = msg[0:max_size]
						alerts.append(pmsg.encode('utf8'))
						msg = msg[max_size:]
				else:
					alerts.append(msg.encode('utf8'))
				open(".oldrss", 'a').write(post.title.encode('utf8')+'\n')
	return alerts

if __name__ == "__main__":
   for alert in get_alerts(): print alert