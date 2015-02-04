#!/usr/bin/python
"""
IRC-RSS-PyBot v1
Leopold von Niebelschuetz-Godlewski

Very simple IRC bot that announces RSS feeds.
"""
import socket, threading, time, re, rss

#SERVER
server        = "127.0.0.1"
port          = 6667
password      = ""
channel       = "#ehteam"

#ADMINISTRATION
admins           = [r"\x6c\x65\x6f", "fang0654", "Arglex", "jsinix", "Securitian", "BigTymer37", "nameless"]
botnick          = "InfoSec_Alert"
nickserv_pass    = ""
check_alert_freq = 1 #HOW OFTEN (IN HOURS) TO CHECK RSS FEEDS

#FEATURES
commands = ["GETALERTS", "RSSFEEDS"]

#MISC
min              = 60
hr               = min*60
day              = hr*12
check_alert_freq = check_alert_freq*hr #EDIT THIS TO CHANGE TO MINUTES, OR EVEN SECONDS?! :)
default_delay    = 3 #SECONDS BETWEEN SENDING ALERTS TO THE IRC SERVER
syntax           = "Syntax: "
space		 = " " * len(syntax)

###CORE FUNCTIONS###
def check_alerts_thread():
	time.sleep(default_delay)
	while 1:
		check_alerts()
		time.sleep(check_alert_freq)

def check_alerts():
	new_alerts = rss.get_alerts() #DIFFERENT FROM THE LOCAL get_alerts METHOD!
	if new_alerts:
		sendmultimsg(channel, new_alerts)
		return 1
	else:
		return 0

def authenticate():
        ircsock.send("PRIVMSG NickServ IDENTIFY " + nickserv_pass + "\n")

def ping(code):
        code = code[6:14]
        ircsock.send("PONG :%s\n" % code)

def sendmsg(chan, msg):
        ircsock.send("PRIVMSG " + chan + " :" + msg + "\n")
	time.sleep(default_delay)

def sendmultimsg(chan, msgs):
        for msg in msgs:
		sendmsg(chan, msg)

def joinchan(chan):
        ircsock.send("JOIN " + chan + "\n")

def get_msg(ircmsg):
	ircmsg = ircmsg[ircmsg.find("PRIVMSG "):]
	ircmsg = ircmsg[ircmsg.find(' :') + len(' :'):]
	return ircmsg.strip()

def get_from(ircmsg):
	return ircmsg.split('!')[0][1:]

def get_to(ircmsg):
	startindex = ircmsg.find("PRIVMSG ")
	ircmsg     = ircmsg[startindex+len("PRIVMSG "):]
	endindex   = ircmsg.find(" :")
	return ircmsg[:endindex]

def help(ircmsg):
	msgto   = get_to(ircmsg)
	msgfrom = get_from(ircmsg)

	msg = ["Hello %s! I can help you with the following commands:" % msgfrom]
	for cmd in commands:
		msg.append(cmd)
	msg.append("\n")
	msg.append("Type '" + botnick  + ": command help' in this channel, or PM me 'command help' and I would be happy to assist you.")

	if (botnick in msgto):
		sendmultimsg(msgfrom, msg)
	else:
		sendmultimsg(msgto, msg)

###ADDITIONAL FEATURES###

#GETALERTS commands[0]
def help_getalerts(ircmsg):
	msgto   = get_to(ircmsg)
	msgfrom = get_from(ircmsg)

	msg = syntax + commands[0]

	if (botnick in msgto):
		sendmsg(msgfrom, msg)
	else:
		sendmsg(msgto, msg)

def get_alerts(ircmsg):
	msgto   = get_to(ircmsg)
	msgfrom = get_from(ircmsg)

	msg = ""
	
	if msgfrom in admins:
		if not check_alerts():
			msg = "Failed to fetch any new RSS posts."
	else:
		msg = "You are not authorized to do this."

	if msg:
		if (botnick in msgto):
			sendmsg(msgfrom, msg)
		else:
			sendmsg(msgto, msg)


#RSSFEEDS commands[1]
def help_rss(ircmsg):
	msgto   = get_to(ircmsg)
	msgfrom = get_from(ircmsg)
	
	msg = [syntax + commands[1] + " ADD http://www.rssfeed.com"]
	msg.append(space + commands[1] + " DEL http://www.rssfeed.com")
	msg.append(space + commands[1] + " LIST")

	if (botnick in msgto):
		sendmultimsg(msgfrom, msg)
	else:
		sendmultimsg(msgto, msg)

def rss_list(ircmsg):
	msgto   = get_to(ircmsg)
	msgfrom = get_from(ircmsg)

	msg = [feed.strip() for feed in open(".rssfeeds").readlines()]

	if (botnick in msgto):
		sendmultimsg(msgfrom, msg)
	else:
		sendmultimsg(msgto, msg)

def rss_add(ircmsg):
	msgto   = get_to(ircmsg)
	msgfrom = get_from(ircmsg)

	if msgfrom in admins:
		ircmsg = get_msg(ircmsg)
		link = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", ircmsg)
		if link:
			link = link[0]
			if link not in open(".rssfeeds").read():
				open(".rssfeeds", 'a').write(link+'\n')
				msg = "Successfully added %s to the RSS feeds." % link
			else:
				msg = "This RSS feed is already in the list."
		else:
			msg = "That link is invalid."
	else:
		msg = "You are not authorized to do this."

	if (botnick in msgto):
		sendmsg(msgfrom, msg)
	else:
		sendmsg(msgto, msg)

def rss_del(ircmsg):
	msgto   = get_to(ircmsg)
	msgfrom = get_from(ircmsg)

	msg = "That link is invalid."	

	if msgfrom in admins:
		ircmsg = get_msg(ircmsg)
		words  = ircmsg.split(' ')
		rssfeeds = [feed.strip() for feed in open('.rssfeeds', 'r').readlines()]
		for word in words:
			for feed in rssfeeds:
				if word == feed:
					rssfeeds = [feed for feed in rssfeeds if word not in feed]
					open('.rssfeeds', 'w').write('\n'.join(rssfeeds)+'\n')
					msg = "Successfully deleted %s from the RSS feeds." % feed
	else:
		msg = "You are not authorized to do this."

	if (botnick in msgto):
		sendmsg(msgfrom, msg)
	else:
		sendmsg(msgto, msg)

###FUN STARTS HERE!###
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, port))
if password: ircsock.send("PASS " + password + "\n")
ircsock.send("USER " + botnick + " " + botnick + " " + botnick + " :The Eh Team's InfoSec_Alert PyBot v1.0\n")
ircsock.send("NICK " + botnick + "\n")

joinchan(channel)

alert_checker = threading.Thread(target=check_alerts_thread)
alert_checker.daemon = True
alert_checker.start()

while 1:
	ircmsg = ircsock.recv(1024)
	ircmsg = ircmsg.strip('\n\r')
	print ircmsg

	if get_from(ircmsg) != botnick:
		if "PING :" in ircmsg:
			ping(ircmsg[ircmsg.find("PING :"):])
	
		if "This nickname is registered and protected" in ircmsg:
			authenticate()
		
		if botnick in ircmsg and "HELP" in ircmsg.upper() and commands[0] in ircmsg.upper():
			help_getalerts(ircmsg)
		elif botnick in ircmsg and "HELP" in ircmsg.upper() and commands[1] in ircmsg.upper():
			help_rss(ircmsg)
		elif botnick in ircmsg and "HELP" in ircmsg.upper():
			help(ircmsg)
		elif botnick in ircmsg and commands[0] in ircmsg.upper():
			get_alerts(ircmsg)
		elif botnick in ircmsg and commands[1] in ircmsg.upper() and "ADD" in ircmsg.upper():
			rss_add(ircmsg)
		elif botnick in ircmsg and commands[1] in ircmsg.upper() and "DEL" in ircmsg.upper():
			rss_del(ircmsg)
		elif botnick in ircmsg and commands[1] in ircmsg.upper() and "LIST" in ircmsg.upper():
			rss_list(ircmsg)