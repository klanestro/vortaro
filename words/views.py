import urllib

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.http import Http404

from vortaro.words.models import *
from vortaro.words.emails import *
from vortaro.words.forms import *

def messages(request):
	"""
	Inside the request.session dict are two keys: message and error. This
	function returns a dict with just the two. It clears the session ones.
	"""
	messages = {}
	if "message" in request.session:
		messages["message"] = request.session["message"]
		request.session["message"] = ""
	if "error" in request.session:
		messages["error"] = request.session["error"]
		request.session["error"] = ""
	return messages

def register(request):
	email = ""
	form = RegisterForm()
	if request.POST:
		form = RegisterForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data["email"]
			# Create username from email
			username = email.replace("@","").replace(".","")[:30]
			# Generate a random password
			password = User.objects.make_random_password(length=10)
			editor = Editor(email=email,username=username)
			editor.set_password(password)
			editor.save()
			subject = "Thank you for becoming a new vortaro.co.cc editor"
			body = email_register % (email, password)
			send_mail(subject, body, 'noreply@vortaro.co.cc',[email],
				fail_silently=False)
			request.session["message"] = "An email has been sent to %s" % email
			return HttpResponseRedirect(
				"/about?message=user_created&email=%s" % email)
	return render_to_response("register.html", {"form":form})
	
def logmein(request):
	error = ""
	form = LoginForm()
	if request.POST:
		form = LoginForm(request.POST)
		if form.is_valid():
			user = authenticate(
				email=form.cleaned_data["email"],
				password=form.cleaned_data["password"]
			)
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
	"form":form,
	"error":error})

def logmeout(request):
	logout(request)
	return HttpResponseRedirect("/about")
	
def about(request):
	return render_to_response("about.html", {
	"messages":messages(request),
	"user":request.user,})
	
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
			request.session["message"] = "Profile updated"
			return HttpResponseRedirect("/home")
		else:
			error = "Invalid data"
	form = SettingsForm({
	"first_name":user.first_name,
	"last_name":user.last_name,
	#"language":user.language.id,
	"languages":[x.id for x in user.languages.all()]})
	return render_to_response("editor/settings.html", {
	"user":user,
	"error":error,
	"form":form})

def homeview(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	return render_to_response("editor/home.html", {
	"user":request.user,
	"messages":messages(request)})

def search(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	return render_to_response("editor/search.html", {
	"user":request.user,
	"words":Word.objects.all()
	})
	
def word(request, command=None):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	editor = request.user
	# I am strictly creating a word
	if command == "new":
		# I want to create a word, give me a form
		if not request.POST:
			form = WordForm()
		# I already entered the fields, create it now
		else:
			form = WordForm(request.POST)
			if form.is_valid():
				# Try to find a duplicate in the database
				word = Word.objects.filter(
					language = form.cleaned_data["language"],
					full = form.cleaned_data["full"])
				# It already exists!
				if word:
					request.session["error"] \
						= "The word already exists here: %s" % word[0].button()
				# It doesn't exist, create it
				else:
					word = editor.create_word(form.cleaned_data)
					# Reditect to the newly created word's homepage :)
					request.session["message"] = "Word successfully created"
					return HttpResponseRedirect('/data/word/%d' % word.id)
		return render_to_response("editor/new_word.html", {
		"messages":messages(request),
		"user":request.user,
		"form":form})
	# I am modifying a word
	elif command == "modify" and request.POST:
		form = WordForm(request.POST)
		word = get_object_or_404(Word, id=request.POST["id"])
		if form.is_valid():
			# If changes were made, give a message
			if editor.modify_word(word, form.cleaned_data):
				request.session["message"] \
					= "The word was successfully modified"
			return HttpResponseRedirect('/data/word/%d' % word.id)
	# I want to look at a word
	elif command.isdigit():
		word = get_object_or_404(Word, id=int(command))
		form = WordForm(word.values())
	# I can't understand the command, 404
	else:
		raise Http404
	return render_to_response("editor/word.html", {
	"messages":messages(request),
	"user":request.user,
	"form":form,
	"commits":Commit.objects.filter(object_id=word.id)})
