# Create your views here.
from vortaro.words.models import *
from vortaro.lang import _dict
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext as _


def search(request, lang):
	lang = request.GET['from']
	lang2 = request.GET['into']
	word = request.GET['word']
	word = Word.objects.filter(text=word)[0]
	#word = get_object_or_404(Word, text=word)
	l = LanguageKey.objects.get(code=lang2)
	d = word.text + ": "
	for concept in word.concepts.all():
		for w in concept.words.filter(language=l):
			d += w.text + ", "
	return dictionary(request, definition=d, lang=lang)

def url(request, url):
	return render_to_response('base.html',{'content':url})

def dictionary(request, lang='en', definition=None):
	langobject = LanguageKey.objects.get(code=lang)
	_ = _dict(lang)
	languages = []
	for l in LanguageKey.objects.all():
		languages.append([l.code,l.names.get(name_in=langobject).text])
	
	return render_to_response('dictionary.html',{
	'content':'',
	'lang':_,
	'active_tab':'dictionary',
	'languages':languages,
	'article':definition
	})
