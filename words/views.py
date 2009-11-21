# Create your views here.
from vortaro.words.models import *
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from vortaro.esperanto import doword

def ajax(request):
	return HttpResponse(doword(request.POST["word"].encode('utf-8')))
