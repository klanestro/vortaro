from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import *
from django.db import IntegrityError
from django.forms.models import model_to_dict
from django.template.loader import get_template
from django.template import Context

from vortaro.words.tools import encode, decode

# Just an id
class UID(Model):
    pass

class UIDAbstract(Model):
    
    uid = ForeignKey(UID)
            
    def assign_uid(self):
        uid = UID()
        uid.save()
        self.uid = uid
            
    def save(self):
        # This turns out is the only way to check if self.uid is defined
        try:
                self.uid
        except:
                self.assign_uid()
        super(UIDAbstract, self).save()
            
    def modify(self, newvals, commit):
        """
        Takes a dict of new values and overwrites each. Returns True if at least
        one new value was given, otherwise False.
        """
        changed = False
        for key, val in newvals.items():
                if key == "id": continue
                if not changed and self.__getattribute__(key) != val:
                        changed = True
                self.__setattr__(key, val)
                MicroCommit(
                        commit = commit,
                        mtype = "m",
                        uid = self.uid,
                        key = key,
                        value = str(val)
                ).save()
        return changed
    
    class Meta:
        abstract = True
            

# The following have no significant content, used only for matching
class LanguageKey(Model):
    code = CharField(max_length=6,unique=True)
    def __unicode__(self):
        return self.code

class Editor(User, UIDAbstract):
    
    def __unicode__(self):
        text = self.first_name + " " + self.last_name
        text = text.strip()
        if not text:
                text = u"Anonymous %d" % self.id 
        return text

    def get_absolute_url(self):
        return u"/data/editors/%d" % self.id

    def create_word(self, values, explanation=None):
        w = Word()
        w.assign_uid()
        commit = Commit(
                editor = self,
                commit_type = "cr",
                explanation = explanation
        )
        commit.save()
        MicroCommit(
                commit = commit,
                mtype = "c",
                uid = w.uid
        ).save()
        w.modify(values, commit)
        w.save()
        return w
    
    def modify_word(self, word, values, explanation=None):
        commit = Commit(
                editor = self,
                commit_type = "md",
                explanation = explanation
        )
        commit.save()
        word.modify(values, commit)
        word.save()
        
            
class Commit(UIDAbstract):
    when = DateTimeField(auto_now=True)
    editor = ForeignKey(Editor,related_name="commits")
    explanation = CharField(max_length=300,null=True)
    # Create, Delete, Modify, Merge (?)
    commit_type = CharField(max_length=2)

class MicroCommit(Model):
    commit = ForeignKey(Commit,related_name="microcommits")
    mtype = CharField(max_length=1)
    uid = ForeignKey(UID, related_name="microcommits")
    key = CharField(max_length=25,null=True)
    value = CharField(max_length=400,null=True)

class Word(UIDAbstract):
    def __unicode__(self):
        return self.full
    def get_absolute_url(self):
        return u"/data/words/%d" % self.id
    # Full representation
    full = CharField(max_length=70,db_index=True)
    # The language of the word
    language = ForeignKey(LanguageKey)

class Concept(UIDAbstract):
    pass

# A connection between a concept and a word
class ConceptConnection(UIDAbstract):
    word = ForeignKey(Word,related_name="concept_connections")
    concept = ForeignKey(Word,related_name="word_connections")


