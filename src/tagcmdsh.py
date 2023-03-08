#! /usr/bin/env python

""" Tagcmdsh.py -- TagSH based on cmd.py
"""

from cmd import *
import tagfs
import string
import readline
import os
import utils

versionstring = "TagSh v0.6 (Beta) - (c) Craig Nicol 2005"

tag_info = """
\ntag1/tag2 matches tag1 AND tag2
tag1 tag2 matches tag1 OR tag2
all tag combinations except special tags support 
brackets and wildcards ( * OR ? )

Special Tags:
    :today\t\tAll files modified today
    :yesterday
    :thisweek\t\tAll files modified since 00:00 on Monday
    :lastN[seconds|minutes|hours|days|weeks|months|years]
    
    For the next three, measure time in seconds since UNIX epoch
    :atleastN[bytes|kilobytes|megabytes|gigabytes|tags|seconds]
    :atmostN[bytes|kilobytes|megabytes|gigabytes|tags|seconds]
    :exactlyN[bytes|kilobytes|megabytes|gigabytes|tags|seconds]
    
    :name=nameexp\t\tWildcards allowed in nameexp
"""


class tagcmdsh(Cmd):
  # TODO: allow defining refresh dir, and possible recursive search
  # TODO: Allow prompt changes - and save them
  def __init__(self, configfile="thisdir.tagshrc", prmpt = "[user %PWD%]$ "):
	self.promptfmt = prmpt
	self.config = configfile
	self.tagfs = tagfs.tagfs()
	
	self.user = "user"
	self.prompt = string.replace(
	                    string.replace(self.promptfmt, "%USR%", self.user),
			    "%PWD%", self.tagfs.pwd())

	# DONE: Need to make tab-completion work
	# Easiest solution - upgrade python - it's in the latest cmd
	# DONE: Need to add commands from system path - os.environ["PATH"]
	# DONE: Also add default fn to call commands from system path
	# TODO: Need to filter executables using:
	#    os.stat(filename)[stat.ST_MODE] & stat.S_IEXEC
	#    which is true iff filename is executable
	pathlist = string.split(os.environ["PATH"],os.pathsep)
	binlist = []
	for p in pathlist:
	  if len(p) > 1:
		try:
		  binlist.extend(os.listdir(p))
		except OSError:
		  print "Ignoring missing path:",p
	self.tagfs.tabcompletionextend([], binlist)
	
	readline.set_completer(self.completer) #(self.tagfs.tabcompletion)
	readline.parse_and_bind("tab: complete")
	# Find the right combo for F5 key
	# readline.parse_and_bind('F5: "refresh\n"')

	print "Loading searchDB..."
	
	try:
	  self.tagfs.loadDB(self.config) # Try to load searches file
	except IOError:
	  "Cannot load searches from config file."

	print "Loading file info..."
	self.tagfs.refresh() # Load file info

  def emptyline(self): # turn off automatic last line completion
    pass

  # Borrowed from cmd.py from python2.3
  def get_names(self):
	# Inheritance says we have to look in class and
	# base classes; order is not important.
	names = []
	classes = [self.__class__]
	while classes:
	  aclass = classes[0]
	  if aclass.__bases__:
		classes = classes + list(aclass.__bases__)
	  names = names + dir(aclass)
	  del classes[0]
	return names

  def completenames(self, text):
	dotext = 'do_'+text
	names = []
	for a in self.get_names():
	  if string.find(a, dotext)==0: # starts with
		names.append(a[3:])
	return names
     
  def do_h(self, args):
	""" h : short list of known shell commands """
	print self.completenames(args)
	
  def completer(self, text, state):
	if state == 0:
	  self.matches = self.tagfs.expandwildcards(text + "*") + self.completenames(text)
	try:
	  return self.matches[state]
	except IndexError:
	  return None

  def help_help(self):
	print "Display help on known commands."

  def help_tags(self):
	print tag_info

  def do_refresh(self, args):
    """ refresh : Refresh the current file info """
    print "Loading file info..."
	self.tagfs.refresh() # Load file info
	
  def do_ls(self, args):
	""" ls [options] [tagsorfilenames] : List files in current domain

	* and ? wildcards allowed in tagsorfilenames, which defaults to *
	
	Options:
	    -l --long       Print full info for each file
	    -t --tags       Print tag list for each file
	       --fids       Print list of file ids instead of file names
	"""
	# TODO: Improve formatting
	if utils.string_find_next_of(args, "*?") > -1:
	  wc = self.tagfs.testwildcards(args)
	  print wc[:1] + ":name...", wc[1:], ":"
	files = self.tagfs.ls(args)
	for f in files:
	  print f + '\t',
	print "\nTotal files", len(files)
    
  def do_cd(self, args):
	""" cd [tags] : Change domain 
	
	cd ..      Change to global domain
	"""
	self.tagfs.cd(args)
	self.prompt = string.replace(self.promptfmt, "%PWD%", self.tagfs.pwd())

  def do_pwd(self, args):
	""" pwd : show present working domain """
	print self.tagfs.pwd()
	
  def do_cp(self, args):
	""" cp file tags : apply tags to file """
	a = string.split(args, " ", 1) # TODO: This might need smart split if command has quotes
	try:
	  self.tagfs.cp(a[0], a[1])
	except tagfs.FileNotFound:
	  print str(a[0]) + ": File does not exist"

  def do_rm(self, args):
	""" rm file tags : remove tags from file """
	a = string.split(args, " ", 1) # TODO: This might need smart split if command has quotes
	try:
	  self.tagfs.rm(a[0], a[1])
	except tagfs.FileNotFound:
	  print str(a[0]) + ": File does not exist"
	
  def do_alias(self, args):
	""" alias [::searchname [tags]] : saved search management 
	
	With no arguments, return currently defined searches
	With one argument, delete the named search
	With many arguments, assign the tags to the named search
	"""
	if string.strip(args) == "":
	  print self.tagfs.showsearches()
	  return
	a = string.split(args, ' ', 1)
	if a[0][:2] != "::":
	  print "Search alias MUST start with ::"
	  return
	if len(a) > 1:
	  self.tagfs.savesearch(a[0][2:], a[1])
	else:
	  self.tagfs.delsearch(a[0][2:])
	
  def default(self, line):
	# DONE: allow forking
	# TODO: Check command before running...
	# TODO: Map tags in 'line' to actual file? - requires capturing FS interupts.
      pid = -1
      sline = string.strip(line)
      if sline[-1] == "&":
        sline = sline[:-1]
        pid = os.fork()
        if pid != 0:
          print "New process <" + str(pid) + "> " + sline
          # Note, python takes this pid, child programs
          # take extra pids. Be aware.
          return
	files = os.popen(sline)
	print files.read()
	files.close()
      if pid == 0:
        print "Process ended <" + str(os.getpid()) + "> " + sline
        os._exit(0) # exit cleanly

#  def do_kill(self, args):
#    print args, int(args)
#    if int(args) != 0:
#      os.kill(int(args), 15)
        
  def do_EOF(self, args):
	""" Save the config file and exit. """
	print "\nSaving searchDB..."
	try:
	  self.tagfs.saveDB(self.config)
	except IOError:
	  print "Cannot save searches to config file"
	return -1

  def do_prompt(self, args):
	""" prompt [newprompt] : Change prompt format, blank to reset """
	if args == None or string.strip(args) == "":
	  self.promptfmt = "[%%USR%% %%PWD%%]"
	else:
	  self.promptfmt = str(args)

  def do_cat(self, args):
	""" cat [] """
	filenames = self.tagfs.ls(args)
	fileids = self.tagfs.open(args)
	for name,fid in map(lambda a,b:(a,b), filenames, fileids):
	  print "--- START", name, "---"
	  for l in fid.readlines():
		print l[:-1]
	  print "--- END", name, "---"
	
    
  do_quit = do_EOF
  do_exit = do_EOF
  do_logout = do_EOF
    
if __name__ == "__main__":
  t = tagcmdsh()
  t.cmdloop(versionstring)
