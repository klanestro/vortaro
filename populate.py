import os
import sys

import random


vowels = ["a", "e", "i", "o", "u"]
consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 
              'r', 's', 't', 'v', 'w', 'x', 'y', 'z']
 
def _vowel():
    return random.choice(vowels)
 
def _consonant():
    return random.choice(consonants)
 
def _cv():
    return _consonant() + _vowel()
 
def _cvc():
    return _cv() + _consonant()
 
def _syllable():
    return random.choice([_vowel, _cv, _cvc])()
 
def word():
    """ This function generates a fake word by creating between two and three
        random syllables and then joining them together.
    """
    syllables = []
    for x in range(random.randint(2,3)):
        syllables.append(_syllable())
    return "".join(syllables)


os.system("cp vort.back vortaro.sqlite3")
# scripts.py file location
scripts = os.path.normpath(os.path.join(os.getcwd(), __file__))
# Vortaro root dir
vortaro = os.path.dirname(scripts)
# Allow to import models
sys.path.append(os.path.split(vortaro)[0])
os.environ["DJANGO_SETTINGS_MODULE"] = "vortaro.settings"

from vortaro.words.models import *

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "syncdb":
	print "boom"
	os.system("rm vortaro.sqlite3")
	os.system("python manage.py syncdb")
	os.system("cp vortaro.sqlite3 vort.back")

languages = []
epo = LanguageKey(code="epo")
epo.save()
eng = LanguageKey(code="eng")
eng.save()
languages.append(epo)
languages.append(eng)

LanguageName(name_of=epo,name_in=eng,text="Esperanto").save()
LanguageName(name_of=eng,name_in=eng,text="English").save()

num_editors = 15
num_actions = 100
editors = []
words = []

for i in range(num_editors):
	first = word()
	last = word()
	email = first + "_" + last + "@example.com"
	username = first + "_" + last
	first = first.capitalize()
	last = last.capitalize()
	editor = Editor(
		last_name = last,
		first_name = first,
		username = username,
		email = email
	)
	editor.set_password("crimson")
	editor.save()
	editors.append(editor)

for i in range(num_actions):
	print i
	act = random.randint(1,2)
	editor = random.choice(editors)
	if act == 1:
		words.append(editor.create_word({"full":word(),"language":random.choice(languages)}))
	if act == 2 and len(words) > 0:
		pass

me = Editor(username="alexeiboroninegmailcom",email="alexei.boronine@gmail.com")
me.set_password("crimson")
me.save()
