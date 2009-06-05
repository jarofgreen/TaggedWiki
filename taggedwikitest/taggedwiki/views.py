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
from django import forms
from django.template import RequestContext
from django import forms
from django import template
from cgi import escape
from random import randint
import re

def viewListAllSpaces(request):
	return render_to_response('allSpaces.html',{'spaces':Space.objects.all(),},context_instance=RequestContext(request))

def viewListSpace(request,spacename):
	try:
		space = Space.objects.get(Slug=spacename)
	except Space.DoesNotExist:
		raise Http404()
	return render_to_response('space.html',{'space':space,'pages':Page.objects.filter(Space=space),},context_instance=RequestContext(request))

  
def viewListPagesWithTagAjax(request, spacename, tagname):
	try:
		space = Space.objects.get(Slug=spacename)
	except Space.DoesNotExist:
		raise Http404()
	try:
		tag = Tag.objects.get(Title=tagname)
	except Tag.DoesNotExist:
		raise Http404()
	pages = Page.objects.filter(Space=space,Tags=tag)
	return render_to_response('pageList.html',{'pages':pages,},context_instance=RequestContext(request))

def viewPage(request,spacename,pagename):
	try:
		space = Space.objects.get(Slug=spacename)
	except Space.DoesNotExist:
		raise Http404()
	try:
		page = Page.objects.get(Slug=pagename, Space=space)
	except Page.DoesNotExist:
		raise Http404()		
	outPages = []
	tags = Tag.objects.filter(page__Space=space)
	# get body, escape for html
	body = " "+escape(page.Body).replace("\n","<br/>")+" " # extra spaces are so tags at start and end are matched
	# pass 1: for every tag we find in our body, store the first position it occurs (if it does) and add to outPages
	for tag in tags:
		tag.LocationInBody = -1
		regex = escape(tag.Title).replace('\\','\\\\').replace('.','\\.').replace('^','\\^').replace('$','\\$').replace('*','\\*').replace('+','\\+').replace('{','\\{').replace('[','\\[').replace(']','\\]').replace('|','\\|').replace('(','\\(').replace(')','\\)') # escaping all special chars in a regular expression		
		regexObj = re.compile('\W'+regex+'\W' , re.IGNORECASE)
		regexMatch = regexObj.search( body )
		if regexMatch:
			for outPage in Page.objects.filter(Space=space, Tags=tag):
				if not outPage in outPages and not outPage == page: # if not already in list and not ourselves
					outPages.append(outPage)
			tag.LocationInBody = regexMatch.start()+1
	# pass 2: Now put in HTML for each tag
	tags = sorted([t for t in tags if t.LocationInBody > -1], key=lambda obj: obj.LocationInBody)
	offset = 0
	for tag in tags:
		html = '<span class="tag" title="'+escape(tag.Title, True)+'"></span>'
		body = body[0:tag.LocationInBody+offset]+html+body[tag.LocationInBody+offset:]
		offset = offset + len(html)
	return render_to_response('viewPage.html',{'space':space,'page':page,'outPages':outPages,'body':body},context_instance=RequestContext(request))

class EditPageForm(forms.Form):
	Title = forms.CharField(required=True)
	Body = forms.CharField(widget=forms.Textarea,required=True)
	AddANewTag = forms.CharField(widget=forms.Textarea,required=False)

def viewEditPage(request,spacename,pagename):
	try:
		space = Space.objects.get(Slug=spacename)
	except Space.DoesNotExist:
		#raise Http404()
		print ""
	try:
		page = Page.objects.get(Slug=pagename, Space=space)
	except Page.DoesNotExist:
		raise Http404()
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

def viewNewPage(request,spacename):
	try:
		space = Space.objects.get(Slug=spacename)
	except Space.DoesNotExist:
		#raise Http404()
		print ""
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



