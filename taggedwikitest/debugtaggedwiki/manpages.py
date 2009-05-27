from taggedwikitest.taggedwiki.models import *
import os


def importPages():
	try:
		space = Space.objects.get(Slug='man')
	except Space.DoesNotExist:
		space = Space(Title='Man Pages', Slug='man')
		space.save()
	commands = []
	for directory in ['/usr/share/man/man1','/usr/share/man/man2','/usr/share/man/man3','/usr/share/man/man4','/usr/share/man/man5','/usr/share/man/man6','/usr/share/man/man7','/usr/share/man/man8']:
		for file in os.listdir(directory):
			if '.gz' in file:
				command = file.split('.').pop(0)
				if not command in commands:
					commands.append(command)
	for command in commands:
		with os.popen('man '+command+' | cat') as f:
			txt = '\n'.join(f.readlines());
			txt = ''.join([x for x in txt if ord(x) < 128])
			txt = unicode(txt)
		if txt:
			try:
				page = Page.objects.get(Title=command, Space=space)
			except Page.DoesNotExist:
				page = Page(Title=command, Space=space)
			page.Body = txt
			page.save()
			page.addTag(command)
