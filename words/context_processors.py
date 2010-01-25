from vortaro.words.forms import *

def login(request):
        return {"login_form":LoginForm()}
