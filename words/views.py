import urllib

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.http import Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

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
                        request.usermessage_set.create(
                                message="An email has been sent to %s" % email)
                        return HttpResponseRedirect("/about")
        return render_to_response("register.html",
        {"form":form},context_instance=RequestContext(request))
        
def logmein(request):
        error = ""
        form = LoginForm()
        if request.POST:
                form = LoginForm(request.POST)
                if form.login(request):
                        next = request.user.get_absolute_url()
                        return HttpResponseRedirect(next)
        return render_to_response("login.html", {
        "login_form":form,
        "error":error})

def about(request):
        return render_to_response("about.html", {
        "messages":messages(request)},
        context_instance=RequestContext(request))

@login_required
def settings(request):
        editor = request.user
        error = ""
        if request.POST:
                form = SettingsForm(request.POST)
                if form.is_valid():
                        editor.first_name = form.cleaned_data["first_name"]
                        editor.last_name = form.cleaned_data["last_name"]
                        editor.languages = form.cleaned_data["languages"]
                        if form.cleaned_data["password"]:
                                editor.set_password(form.cleaned_data["password"])
                        editor.save()
                        editor.message_set.create(message="Profile updated")
                        return HttpResponseRedirect(editor.get_absolute_url())
                else:
                        error = "Invalid data"
        form = SettingsForm({
        "first_name":editor.first_name,
        "last_name":editor.last_name,
        #"language":user.language.id,
        "languages":[x.id for x in editor.languages.all()]})
        
        return render_to_response("settings.html", {
        "error":error,
        "form":form},context_instance=RequestContext(request))

def editor_profile(request, id):
        editor = get_object_or_404(Editor, id=id)               
        return render_to_response("editor_profile.html",
                {"editor":editor},
                context_instance=RequestContext(request))

def search(request):
        if not request.user.is_authenticated():
                return HttpResponseRedirect('/login/?next=%s' % request.path)
        return render_to_response("search.html", {
        "words":Word.objects.all()
        },context_instance=RequestContext(request))

@login_required
def word_actions(request, command=None):
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
                                        editor.message_set.create(message="Word successfully created")
                                        return HttpResponseRedirect(word.get_absolute_url())
                return render_to_response("new_word.html", {
                "form":form},context_instance=RequestContext(request))
        # I am modifying a word
        elif command == "modify" and request.POST:
                form = WordForm(request.POST)
                word = get_object_or_404(Word, id=request.POST["id"])
                if form.is_valid():
                        # If changes were made, give a message
                        if editor.modify_word(word, form.cleaned_data):
                                editor.message_set.create(
                                        message="The word was successfully modified"
                                )
                        return HttpResponseRedirect(word.get_absolute_url())
        # I don't know this command
        else:
                raise404

def word_profile(request,id):
        word = get_object_or_404(Word, id=id)
        form = WordForm(word.values())
        #print type(pickle.dumps(word))
        #print type(word.uid.commits.all()[0].backup_new)
        return render_to_response("word.html", {
        "form":form,
        "commits":word.uid.commits},
        context_instance=RequestContext(request))
