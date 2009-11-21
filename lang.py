# -*- coding: utf-8 -*-
from UserDict import DictMixin
from vortaro.words.models import *

class _dict(DictMixin):
	def __init__(self,lang):
		self.langs = ['en','eo','ru']
		self.langnames = ['English','Esperanto','Русский']
		self.text = {
		'menu_dictionary':['Dictionary','Vortaro','Словарь'],
		'menu_project':['Project','Projekto','Проект'],
		'available_languages':['Available languages','Haveblaj lingvoj','Доступные языки'],
		'search_in_dictionary':['Search in dictionary','Serĉi en vortaro','Искать в словаре'],
		'search':['Search','Serĉi','Искать']
		}
		self.l = self.langs.index(lang)
		self.lang = lang
	def __getitem__(self, key):
		if key in self.langs: # if given language code
			return self.langnames[self.langs.index(key)]
		text = self.text[key][self.l]
		if text == '':
			text = self.text[key][0] + " [en]"
		return text
	def languages(self):
		return zip(self.langs, self.langnames)
		
def eo(word, lang):
	#lang = LanguageKey.objects.get(code=lang)
	
	def find(word):
		w = Word.objects.filter(text=word,language=lang)
		if w: return w[0]
	
	# Without modification
	w = find(word)
	if w: return w
	
	# Try without plural and accusative
	if word.endswith('n') or word.endswith('j') or word.endswith('jn'):
		w = find(word.rstrip('jn'))
		if w: return w
	
	# Verbs
	ends = ['as','is','os','us','u']
	for end in ends:
		if word.endswith(end):
			w = find(word[:-len(end)] + 'i')
			if w: return w
	
	return None
