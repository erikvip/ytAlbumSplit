#!/usr/bin/python
# -*- coding: utf-8 -*-
__version__ = "0.3.1"
__author__ = "Erik Phillips <erikvip@gmail.com>"
__license__ = "GPLv3"


outputDir = "C:\\youtube\\albums"

import os
import sys
import traceback
import pprint
import logging
import urllib
import time
import urlparse
import re

# from PyQt4 import QtGui

# Ensure lib added to path, before any other imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib/'))

# Included libs
import musicbrainzngs as mb
#import pafy

#import ytalbumgui as gui
from feedparser import *

from subprocess import call

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', filename='run.log')

def main():

	#yta = YtAlbum()
	#yta.query = 'Savant ISM'
	#res = yta.fi`ndRelease()

	if len(sys.argv) < 2:
		print "You must specify a youtube URL\n Usage: mbcue.py <youtube URL>"
		sys.exit(1)

	url = sys.argv[1]

	# Parse the youtube URL and extract the video_id from v=
	urldata = urlparse.urlparse(url)
	qs = urlparse.parse_qs(urldata.query)
	video_id = qs["v"][0]
	
	# Query Youtube to find the video title
	api = 'https://gdata.youtube.com/feeds/api/videos?q=%s&v=2' % urllib.quote_plus(video_id)

	logging.info('Youtube API URL: %s' % api)

	yt = feedparser.parse(api)

	logging.info('Youtube API Response: \n %s' % yt)

	if yt['entries'] == False:
		print "No videos found"
		sys.exit(1)

	title = yt['entries'][0]['title']

	logging.info('Raw title: %s' % title)

	# Remove anything betwen parenthesis or brackets
	# This is to remove (FULL ALBUM) or [COMPLETE ALBUM] and similar..
	title = re.sub("[\(\[].*[\)\]]", "", title).encode('utf-8').strip()

	logging.info('Scrubbed title: %s' % title)


	# We now have 'title' and URL attributes

	# Download the youtube video using youtube-dl and convert it to an mp3
	cmd = 'bin/youtube-dl.exe -f "best" -o "%(id)s.%(ext)s" -x --audio-format "mp3" ' + url
	logging.info('Youtube-dl command line: %s' % cmd)
	#call(cmd)

	# Now generate the CUE sheet
	yta = YtAlbum()
	yta.query = title

#	for i in range(0, 100):
		#while True:
		#	try:
	cuesheet = yta.findRelease()
		#	except:
		#		continue
		#	break

	cuesheet = cuesheet.encode('utf-8').strip()

	logging.info('Cuesheet:\n %s' % cuesheet)

	# Save the cue file to (video_id).cue
	f = open(video_id + ".cue", "w")
	f.write(cuesheet)
	f.close()

	# Now run mp3splt
	#spltcmd = 'bin/mp3splt.exe -c '+video_id+'.cue -T 2 -o "@b - @n2 - @t" ' + video_id + ".mp3"
	splitcmd = "bin/mp3splt/mp3splt.exe -c %s.cue -T 2 -o \"@b - @n2 - @t\" -d \"%s\\%s\" %s.mp3" % (video_id, outputDir, title, video_id)
	logging.info('mp3splt command line: %s' % splitcmd)
	call(splitcmd)

	# Cleaup
	#os.remove(video_id + ".mp3")
	#os.remove(video_id + ".cue")


class YtAlbum:
	def findRelease(self):
		name = self.query
		
		results = []

		limit = 1

		chars = set('!?*')
		if any((c in chars) for c in name):
		    name = '"'+name+'"' 
		    
		mb.set_useragent("headphones","1.0","https://github.com/erikvip/headphones")
		mb.set_rate_limit(True)
		res = mb.search_releases(query='artist:'+name,limit=limit)

		logging.info('musicbrainz query: %s' % name)
		logging.info('musicbrainz response: \n %s' % res)

		for a in res['release-list']:
			album = {
				'id': a['id'], 
				'artist': a['artist-credit-phrase'], 
				#'date': a['date'], 
				#'country': a['country'], 
				'status': a['status'], 
				'title' : a['title'],
				'tracks' : []
			}

			disc = mb.get_release_by_id(a['id'], ["media","recordings"])

			output = "TITLE \"%(artist)s - %(title)s\"\n" % album
			output += "PERFORMER \"%(artist)s\"\n" % album
			output += "FILE \"%s.mp3l\" MP3\n" % a['id']

			time = 0
			minutes = 0
			seconds = 0

			logging.info('musicbrainz release response: \n %s' % disc)

			for d in disc['release']['medium-list']:
				
				for t in d['track-list']:
					track = {
						'position': str(t['position'].zfill(2)), 
						'title' : t['recording']['title'].encode('ascii', 'ignore'),
						'minutes' : str(minutes).zfill(2), 
						'seconds ': seconds,
						'duration' : "%s:%s" % (str(minutes).zfill(2), seconds), 
						'seconds' : time
					}

					output += "  TRACK %(position)s AUDIO\n" % track
					output += "    TITLE \"%(title)s\"\n" % track
#					if t['position'] == "1":
#						output += "    INDEX 00 00:00:00\n"
					output += "    INDEX 01 %(duration)s:00\n" % track


					# Convert recording time to Minutes:Seconds
					time += int(t['length']) / 1000
					minutes = time/60
					seconds = str(time%60)[:2].zfill(2)
					

#					logging.info('Track #%(position)s \tDuration: %(duration)s [%(seconds)ss] \t%(title)s' % track)

			results.append(album)

					

		#return results
		return output
				
# main() when invoked from the shell
if __name__ == '__main__':

		main()


	