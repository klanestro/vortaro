# Create your views here.
from words.models import *
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404

def dict(request,lang,lang2,word):
	word = Word.objects.filter(text=word)[0]
	#word = get_object_or_404(Word, text=word)
	l = LanguageKey.objects.get(code=lang2)
	d = word.text + ": "
	for concept in word.concepts.all():
		for w in concept.words.filter(language=l):
			d += w.text + ", "
	return render_to_response('base.html',{'contents':d})
