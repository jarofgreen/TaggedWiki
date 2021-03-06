#Copyright (C) 2009 James (james at jarofgreen dot co dot uk)
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Lesser General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Lesser General Public License for more details.
#
#You should have received a copy of the GNU Lesser General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

from taggedwiki.views import *
from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^$', viewListAllSpaces),
	(r'^(?P<space>\D+)/p/(?P<page>[^\.]+)/edit/$', viewEditPage),
	(r'^(?P<space>\D+)/p/(?P<page>[^\.]+)/$', viewPage),
	(r'^(?P<space>\D+)/list/$', viewListSpace),
	(r'^(?P<space>\D+)/newpage/$', viewNewPage),
	(r'^(?P<space>\D+)/t/(?P<tagname>.+)/ajax/$', viewListPagesWithTagAjax),
	(r'^(?P<space>\D+)/$', viewListSpace),

)
