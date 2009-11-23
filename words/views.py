import urllib

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.http import Http404

from vortaro.words.models import *
from vortaro.words.emails import *
from vortaro.words.forms import *

def button(obj):
	"""
	Creates an embeddable link button for an object such as Word or Sentence.
	Takes the object as an argument.
	"""
	c = "button"
	if obj.deleted:
		c = "button deleted"
	if isinstance(obj, Word): name = ("word","W")
	else: return ""
	return """
	<span class="%s"><a href="/data/%s/%d">%s%d</a></span>
	""" % (c, name[0], obj.id, name[1], obj.id)

def messages(request):
	"""
	The GET variable message represents a message about the user's previous
	action to be shown on the redirected page. This function takes request
	as an argument and return the full message. If there is nothing, it
	returns an empty string.
	"""
	text = ""
	if "message" in request.GET:
		message = request.GET["message"]
		# If you are redirected here from successfully updating your profile
		if message == "updated":
			text = "Profile updated"
		elif message == "user_created":
			text = "An email has been sent to %s" % request.GET["email"]
	return text

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
	"message":messages(request),
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
			return HttpResponseRedirect("/home?message=updated")
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
	"message":messages(request)})

def search(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	return render_to_response("editor/search.html", {
	"user":request.user
	})
	
def word(request, id=None):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	form = WordForm()
	error = ""
	message = ""
	# You are requesting to see a word
	if id != None:
		word = Word.objects.filter(id=id)
		if word:
			form = WordForm({
				"language":word[0].language.id,
				"full":word[0].full,
				"id":word[0].id
			})
		else:
			raise Http404
	# You are creating or updating a word
	elif request.POST:
		form = WordForm(request.POST)
		if form.is_valid():
			# You are modifying a word
			if request.POST["id"] != "":
				word = Word.objects.filter(id=request.POST["id"])
				if word:
					word[0].language = form.cleaned_data["language"]
					word[0].full = form.cleaned_data["full"]
					word[0].save()
					message = "The word was successfully modified"
				else:
					# The word was physically deleted as you were editing it
					error = "The word was physically deleted as you were editing it"
			# You are creating a word
			else:
				# Try to find the word in the database
				word = Word.objects.filter(
					language = form.cleaned_data["language"],
					full = form.cleaned_data["full"])
				# It already exists!
				if word:
					error = "The word already exists here: %s" % button(word[0])
				# It doesn't exist, create it
				else:
					word = Word(
						language = form.cleaned_data["language"],
						full = form.cleaned_data["full"])
					word.save()
					message = "The word has been successfully created"
					# Now the form has an id
					form = WordForm(dict(request.POST.items() + [("id",word.id)]))
	return render_to_response("editor/word.html", {
	"error":error,
	"message":message,
	"user":request.user,
	"form":form})
