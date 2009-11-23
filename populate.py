import os
import sys

# scripts.py file location
scripts = os.path.normpath(os.path.join(os.getcwd(), __file__))
# Vortaro root dir
vortaro = os.path.dirname(scripts)
# Allow to import models
sys.path.append(os.path.split(vortaro)[0])
os.environ["DJANGO_SETTINGS_MODULE"] = "vortaro.settings"

from vortaro.words.models import *

epo = LanguageKey(code="epo")
epo.save()

eng = LanguageKey(code="eng")
eng.save()

LanguageName(name_of=epo,name_in=eng,text="Esperanto").save()
LanguageName(name_of=eng,name_in=eng,text="English").save()

me = Editor(username="alexeiboroninegmailcom",email="alexei.boronine@gmail.com")
me.set_password("crimson")
me.save()
