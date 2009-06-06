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

from taggedwiki.models import Space, Page
from django.http import Http404

def loadSpaceOr404(f):
	def new_f(*args,**kargs):
		try:
			kargs['space'] = Space.objects.get(Slug=kargs['space'])
		except Space.DoesNotExist:
			raise Http404()
		return f(*args,**kargs)
	return new_f

def loadPageOr404(f):
	def new_f(*args,**kargs):
		try:
			kargs['page'] = Page.objects.get(Slug=kargs['page'], Space=kargs['space'])
		except Page.DoesNotExist:
			raise Http404()
		return f(*args,**kargs)
	return new_f
