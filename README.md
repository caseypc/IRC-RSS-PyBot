# IRC-RSS-PyBot
Very simple IRC bot that announces RSS feeds every hour (by default). Can be forced to check for alerts using the GETALERTS command.

Usage:

https://dl.dropboxusercontent.com/u/64461957/IRC-RSS-PyBot%20Usage.png

Configuration:

1. Under "pybot.py" you must configure the server information between lines 11-14, and the administration information between lines 17-20.
2. Under "rss.py" you must configure the the RSS feeds between lines 13-17.
3. To run as a background process on a Linux server, you can simply run the following command: "nohup python pybot.py > /dev/null 2>&1 &". This will also redirect the STDOUT in order to conserve disk space.
