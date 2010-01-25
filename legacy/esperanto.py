# -*- coding: utf-8 -*-

import sys
from vortaro.settings import PROJECT_ROOT 
from django.http import HttpResponse

roots = set(open(PROJECT_ROOT+'/legacy/roots.txt','r').read().decode('utf-8').strip().split("\n"))
prefixes=[u"ali",u"bo",u"dis",u"ek",u"eks",u"fi",u"ge",u"i",u"ki",u"mal",u"neni",u"pra",u"re",u"ti",u"ĉef",u"ĉi",u"ne"]
suffixes=set([u"aĵ",u"ar",u"ant",u"ad",u"at",u"aĉ",u"ant",u"an",u"ar",u"ec",u"eg",u"estr",u"et",u"ej",u"ebl",u"em",u"er",u"ent",u"el",u"end",u"ig",u"iĝ",u"ing",u"int",u"ist",u"in",u"iĉ",u"ind",u"il",u"id",u"ism",u"it",u"int",u"obl",u"op",u"ot",u"on",u"ont",u"uj",u"ul",u"um",u"ut",u"unt",u"ĉj"])

verbose = False
morphemes = {"root":[],"suf":[],"pre":[]}
defs = []
dead_ends = []

def ajax(request, word):
    cback = request.GET["callback"]
    jsonp = cback+'({"text":"'+doword(word.encode('utf-8')).strip()+'"})'
    return HttpResponse(content=jsonp, mimetype='application/javascript')


class Node:
    def __init__(self, type, body, rest, parent=False):
        self.parent = parent
        self.type = type
        self.body = body
        
        # Children
        self.pre = False
        self.suf = False
        self.roots = []
        
        self.rest = rest
        self.end = False
        if verbose: print "add:    " + self.trace()
        if rest != "":
            self.search()
    
    def gather(self):
        global morphemes
        
        root = False
        
        if self.pre and self.pre.body not in morphemes["pre"]:
            morphemes["pre"].append(self.pre.body)
            findword("pre", self.pre.body)
            self.pre.gather()
        
        if self.suf and self.suf.body not in morphemes["suf"]:
            morphemes["suf"].append(self.suf.body)
            findword("suf", self.suf.body)
            self.suf.gather()
        
        # If there are many roots, find the longest
        root = False
        for r in self.roots:
            if not root or len(r.body) > len(root.body):
                root = r
    
        if root:
            if root.body in morphemes['suf'] + morphemes['pre']:
                return

            # Try to get root+suf
            if root.suf:
                if findword("root",root.body+root.suf.body,("o","a","e","i")):
                    root.suf.gather()
                    return

            # Try root with the given ending
            if root.end:
                if findword("root",root.body,root.end):
                    root.gather()
                    return
        
            # If the following suffix is -ebl, force verb
            if root.suf and root.suf.body in ["ebl"]:
                if findword("root",root.body,"i"):
                    root.gather()
                    return
        
            findword("root",root.body,("o","a","e","i"))
            root.gather()
                            
    def search(self):
        #if verbose: print "search: " + self.trace()
        ps = starts_with(self.rest, prefixes)
        rs = starts_with(self.rest, roots)
        ss = starts_with(self.rest, suffixes)
        if self.type in ["pre","suf"]:
            for m in ps:
                self.addchild("pre",m)
        if self.type in ["pre","root","suf"]:
            for m in rs:
                self.addchild("root",m)
        if self.type in ["root","suf"]:
            for m in ss:
                self.addchild("suf",m)                  
            for m in ["o","a","e","i"]:
                if self.rest.startswith(m):
                    if verbose: print " | ending: " + m
                    self.end = self.rest[0]
                    self.rest = self.rest[1:]
                    self.search()
                    return
        # Remove a dead branch
        if self.rest != "" and self.nochildren():
            dead_ends.append(self)
            if verbose: print " | reached a dead end"
        elif verbose:
            print " | reached the end"
    def addchild(self, type, body):
        child = Node(type,body,self.rest[len(body):],self)
        if type == "pre":
            self.pre = child
        elif type == "suf":
            self.suf = child
        else:
            self.roots.append(child)

    def nochildren(self):
        return not self.pre and not self.suf and not self.roots

    def dead_end(self):
        # Is there no parent, or maybe a living child?
        if not self.nochildren() or not self.parent:
            return
        # Nope, all dead (or none existent), die
        if verbose: print " | kill: " + self.type + " " + self.body
        if self.type == "pre":
            self.parent.pre = False
        elif self.type == "suf":
            self.parent.pre = False                 
        else: # Kill roots.
            self.parent.roots = filter(lambda x: x.body != self.body,self.parent.roots)
        # Perhaps the parent is hopeless too?
        self.parent.dead_end()
    def trace(self):
        if self.body == "":
            return ""
        else:
            return self.parent.trace() + ("/%s(%s)" % (self.type, self.body))

def findword(type, body, endlist=None):
    global defs
    if type == "pre":
        result = look(body+"-")
    elif type == "suf":
        result = look("-"+body)
    else: # root
        for end in endlist:
            result = look(body+end)
            if result != None:
                break
    if result != None:
        defs.append(result)
        return True
    else:
        return False

def look(w):
    import sqlite3
    conn = sqlite3.connect(PROJECT_ROOT+'/legacy/words.sqlite')
    cursor = conn.cursor()
    cursor.execute("select * from words where eo like ?", (w,))
    result = cursor.fetchone()
    conn.close()
    if result != None:
        return [w, result[0]]
    else:
        return None

def starts_with(word, keys):
    """
    Returns only the keys that the word starts with
    """
    return filter(lambda x: word.startswith(x), keys)

def doword(word):
    global defs
    word = word.decode('utf-8')     
    defs = []
    # Poetic omission of the ending
    if word.endswith("'"):
        word = word[:-1]+"o"

    word = word.lower()     
    if word.endswith('n'):
        word = word[:-1]
    if word.endswith('j'):
        word = word[:-1]
    for end in ['as','is','os','us','u']:
        if word.endswith(end):
            word = word[:-len(end)]+"i"

    findword("root",word[:-1],(word[-1],"o","a","e","i"))
    
    if not defs:
        w = Node("pre","",word)
        for d in dead_ends:
            d.dead_end()
        w.gather()

    text = ""
    if defs:
        for d in defs:
            definition = (", ".join(d[1].split("|"))).strip()
            text += "<b>%s</b>: %s<br/>" % (d[0], definition)
        text = text[:-5]
    else:
        text = "Sorry, not found."

    return text


if __name__ == "__main__":
    verbose = True
    print doword(sys.argv[1])
