#! /usr/bin/env python


# TODO: rewrite to use /usr/lib/python1.5/cmd.py
# this will enable tabcompletion (but add system ones) and command history
""" tagsh

A simple shell for testing out tagfs
"""
from __future__ import print_function

import tagfs
import sys
import string
import os
import readline

versionstring = "TagSh v0.1 (Beta) - (c) Craig Nicol 2005"

def help():
  print ("\nKnown commands:\n---------------\n")
  print ("ls [-l|--long] [-t|--tags] [--fids] tagsorfilenames")
  print ("\tlist files matching tag list")
  print ("cd tags")
  print ("\tchange domain to tags")
  print ("pwd")
  print ("\tshow present working domain")
  print ("cp file tag")
  print ("\tadd tag to file")
  print ("rm file tag")
  print ("\tremove tag from file")
  print ("alias [::searchtag [searchstring]]")
  print ("\tview|remove|add searchtags")
  print ("^D|quit|exit|logout")
  print ("\ntag1/tag2 matches tag1 AND tag2")
  print ("tag1 tag2 matches tag1 OR tag2")
  print ("all tag combinations support brackets")
  print ("type help specialtags for details on :tags")

def helpspecialtags():
  print ("\nCurrently known special tags:\n")
  print (":today\t\tAll files modified today")
  print (":yesterday")
  print (":thisweek")
  print (":lastN[seconds|minutes|hours|days|weeks|months|years]")
  print ("\nFor the next three, measure time in seconds since UNIX epoch")
  print (":atleastN[bytes|kilobytes|megabytes|gigabytes|tags|seconds]")
  print (":atmostN[bytes|kilobytes|megabytes|gigabytes|tags|seconds]")
  print (":exactlyN[bytes|kilobytes|megabytes|gigabytes|tags|seconds]")
  
def run(cmdstring, tfs):
  """ run(cmdstring, tfs) -> None
  
  Runs cmdstring in the context of tfs
  """
  cmd = string.split(cmdstring, ' ', 1)
  if len(cmd) == 1: # no args
    cmd.append("")
    
  if cmd[0] == "ls":
    # Improve formatting
    files = tfs.ls(cmd[1])
    for f in files:
      print (f + '\t',)
    print ("\nTotal files", len(files))
  elif cmd[0] == "cd":
    tfs.cd(cmd[1])
  elif cmd[0] == "pwd":
    print (tfs.pwd())
  elif cmd[0] == "cp": # TODO: This might need smart split
    a = string.split(cmd[1])
    try:
      tfs.cp(a[0], a[1])
    except "File Not Found":
      print (str(a[0]) + ": File does not exist")
  elif cmd[0] == "rm": # TODO: This might need smart split
    a = string.split(cmd[1])
    try:
      tfs.rm(a[0], a[1])
    except "File Not Found":
      print (str(a[0]) + ": File does not exist")
  elif cmd[0] == "alias":
    if string.strip(cmd[1]) == "":
      print (tfs.showsearches())
      return
    a = string.split(cmd[1], ' ', 1)
    if a[0][:2] != "::":
      print ("Search alias MUST start with ::")
      return
    if len(a) > 1:
      tfs.savesearch(a[0][2:], a[1])
    else:
      tfs.delsearch(a[0][2:])
  elif cmd[0] == "help":
    if len(cmd[1]) > 0 and cmd[1][0] == "s":
      helpspecialtags()
    else:
      help()
  else: # hand over to caller - need to restice files properly & fork
    files = os.popen(cmdstring)
    print (files.read())
    files.close()
    
def runsh(args = None):
  config = "thisdir.tagshrc"
  promptfmt = "[user %PWD%]$ "
  
  readline.set_completer(tagfs.tagfs().tabcompletion)
  readline.parse_and_bind("tab: complete")
  
  print (versionstring)
  print ("Loading searchDB...")
  
  t = tagfs.tagfs()
  try:
    t.loadDB(config) # Try to load searches file
  except IOError:
    "Cannot load searches from config file."
  
  print ("Loading file info...")
  t.refresh() # Load file info

  cmd = "\n"
  while cmd != "" and cmd[:4] != "quit" and cmd[:6] != "logout" and cmd[:4] != "exit":
    run(string.strip(cmd), t)
    print (string.replace(promptfmt, "%PWD%", t.pwd()),)
    # cmd = sys.stdin.readline()
    cmd = readline.get_line_buffer()
  
  try:
    t.saveDB(config)
  except IOError:
    print ("Cannot save searches to config file")
    
if __name__ == "__main__":
  runsh(sys.argv)
