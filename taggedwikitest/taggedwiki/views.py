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
from taggedwikitest.taggedwiki.models import *
from django import forms
from django.template import RequestContext
from django import forms
from django import template
from cgi import escape
from random import randint

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
	tags = Tag.objects.all()
	# get body, as html  TODO: Escape all Entities ...
	body = escape(page.Body).replace("\n","<br/>")
	# pass 1: for every tag we find in our body, add all pages with this tag to our list AND replace it with a special char and store that special char on the tag
	for tag in tags:
		tag.SpecialChar = False
		tagTitleEscaped = escape(tag.Title);
		if tagTitleEscaped in body:
			for outPage in Page.objects.filter(Space=space, Tags=tag):
				if not outPage in outPages and not outPage == page: # if not already in list and not ourselves
					outPages.append(outPage)
			char = unichr(randint(130,65000)) # find a special char to use as a placeholder
			while char in body:
				char = unichr(randint(130,65000)) # 130 cos the ones below 128 have a higher chance of being used already.
			tag.SpecialChar = char
			body = body.replace(tagTitleEscaped, char+tagTitleEscaped)
	# pass 2: for every tag with a special char, replace that special char with the HTML
	# why do we do two passes? If you have a tag "lass" then it might find the "class" in the HTML below and put HTML into HTML - causing serious breakage
	for tag in tags:
		if tag.SpecialChar:
			body = body.replace(tag.SpecialChar, '<span class="tag" title="'+escape(tag.Title, True)+'"></span>')
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
		#raise Http404()
		print ""
	if request.method == 'POST':
		form = EditPageForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			page.Title = cd['Title'].strip()
			page.Body = cd['Body']
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
			page = Page(Space=space, Title=cd['Title'], Body=cd['Body'])
			page.save()
			for newtag in cd['AddANewTag'].split("\n"):
				if newtag.strip():
					page.addTag(newtag.strip())
			return HttpResponseRedirect(page.get_absolute_url())
	else:
		form = EditPageForm( )
	return render_to_response('editPage.html', {'space':space,'form': form,},context_instance=RequestContext(request))



