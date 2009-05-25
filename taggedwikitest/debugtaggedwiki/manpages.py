from taggedwikitest.taggedwiki.models import *
import os


def importPages():
	try:
		space = Space.objects.get(Slug='man')
	except Space.DoesNotExist:
		space = Space(Title='Man Pages', Slug='man')
		space.save()
	commands = ['ls','su','ssh','scp','passwd','whoami','logname','groups','group','finger','delgroup','deluser','crontab','adduser','addgroup','login','newgrp']
	for command in commands:
		try:
			page = Page.objects.get(Title=command, Space=space)
		except Page.DoesNotExist:
			page = Page(Title=command, Space=space)
		with os.popen('man '+command+' | cat') as f:
			txt = '\n'.join(f.readlines());
			txt = ''.join([x for x in txt if ord(x) < 128])
			page.Body = unicode(txt)
		page.save()
		page.addTag(command)
