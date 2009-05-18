from django.conf.urls.defaults import *
from taggedwikitest.taggedwiki.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^taggedwikitest/', include('taggedwikitest.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),

	(r'^taggedwiki/$', viewListAllSpaces),
	(r'^taggedwiki/(?P<spacename>\D+)/p/(?P<pagename>[^\.]+)/edit/$', viewEditPage),
	(r'^taggedwiki/(?P<spacename>\D+)/p/(?P<pagename>[^\.]+)/$', viewPage),
	(r'^taggedwiki/(?P<spacename>\D+)/list/$', viewListSpace),
	(r'^taggedwiki/(?P<spacename>\D+)/newpage/$', viewNewPage),
	(r'^taggedwiki/(?P<spacename>\D+)/$', viewListSpace),

	(r'^$', viewListAllSpaces),
)
