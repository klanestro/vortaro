# Create your views here.
from vortaro.words.models import *
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from vortaro.esperanto import doword
import urllib

def ajax(request, word):
	cback = request.GET["callback"]
	#word = base64.b64decode(word)
	#word = urllib.quote(word)
	#print text
	#word = "boom"
	jsonp = cback+'({"text":"'+doword(word.encode('utf-8')).strip()+'"})'
	return HttpResponse(content=jsonp, mimetype='application/javascript')
