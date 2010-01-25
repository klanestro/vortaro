import os
import sys
import random
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from vortaro.words.models import *
from vortaro.settings import DATABASE_NAME

vowels = "aeiou"
consonants = 'bcdfghjklmnpqrstvwz'


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
 
def word(cap=False):
    """ This function generates a fake word by creating between two and three
        random syllables and then joining them together.
    """
    syllables = []
    for x in range(random.randint(2,3)):
        syllables.append(_syllable())
    word = "".join(syllables)
    if cap: word = word[0].upper() + word[1:]
    return word
   
def sentence():
    ret = word(True)
    for i in range(random.randint(5,15)):
        ret += " " + word()
        if random.randint(0,5) == 0:
             ret += ","
    return ret + ". "

def mutate(word):
    p = random.randint(0,len(word)-1)
    return word[:p] + _vowel() + word[p+1:]

class Command(BaseCommand):
    help = """"""
    def handle(self, *args, **options):
        os.system("rm %s" % DATABASE_NAME)
        os.system("python manage.py syncdb --noinput")
        
        languages = []
        editors = []
        
        epo = LanguageKey(code="epo")
        eng = LanguageKey(code="eng")
        epo.save()
        eng.save()
        
        languages.append(epo)
        languages.append(eng)
        
        me = Editor(
            first_name = "Alexei",
            last_name = "Boronine",
            email = "alexei.boronine@gmail.com"
        )
        me.set_password("crimson")
        me.save()
        editors.append(me)
        
        # Make 10 editors
        for i in range(9):
            first = word(True)
            last = word(True)
            editor = Editor(
                first_name = first,
                last_name = last,
                email = "%s.%s@gmail.com" % (first, last),
                username = "%s_%s" % (first, last)
            )
            editor.set_password("crimson")
            editor.save()
            editors.append(editor)
            print editor
        
        # Make about 100 random actions
        for i in range(99):
            editor = random.choice(editors)
            action = random.randint(1,5)
            
            # Create word
            if 0 <= action < 3:
                w = Word(
                    editor,
                    {"full":word(),
                    "language":random.choice(languages)},
                    explanation = sentence()
                )
                print "New word:", w
            
            # Modify word
            if 3 <= action < 5:
                if not Word.objects.count():
                    continue
                w = Word.objects.order_by('?')[0]
                editor.modify_word(
                    w,
                    {"full":mutate(w.full)},
                    explanation = sentence()
                )
                print "Modified word"
            
            # Delete word 
            if 5 <= action < 6:
                if not Word.objects.count():
                    continue
                w = Word.objects.order_by('?')[0]
                editor.delete_word(
                    w,
                    explanation = sentence()
                )
                print "Deleted word"








