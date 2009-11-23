import urllib

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail

from vortaro.words.models import *
from vortaro.words.emails import *
from vortaro.words.forms import *

def email2username(email):
	return email.replace("@","").replace(".","")[:30]

def register(request):
	sent = False
	error = ""
	email = ""
	form = RegisterForm()
	if request.POST:
		form = RegisterForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data["email"]
			username = email2username(email)
			try:
				old_user = Editor.objects.get(username=username)
			except Editor.DoesNotExist:
				old_user = False
			if old_user:
				error = "A user with this email already exists."
			else:
				password = User.objects.make_random_password(length=10)
				editor = Editor(email=email,username=username)
				editor.set_password(password)
				editor.save()
				subject = "Thank you for becoming a new vortaro.co.cc editor"
				body = email_register % (email, password)
				send_mail(subject, body, 'noreply@vortaro.co.cc',[email],
				         fail_silently=False)
				sent = True
		else:
			error = "Please enter a valid email"
		
	return render_to_response("register.html", {
	"email":email,
	"error":error,
	"sent":sent})
	
def logmein(request):
	email = ""
	error = ""
	if request.POST:
		email = request.POST['email']
		password = request.POST['password']
		user = authenticate(email=email, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				next = "/home"
				if "next" in request.GET:
					next = request.GET["next"]
				return HttpResponseRedirect(next)
			else:
				error = "This account is disabled."
		else:
			error = "Email or password is incorrect."
	return render_to_response("login.html", {
	"email":email,
	"error":error})

def logmeout(request):
	logout(request)
	return HttpResponseRedirect("/about")
	
def about(request):
	return render_to_response("about.html", {
	"user":request.user})
	
def settings(request):
	user = request.user
	if not user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	error = ""
	if request.POST:
		form = SettingsForm(request.POST)
		if form.is_valid():
			user.first_name = form.cleaned_data["first_name"]
			user.last_name = form.cleaned_data["last_name"]
			user.languages = form.cleaned_data["languages"]
			if form.cleaned_data["password"]:
				user.set_password(form.cleaned_data["password"])
			user.save()
			return HttpResponseRedirect("/home?message=updated")
		else:
			error = "Invalid data"
	form = SettingsForm({
	"first_name":user.first_name,
	"last_name":user.last_name,
	#"language":user.language.id,
	"languages":[x.id for x in user.languages.all()]
	})
	return render_to_response("editor/settings.html", {
	"user":user,
	"error":error,
	"form":form})

def homeview(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	message = ""
	if "message" in request.GET:
		# If you are redirected here from successfully updating your profile
		if request.GET["message"] == "updated":
			message = "Profile updated"
	return render_to_response("editor/home.html", {
	"user":request.user,
	"message":message
	})

def search(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	return render_to_response("editor/search.html", {
	"user":request.user
	})
