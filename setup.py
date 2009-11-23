import os

def setup():
	dir = os.path.dirname(os.path.normpath(os.path.join(os.getcwd(), __file__)))
	print ""
	print "Vortaro root: " + dir + "/vortaro"
	if not confirm("Do you want vortaro set up in this directory?"):
		return
	os.system("git clone git://github.com/alexeiboronine/vortaro.git vortaro")
	os.chdir("vortaro")
	f = open("local_settings.py", "w")
	f.write('ROOT_FOLDER = "' + dir + '/vortaro/"')
	f.write("\n")
	f.close()
	if confirm("Do you want to run the Django server?"):
		os.system("python manage.py runserver")
	else:
		print 'Done. Run "python manage.py runserver" to test'

def confirm(prompt=None, resp=True):
	if prompt is None:
		prompt = 'Confirm'

	if resp:
		prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
	else:
		prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
	while True:
		ans = raw_input(prompt)
		if not ans:
			return resp
		if ans not in ['y', 'Y', 'n', 'N']:
			print 'please enter y or n.'
			continue
		if ans == 'y' or ans == 'Y':
			return True
		if ans == 'n' or ans == 'N':
			return False

if __name__ == "__main__":
	setup()
