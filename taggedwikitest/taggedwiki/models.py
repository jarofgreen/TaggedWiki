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
from django.db import models
from django.template.defaultfilters import slugify

class Space(models.Model):
	Title = models.CharField(max_length=255)
	Slug = models.SlugField(unique=True)
	Description = models.TextField()
	def __unicode__(self):
        	return self.Title
	class Meta:
        	ordering = ['Title']
	@models.permalink
	def get_absolute_url(self):
 		return ('taggedwiki.views.viewListSpace', None, {'space': self.Slug})
	@models.permalink	
	def get_absolute_new_page_url(self):
 		return ('taggedwiki.views.viewNewPage', None, {'space': self.Slug})


class Tag(models.Model):
	Title = models.CharField(max_length=255)
	def __unicode__(self):
        	return self.Title
	class Meta:
        	ordering = ['Title']

class Page(models.Model):
	Title = models.CharField(max_length=255)
	Slug = models.SlugField(editable=False)
	Body = models.TextField()
	Space = models.ForeignKey(Space, related_name="pages")
	Tags = models.ManyToManyField(Tag, blank=True)
	LastUpdated = models.DateTimeField(auto_now=True, editable=False)
	Created = models.DateTimeField(auto_now_add=True, editable=False)
	LastUpdateIP = models.IPAddressField(editable=False)
	def __unicode__(self):
        	return self.Space.Slug+"/"+self.Title
	class Meta:
        	ordering = ['Title']
	@models.permalink	
	def get_absolute_url(self):
 		return ('taggedwiki.views.viewPage', None, {'space': self.Space.Slug, 'page':self.Slug})
	@models.permalink	
	def get_absolute_edit_url(self):
 		return ('taggedwiki.views.viewEditPage', None, {'space': self.Space.Slug, 'page':self.Slug})
	def save(self, force_insert=False, force_update=False):
		self.Slug = slugify(self.Title)
		super(Page, self).save(force_insert, force_update) # Call the "real" save() method.
		self.addTag(self.Title)
	def addTag(self, tagName):
		tag, created = Tag.objects.get_or_create(Title__iexact=tagName, defaults={'Title':tagName})
		self.Tags.add(tag)
	def removeTag(self, tag):
		self.Tags.remove(tag)
