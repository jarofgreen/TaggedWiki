from taggedwikitest.taggedwiki.views import *
from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^$', viewListAllSpaces),
	(r'^(?P<spacename>\D+)/p/(?P<pagename>[^\.]+)/edit/$', viewEditPage),
	(r'^(?P<spacename>\D+)/p/(?P<pagename>[^\.]+)/$', viewPage),
	(r'^(?P<spacename>\D+)/list/$', viewListSpace),
	(r'^(?P<spacename>\D+)/newpage/$', viewNewPage),
	(r'^(?P<spacename>\D+)/$', viewListSpace),
)
