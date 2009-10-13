import settings
from vortaro.words.models import *
import sqlite3
conn = sqlite3.connect('words.sqlite')
c = conn.cursor()

c.execute('select * from words')
eo = LanguageKey.objects.get(code='eo')
en = LanguageKey.objects.get(code='en')
verb = CategoryKey.objects.get(code='verb')
noun = CategoryKey.objects.get(code='noun')
for row in c:
	e = row[1].strip()
	if e.find(' ') != -1:
		continue
	con = Concept()
	con.save()
	print "created concept"
	
	if e.endswith('i'):
		c = verb
	elif e.endswith('o'):
		c = noun
	else:
		c = None
	try:
		esp = Word.objects.get(text=e,language=eo)
		print "exists: " + e
	except:
		esp = Word(text=e,language=eo,isword=True,category=c)
		esp.save()
		print "eo: " + e
	con.words.add(esp)
	words = []
	for o in row[0].split("|"):
		o = o.strip()
		w = o.find(' ') == -1
		try:
			word = Word.objects.get(text=o,language=en)
			print "exists: " + o
		except:
			word = Word(text=o,language=en,isword=w)
			word.save()
			print "en: " + o
		con.words.add(word)
