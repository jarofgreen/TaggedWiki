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

def viewListAllSpaces(request):
	return render_to_response('allSpaces.html',{'spaces':Space.objects.all(),},context_instance=RequestContext(request))

def viewListSpace(request,spacename):
	try:
		space = Space.objects.get(Slug=spacename)
	except Space.DoesNotExist:
		raise Http404()
	return render_to_response('space.html',{'space':space,'pages':Page.objects.filter(Space=space),},context_instance=RequestContext(request))

    
def html_escape(text):
	"""Produce entities within text.  http://wiki.python.org/moin/EscapingHtml"""
	html_escape_table = {
		"&": "&amp;",
		'"': "&quot;",
		"'": "&apos;",
		">": "&gt;",
		"<": "&lt;",
	 }
	L = []
	for c in text:
		L.append(html_escape_table.get(c, c))
	return "".join(L)

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
	t = template.Template('{{ body|linebreaks }}')
	c = template.Context({'body':  page.Body })
	body = t.render(c)  # this will do all new line's and escaping silly characters for us
	for tag in Tag.objects.all():
		if tag.Title in page.Body:
			for outPage in Page.objects.filter(Space=space, Tags=tag):
				if not outPage in outPages and not outPage == page: # if not already in list and not ourselves
					outPages.append(outPage)
			body = body.replace(tag.Title, '<span class="tag" title="'+html_escape(tag.Title)+'"></span>'+tag.Title)
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



