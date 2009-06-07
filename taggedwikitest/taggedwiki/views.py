#Copyright (C) 2009 James (james at jarofgreen dot co dot uk)
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Lesser General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.#
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Lesser General Public License for more details.
#
#You should have received a copy of the GNU Lesser General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from taggedwiki.models import *
from django.template import RequestContext
from django import forms
from django import template
from cgi import escape
from random import randint
import re
import taggedwiki.decorators as decorators
 
def viewListAllSpaces(request):
	return render_to_response('allSpaces.html',{'spaces':Space.objects.all(),},context_instance=RequestContext(request))

@decorators.loadSpaceOr404
def viewListSpace(request,space):
	return render_to_response('space.html',{'space':space,'pages':Page.objects.filter(Space=space),},context_instance=RequestContext(request))

@decorators.loadSpaceOr404
def viewListPagesWithTagAjax(request, space, tagname):
	try:
		tag = Tag.objects.get(Title=tagname)
	except Tag.DoesNotExist:
		raise Http404()
	pages = Page.objects.filter(Space=space,Tags=tag)
	return render_to_response('pageList.html',{'pages':pages,},context_instance=RequestContext(request))

@decorators.loadSpaceOr404
@decorators.loadPageOr404
def viewPage(request,space,page):
	outPages = []
	tags = set(Tag.objects.filter(page__Space=space)) # set is needed because in seems the enclosed query can return the same tag twice?
	# get body, escape for html
	body = " "+escape(page.Body).replace("\n","<br/>")+" " # extra spaces are so tags at start and end are matched
	# pass 1: for every tag we find in our body, store the first position it occurs (if it does) and add to outPages, counting links as we go
	for tag in tags:
		tag.LocationInBody = -1
		regex = escape(tag.Title).replace('\\','\\\\').replace('.','\\.').replace('^','\\^').replace('$','\\$').replace('*','\\*').replace('+','\\+').replace('{','\\{').replace('[','\\[').replace(']','\\]').replace('|','\\|').replace('(','\\(').replace(')','\\)') # escaping all special chars in a regular expression		
		regexObj = re.compile('\W'+regex+'\W' , re.IGNORECASE)
		regexMatch = regexObj.search( body )
		if regexMatch:
			tag.CountInBody = len ( regexObj.findall(body) ) # TODO: This will undercount if tags are right next to each other with only one character seperating them.
			for outPage in Page.objects.filter(Space=space, Tags=tag):
				if not outPage == page:
					if not outPage in outPages:
						outPage.NumberOfLinks = tag.CountInBody
						outPages.append(outPage)
					else:
						outPageIndex = outPages.index(outPage)
						outPages[outPageIndex].NumberOfLinks = outPages[outPageIndex].NumberOfLinks + tag.CountInBody
			tag.LocationInBody = regexMatch.start()+1
	# pass 2: Now put in HTML for each tag
	tags = sorted([t for t in tags if t.LocationInBody > -1], key=lambda obj: obj.LocationInBody)
	offset = 0
	for tag in tags:
		html = '<span class="tag" title="'+escape(tag.Title, True)+'"></span>'
		body = body[0:tag.LocationInBody+offset]+html+body[tag.LocationInBody+offset:]
		offset = offset + len(html)
	# finally sort results before returning
	outPages = sorted([p for p in outPages], key=lambda obj: obj.NumberOfLinks, reverse=True)
	return render_to_response('viewPage.html',{'space':space,'page':page,'outPages':outPages,'body':body,'tags':tags},context_instance=RequestContext(request))

class EditPageForm(forms.Form):
	Title = forms.CharField(required=True)
	Body = forms.CharField(widget=forms.Textarea,required=True)
	AddANewTag = forms.CharField(widget=forms.Textarea,required=False)

@decorators.loadSpaceOr404
@decorators.loadPageOr404
def viewEditPage(request,space,page):
	if request.method == 'POST':
		form = EditPageForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			page.Title = cd['Title'].strip()
			page.Body = cd['Body']
			page.LastUpdateIP = request.META['REMOTE_ADDR']
			page.save()
			for newtag in cd['AddANewTag'].split("\n"):
				if newtag.strip():
					page.addTag(newtag.strip())
			for removetag in request.POST.getlist('Remove'):
				tag = Tag.objects.get(id=removetag)
				if tag in page.Tags.all():
					page.removeTag(tag)
			return HttpResponseRedirect(page.get_absolute_url())
	else:
		form = EditPageForm(  {  'Title':page.Title, 'Body':page.Body, }  )
	return render_to_response('editPage.html', {'space':space,'page':page,'form': form,},context_instance=RequestContext(request))

@decorators.loadSpaceOr404
def viewNewPage(request,space):
	if request.method == 'POST':
		form = EditPageForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			# todo: check name doesn't already exist!
			page = Page(Space=space, Title=cd['Title'], Body=cd['Body'], LastUpdateIP = request.META['REMOTE_ADDR'])
			page.save()
			for newtag in cd['AddANewTag'].split("\n"):
				if newtag.strip():
					page.addTag(newtag.strip())
			return HttpResponseRedirect(page.get_absolute_url())
	else:
		form = EditPageForm( )
	return render_to_response('editPage.html', {'space':space,'form': form,},context_instance=RequestContext(request))



