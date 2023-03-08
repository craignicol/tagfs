""" tagfs.py - demo for tagged filesystem

See tagfs.txt for more details.
This is probably quite inefficient for now.

Since this uses ls to retrieve file info, it is Unix only
"""
import utils
import string
import pickle
import os
import time
import getopt
import re # for wildcard matching

# Programs can redefine these 
andsep = "/"
orsep = ":"

# Data format:
#      { fid : (permissions, links, user, group, size, 
#               moddate, otherdates*, filename, [tags...]),
#        fid : (...) }
testdata = { 1 : (0777, 1, "user","group", 16, 946684800, # 01/01/2000 00:00
                  "file.txt", ["text","test","docs"]),
             2 : (0755, 1, "user", "share", 2306867, 1117926000, # 20/06/2003 00:00
              "music.mp3", ["music","test","bandname"]),
             3 : (0740, 1, "user", "httpd", 1500, 1123607702, # 20/09/2005 18:15:02
              "web.html", ["test","blog","bandname"]), 
         4 : (0777, 2, "user", "group", 2000, 1119223000,
              "newfile", ["new", "test"])
         }

tagperms = { "text" : (0777, []), "test" : (0700, []), 
             "bandname" : (0755, []), "blog" : (0640, []) }
         
def setappend(list, value):
  if utils.listfind(list, value) == -1:
    list.append(value)

def setremove(list, value):
  if utils.listfind(list, value) > -1:
    list.remove(value)

def setunion(list1, list2):
  if list2 == []:
    return list1
  if list1 == []:
    return list2
  outlist = list1[:]
  for item in list2:
    setappend(outlist, item)
  return outlist
    
def setintersection(list1, list2):
  if list1 == []:
    return []
  if list2 == []:
    return []
  outlist = []
  for item in list2:
    if utils.listfind(list1, item) > -1:
      outlist.append(item)
  return outlist

def setdifference(list1, list2):
  """ setdifference(list1, list2) -> list3
  
  list3 = list1 - list2
  i.e. list3 contains all the elements of list1 that are not in list2
  """
  if list1 == []:
    return []
  
  outlist = list1[:]
  for item in list2:
    setremove(outlist, item)
  return outlist

def addhashdata(dict, key, data):
  if dict.has_key(key):
    setappend(dict[key],data)
  else:
    dict[key] = [data]

def smallestatleast(list, val):
  """ smallestatleast(list, val) -> val
  
  Returns the smallest value in list that is at least as big as val,
  or max(list)+1 if val is bigger than all of them
  """
  v = max(list)+1
  for i in list:
    if i < v and i > val:
      v = i
  return v
    
def ask(string):
  print string
  return 0

class FileNotFound:
  def __str__(self):
    return "File Not Found"
    
class tagfs:
  __files = {}
  __tags = {}
  __searches = {}
  __filenames = {}
  __fileformat = "pickle"
  __context = "()"
  
  def __str__(self):
    return "tagfs: <files : " + str(len(self.__files)) + \
       ", tags : " + str(len(self.__tags)) + \
       ", searches : " + str(len(self.__searches)) + \
       ", DBformat : " + self.__fileformat + ">"
  
  # Data format:
  #      { fid : (permissions, links, user, group, size, 
  #               moddate, otherdates..., filename, [tags...]),
  #        fid : (...) }
  __fileperm = 0
  __filelinks = 1
  __fileowner = 2
  __filegroup = 3
  __filesize = 4
  __filemdate = 5
  __filecdate = 6
  __filename = -2
  __filetags = -1

  __alltimes = [__filemdate]
  
  def __tagsfromfiles(self, files):
    self.__tags = {} 
    for f in files.keys():
      addhashdata(self.__filenames, files[f][self.__filename], f)
      for t in self.__files[f][self.__filetags]:
        if self.__tags.has_key(t):
          self.__tags[t].append(f)
        else:
          self.__tags[t] = [f]
  
  def __file2fid(self, file):
    """ private self.file2uid(file) -> fid
    
    Finds the unique file id for the given file and tags
    """
    return file
  
  def __fid2file(self, fid):
    """ private self.uid2file(uid) -> file
    
    Returns the filename of the file with the given unique file id
    """
    return fid

  def __loadPickleDB(self, filename):
    f = open(filename)
    self.__files = pickle.load(f)
    self.__filenames = pickle.load(f)
    self.__searches = pickle.load(f)
    self.__tagsfromfiles(self.__files)
    f.close()
    
  def __savePickleDB(self, filename):
    f = open(filename, "w")
    pickle.dump(self.__files, f)
    pickle.dump(self.__filenames, f)
    pickle.dump(self.__searches, f)
    f.close()
  
  def __loadXMLDB(self, filename):
    utils.loadraw(filename)
    # Do XML processing here
    
  # This needs to reflect tagfs.txt, but it's only for testing
  def __saveXMLDB(self, filename):
    outstr = "<tagfs>"
    for file in self.__files.keys():
      outstr = outstr + "<file><name>" + self.__fid2file(file) \
                      + "</name><owners>"
      for own in self.__files[file][0]:
        outstr = outstr + "<owner>" + own + "</owner>"
      outstr = outstr + "</owners><tags>"
      for tag in self.__files[file][1]:
        outstr = outstr + "<tag>" + tag + "</tag>"
      outstr = outstr + "</tags></file>"
    for s in self.__searches.keys():
      outstr = outstr + "<search>"
      outstr = outstr + "<name>" + s + "</name>"
      outstr = outstr + "<tag>" + self.__searches[s] + "</tag>"
      outstr = outstr + "</search>"
    outstr = outstr + "</tagfs>"
    utils.saveraw(filename, outstr)

  def saveDB(self, filename):
    if self.__fileformat == "pickle":
      self.__savePickleDB(filename)
    else:
      self.__saveXMLDB(filename)
      
  def loadDB(self, filename):
    # Need to try some smart handling here
    if self.__fileformat == "pickle":
      self.__loadPickleDB(filename)
    else:
      self.__loadXMLDB(filename)

  def exportXML(self, filename):
    self.__saveXMLDB(filename)
        
  def __init__(self, files = None, internalDB=0):
    """ self.__init__(files = None, internalDB = false)
    
    If internalDB is false, files is the filename for
    the tagfs files database. If internalDB is true,
    files is a dict of files and tags.
    """
    if type(files) == type({}):
      self.__files = files
    else:
      self.__files = {}
    self.__tagsfromfiles(self.__files)

  def getsearch(self, search):
    if self.__searches.has_key(search):
      return self.__searches[search]
    else:
      return None

  # Data format:
  #      { fid : (permissions, links, user, group, size, 
  #               moddate, otherdates..., filename, [tags...]),
  #        fid : (...) }

  # Needs i18n
  __month = { "Jan" : 1, "Feb" : 2, "Mar" : 3, "Apr" : 4, "May" : 5,
              "Jun" : 6, "Jul" : 7, "Aug" : 8, "Sep" : 9, "Oct" : 10,
        "Nov" : 11, "Dec" : 12 }
        
  # As returned by time module
  __day = { "Mon" : 0, "Tue" : 1, "Wed" : 2, "Thu" : 3, "Fri" : 4,
            "Sat" : 5, "Sun" : 6}
  
  def __filetypetags(self, filename):
    tags = []
    if filename[0] == "#":
      tags.append("temp")
      filename = '"' + filename + '"'
    if os.path.islink(filename):
      tags.append("symlink")
      filename = os.readlink(filename)
        
    commandstring = "file -b " + filename
#    print commandstring,
    files = os.popen(commandstring)
    filetags = files.read()
#    print filetags
    files.close()
    
    if filetags[:3] == "a /": # something script
      filetags = filetags[string.find(filetags, " ", 3):]
    if string.find(filetags, ",") > -1:
      filetags = filetags[:string.find(filetags, ",")]
    if filename[-1] == "~":
      tags.append("temp")
    return tags + string.split(filetags)
    
  def __permstooctal(self, permstring):
    octval = 00
    v = 2**len(permstring)
    for p in permstring:
      if p != "-":
        octval = octval + v
      v = v / 2
    return octval

  def __getfileinfo(self, addtypetags = 1, rootdir=".", recurse = 0):
    """ self.__getfileinfo() -< list of files from os.listdir and os.lstat
    
    Format is (mode,ino,dev,nlink,uid,gid,size,atime,mtime,ctime)

    Data format:
        { fid : (permissions, links, user, group, size, 
                 moddate, otherdates..., filename, [tags...]),
          fid : (...) }
    """
    from stat import *
    os.chdir(rootdir)
    pathtags = string.split(os.getcwd(), os.sep)[1:] # ignore leading sep
    typetags = []
    
    filelist = []
    files = os.listdir(".")
    for f in files:
      s = os.lstat(f)
      if addtypetags:
        typetags = self.__filetypetags(f)
      filelist.append((s[ST_INO], s[ST_MODE], ) + \
                s[ST_NLINK:ST_SIZE+1] + \
              (s[ST_MTIME], s[ST_ATIME]) + \
              tuple(s[ST_CTIME:]) + (f, pathtags + typetags))
    return filelist
              
  def __getfileinfofromls(self, addtypetags = 1):
    """ self.__getfileinfofromls() -> list of files from ls command 
    
    Format is:
        [[inode, permissions, links, owner, group, size, 
          Day, Mon(th), date, hh:mm:ss, year, filename],
         [...]
        ]
        
    """
    # Investigate date command perhaps? - see time module
    # TODO: Needs to handle links correctly...
    
    commandstring = "ls -i -l --full-time"
#    for file in self.__files.keys():
#      commandstring = commandstring + file + " "
    files = os.popen(commandstring)
    output = files.read()
    files.close()
    
    commandstring = "pwd"
    files = os.popen(commandstring)
    pathtags = string.split(files.read(), "/")
    files.close()
    pathtags[-1] = string.strip(pathtags[-1]) # remove nl
    del pathtags[0] # cos there's a leading /
    
    typetags = []
    
    filelist = []
    list = string.split(output, '\n')
    for file in list:
      if len(file) > 12 and file[:2] != "ls": # "Total" or "No such file"
        fileinfo = string.split(file)
    # (year, month, day, hour, minute, second, weekday, dayofyear, DST?)
        if len(fileinfo[1]) != 10: # not permissions
          continue
        h,m,s = string.split(fileinfo[9], ':')
        filetime = (int(fileinfo[10]), self.__month[fileinfo[7]],
                    int(fileinfo[8]), int(h), int(m), int(s), 
                self.__day[fileinfo[6]], 0, -1)
#               filetime = (1970, 1, 1, 0, 0, 0, 3, 0, -1)
        epochtime = int(time.mktime(filetime))
        if addtypetags:
          typetags = self.__filetypetags(file)
        # Convert permissions string to octal
        # fileinfo[1] = self.__permstooctal(fileinfo[1][1:])
        # convert numbers
        fileinfo[0] = int(fileinfo[0]) # inode
        fileinfo[2] = int(fileinfo[2]) # linkcount
        fileinfo[5] = int(fileinfo[5]) # size
        filelist.append(fileinfo[:6] + [epochtime] + fileinfo[11:] + [pathtags + typetags])
        
    return filelist

  def refresh(self): # update internal DB
    fileinfo = self.__getfileinfo()
    filedict = {}
#    print fileinfo
    for f in fileinfo:
      if self.__files.has_key(f[0]): # Keep existing tag info - not safe across file systems
        f = f[:-1] + (self.__files[f[0]][-1],)
      filedict[f[0]] = tuple(f[1:])
    self.__files = filedict
    self.__tagsfromfiles(self.__files)
  
  __unitspersecond = {"seconds" : 1, "minutes" : 60, "hours" : 3600, 
                        "days" : 3600*24, "weeks" : 3600*24*7}
    
  def __getsystemtag(self, tag):
    """ self.__getsystemtag(tag) -> list of filenames """
    # Need to keep i18n in mind for tags...

    # Name based
    # :name=nameexpr
    if tag[:6] == ":name=":
      return self.getfile(tag[6:])
    
    # Size based
    bytestart = string.find(tag, "bytes") # is it a byte thing?
    if (bytestart > -1) and (tag[bytestart-1] not in string.digits): 
      # Convert down to bytes
      numberstart = utils.string_find_next_of(tag, string.digits)
      numberend = utils.string_find_next_of(tag, string.letters, numberstart)
      val = int(tag[numberstart:numberend])
      if tag[numberend:] == "kilobytes":
        val = val * 1024
      elif tag[numberend:] == "megabytes":
        val = val * 1024 * 1024
      elif tag[numberend:] == "gigabytes":
        val = val * 1024 * 1024 * 1024
      tag = tag[:numberstart] + str(val) + "bytes"

    # Time based
    # TODO: i18n
    if tag==":today" or tag==":yesterday":
      ltime = time.localtime(time.time())
      todaystart = time.mktime(ltime[:3] + (0, 0, 0) + ltime[6:])
      if tag==":today":
        tag = ":atleast" + str(int(todaystart)) + "seconds"
      if tag==":yesterday":
        yesterdaystart = todaystart - (3600*24)
        return self.__ls(":atleast" + str(int(yesterdaystart)) + 
                "seconds/:atmost" + str(int(todaystart)) + "seconds")
    
    if tag==":thisweek":
      ltime = time.localtime(time.time())
      # mktime handles negative days properly :-)
      weekstart = time.mktime(ltime[:2] + 
                        (ltime[2]-ltime[6], 0, 0, 0, 0) + ltime[7:])
      tag = ":atleast" + str(int(weekstart)) + "seconds"
            
    if string.find(tag, "last") > -1:
      # Convert all times to seconds
      # TODO: MAY NOT WORK CORRECTLY ACROSS DST CHANGEOVER
      currentsystemtime = time.time()
      
      numberstart = utils.string_find_next_of(tag, string.digits)
      numberend = utils.string_find_next_of(tag, string.letters, numberstart)
      timebefore = int(tag[numberstart:numberend])
      
      units = tag[numberend:]
      if self.__unitspersecond.has_key(units):
        tagtime = currentsystemtime - (timebefore * self.unitspersecond(units))
      else:
        ltime = time.localtime(currentsystemtime)
        if units == "months":
          ltime = (ltime[0], ltime[1] - timebefore) + ltime[2:]
        elif units == "years":
          ltime = (ltime[0] - timebefore, ) + ltime[1:]
        tagtime = time.mktime(ltime)
        
      tag = ":atleast" + str(int(tagtime)) + "seconds"
      
    if (string.find(tag, "exactly") > -1 or string.find(tag, "at") > -1 ):
      numberstart = utils.string_find_next_of(tag, string.digits)
      numberend = utils.string_find_next_of(tag, string.letters, numberstart)
      val = int(tag[numberstart:numberend])
      # filelist = self.__getfileinfo()
      # print val, filelist
      outlist = []
      if tag[1:numberstart] == "atleast":
        fun = lambda a,b: a > b
      elif tag[1:numberstart] == "atmost":
        fun = lambda a,b: a < b
      else:
        fun = lambda a,b: a == b
      
      # print tag[:numberstart], fun(0,1), fun(1,0), fun(0,0)
      if bytestart > -1:
        getval = lambda x, idx=self.__filesize: x[idx]
      elif string.find(tag, "seconds") > -1:
        getval = lambda x, idx=self.__filemdate: x[idx]        
      else: # tag count
        getval = lambda x, idx=self.__filetags: len(x[idx])
        
      for fid in self.__files.keys():
        # print val, self.__files[fid][self.__filesize], self.__files[fid][self.__filename]
        if fun(getval(self.__files[fid]), val):
          outlist.append(fid)
            
      return outlist
        
    return []

  def savesearch(self, tag, search):
    """ self.savesearch(tag, searchstring)
    
    Adds or replaces search tag with searchstring
    """
    self.__searches[tag] = search

  def delsearch(self, tag):
    if self.__searches.has_key(tag):
      del self.__searches[tag]
  
  def showsearches(self):
    return self.__searches

  __tagmask = 0x01
  __filemask = 0x02    

  def expandwildcards(self, tag, flags=0xFF):
    restring = string.replace(tag, ".", r"\.")
    restring = string.replace(restring, "?", ".")
    restring = string.replace(restring, "*", ".*?")
    restring = "^" + restring + "$"
    rec = re.compile(restring)
    
    expandlist = []
    
    if flags & self.__filemask:
      expandlist.extend(self.__filenames.keys())
    
    if flags & self.__tagmask:
      expandlist.extend(self.__tags.keys())
        
    matches = []
    for t in expandlist:
      if rec.match(t) is not None:
        matches.append(t)
    return matches
    
  def __wildcardstring(self, tag, flags=0xFF):
    tagexpr = "("
    for t in self.expandwildcards(tag, flags):
      tagexpr = tagexpr + t + " "
#    if tagexpr[-1] != "(":
#      tagexpr = tagexpr[:-1] 
    tagexpr = tagexpr[:-1] + ")"
#    print tagexpr
    return tagexpr
  
  def testwildcards(self, tag):
    return self.__wildcardstring(tag, self.__tagmask)
    
  # Need to find a way to combine this and getfile
  def gettag(self, tag):
    """ self.gettag(tag) -> list of filenames
    
    Returns a list of files that match the given simple tag,
        or files whose tags match the given wildcards.
    Supports ? for a single character, * for several
    characters and !tag to match all files that do not
    possess the given tag.
    """
    if tag == None or string.strip(tag) == "":
      return []
    if tag[0] == ":":
      return self.__gettag(tag)
    if utils.string_find_next_of(tag, "*?") > -1:
      return self.__ls(self.__wildcardstring(tag, self.__tagmask))
    if tag[0] == "!":
      return setdifference(self.__files.keys(), self.__gettag(tag[1:]))
    else:
      return self.__gettag(tag)
    
  def __gettag(self, tag):
    """ self.__gettag(tag) -> list of filenames
    
    Returns a list of files that match the given simple tag.
        For multiple tags, use self.ls(tags)
    """
    # Needs to handle wildcards
    # Use regex:     * -> .*     ? -> .
    if tag[0] == ":": # System tag
      if tag[1] == ":": # It's a search
        return self.__ls(self.getsearch(tag[2:]))
      else: # We need to do some fs handling
        return self.__getsystemtag(tag)
      elif self.__tags.has_key(tag):
        return self.__tags[tag]
      else:
        return []

  def getsearch(self, tag):
    """ self.getsearch(tag) -> list of searches
    
    Returns the tag search associated with the given
        argument, or the empty string if no search is
    found.
    """
    if self.__searches.has_key(tag):
      return self.__searches[tag]
    else:
      return ""

  def getfile(self, tag):
    """ self.getfile(tag) -> list of filenames
    
    Returns a list of files that match the given simple filename,
        or files whose filenames match the given wildcards.
    Supports ? for a single character, * for several
    characters and !tag to match all files that do not
    possess the given tag.
    """
    if tag == None or string.strip(tag) == "":
      return []
    if utils.string_find_next_of(tag, "*?") > -1:
      return self.__ls(self.__wildcardstring(tag, self.__filemask))
    if tag[0] == "!":
      return setdifference(self.__files.keys(), self.__getfile(tag[1:]))
    else:
      return self.__getfile(tag)
    
  def __getfile(self, file):
    # Needs to handle wildcards
    # Use regex:     * -> .*     ? -> .    . -> \.
    if self.__filenames.has_key(file):
      return self.__filenames[file]
    else:
      return []

  def __simplels(self, tag):
    if self.__tags.has_key(tag):
      fidlist = self.__tags[tag]
    elif self.__filenames.has_key(tag):
      fidlist = self.__filesnames[tag]
    else:
      fidlist =  []
    matchingfiles = []
    for f in fidlist:
      matchingfiles.append(self.__files[f][self.__filename])
    return matchingfiles

  def __fieldstostring(self, tup, fieldlist, sep = "\t", flags = ""):
    outstr = ""
    for f in fieldlist:
      # Special field formatting here if required
      if f == self.__fileperm:
        outstr = outstr + "p" + str(tup[f]) + sep
      elif f in self.__alltimes:
        outstr = outstr + time.ctime(tup[f]) + sep
      elif f == self.__filetags:
        outstr = outstr + "tags:"
        for t in tup[f]:
          outstr = outstr + " " + t + ","
        outstr = outstr[:-1] + sep # strip trailing comma
      else:
        outstr = outstr + str(tup[f]) + sep
    if outstr != "":
      outstr = outstr[:-len(sep)]
    return outstr
    
  def __filetostring(self, fid, formatstring = ""):
    if string.find(formatstring, "-l") > -1:
      return "\n" + str(fid) + " " + self.__fieldstostring(self.__files[fid], range(0,self.__filemdate+1) + [self.__filename, self.__filetags], " ")
    elif string.find(formatstring, "-t") > -1:
      return "\n" + self.__fieldstostring(self.__files[fid], [self.__filename, self.__filetags])
    elif string.find(formatstring, "-f") > -1:
      return str(fid)
    else:
      return self.__files[fid][self.__filename]
    
  def ls(self, args, format = ""):
    """ self.ls(tag, format = "") -> list of files
    
    tag can be:
        a single word
        a list of words seperated by / and space where:
        space indicates an OR operation
        / indicates an AND operation
    
    word can be:
        a string of alphanumeric characters
        a system tag starting with :
        a saved-search tag starting with ::
        
    List of files defaults to a list of file names
    Other options are:
        -l --long      Full file details
           --fids      List of fids
            -t --tags      List of filename and tags
        
    """
    opt = "lt"
    longopt = ["long", "fids", "tags"]
    options, tags = getopt.getopt(string.split(args), opt, longopt)
    tag = ""
    for t in tags:
      tag = tag + " " + t
    filelist = self.__ls(self.pwd() + "/(" + string.strip(tag) + ")")
    
    # remove non-formatting options, then...
    if format == "":
      setremove(options, ("-f", ""))
      # ...process remaining options
      for o in options:
        if o[0][:2] == "--":
          if o[0][2:] == "long":
            format = format + " -l"
          elif o[0][2:] == "fids":
            format = format + " -f"
          elif o[0][2:] == "tags":
            format = format + " -t"
        else:
          format = format + " " + o[0]
    # Convert ids to required format
    outlist = []
    for fid in filelist:
      outlist.append(self.__filetostring(fid, format))
    return outlist

  __bracketcalls = 0
  def __bracketls(self, tag):
    self.__bracketcalls = self.__bracketcalls + 1 # For unique ID
    # NOTE: Overflow should be OK here, but may fail if one tag string
    # has more bracket pairs than there are unique integers.
    # I don't expect anyone to be typing any such string
    bracketcount = 0
    searchterms = {}
    bracketstarts = [string.find(tag, "(")]
    bracketends = [string.find(tag, ")")]
    bracketlist = []
    while bracketstarts[-1] > -1:
      bracketstarts.append(string.find(tag, "(", bracketstarts[-1]+1))
      bracketends.append(string.find(tag, ")", bracketends[-1]+1))
    # Remove 'bracket not found' entries (i.e. -1)
    bracketstarts = bracketstarts[:-1]
    bracketends = bracketends[:utils.listfind(bracketends, -1)]
    if len(bracketstarts) != len(bracketends):
      return []
    bracketstarts.reverse()
    for bracket in bracketstarts:
      closebracket = smallestatleast(bracketends, bracket)
      bracketends.remove(closebracket)
      bracketlist.append((bracket, closebracket))
    for p in bracketlist:
      searchtag = ":p" + str(self.__bracketcalls) + "," + \
                  str(p[0]) + "," + str(p[1])
      searchtext = tag[p[0]+1:p[1]]
      tag = tag[:p[0]] + "::" + searchtag + tag[p[1]+1:]
      searchterms[searchtag] = searchtext
        
    self.__searches.update(searchterms)
    results = self.__ls(tag)
    for s in searchterms.keys():
      del self.__searches[s]
        
    return results

  # Need to add ! NOT operator
  def __ls(self, tag):
#    print "__ls(", tag, ")"
    # TODO: Need to allow wildcards
    if tag == None or string.strip(tag) == "":
      return self.__files.keys()
    if string.find(tag, "(") > -1:
      return self.__bracketls(tag)
    orlist = string.split(tag)
    filelist = []
    for ortag in orlist:
      andlist = string.split(ortag, '/')
      andfiles = self.__files.keys()
      for andtag in andlist:
        thisfiles = setunion(self.gettag(andtag), self.getfile(andtag)) 
        andfiles = setintersection(andfiles, thisfiles)
      filelist = setunion(filelist, andfiles)
    return filelist

  def open(self, tag):
    """ self.open(tag) -> [files]

    Return a list of open files matching tag.
    """
    files = self.__ls(tag)
    filelist = []
    
    for f in files:
        name = self.__filetostring(f)
        try:
            filelist.append(open(name))
        except IOError:
            print 'Error opening', name

    return filelist
         
  def addown(self, file, owner):
    """ self.addown(file, owner) 
    
    Add an owner to a file
    """
    if self.__files.has_key(file):
      setappend(self.__files[file][0], owner)
    else:
      self.__files[file] = (["user", owner], [])

  def delown(self, file, owner):
    """ self.delown(file, owner) 
    
    Remove an owner from a file
    """
    if self.__files.has_key(file):
      setremove(self.__files[file][0], owner)
      if(self.__files[file][0] == []):
        self.__files[file][0] = ["orphan"]
    
  def __cp(self, fid, tag):
    if self.__files.has_key(fid):
      setappend(self.__files[fid][self.__filetags], tag)
    else:
      raise FileNotFound
            
    addhashdata(self.__tags, tag, fid)

  def cp(self, file, tag):
    if string.find(tag[0],":") > -1:
      print "Cannot assign to system tag"
      return 1
    if utils.string_find_next_of(tag, "/ ") > -1:
      tag = string.split(tag, " ", 1) # take only first arg
      taglist = string.split(tag[0], "/")
      for t in taglist:
        print "self.cp(" + file + ", " + t + ")"
        self.cp(file, t)
      return None
    for fid in self.getfile(file):
      self.__cp(fid, tag)
      return None
        
  def __rm(self, fid, tag):
    if self.__files.has_key(fid):
      setremove(self.__files[fid][self.__filetags], tag)
    else:
      raise FileNotFound
    if self.__tags.has_key(tag):
      setremove(self.__tags[tag], fid)

  def rm(self, file, tag, verify = 0):
    if utils.string_find_next_of(tag, "/ ") > -1:
      tag = string.split(tag, " ", 1) # take only first arg
      taglist = string.split(tag[0], "/")
      for t in taglist:
        self.rm(file, t, verify)
      return
    for fid in self.getfile(file):
      if (not verify) or ask("Delete " + self.__fid2file(fid) + "? Are you sure?"):
        # Insert are you sure message?
        self.__rm(fid, tag)

  def cd(self, tag):
    if tag == ".." or tag == andsep:
      self.__context = "()"
    elif tag == ".":
      self.__context = self.__context
    else:
      self.__context = "(" + tag + ")"
      
  def pwd(self):
    return self.__context
    
  beforelist = []
  afterlist = []
    
  def tabcompletionextend(self, before, after):
    self.beforelist = before
    self.afterlist = after
    
  def tabcompletion(self, text, state):
    """ Return the tab completion for text for tags or files
    
    This is called successively with state == 0, 1, 2, ... until it
    returns None
    """
    if state == 0:
      self.__completes = self.beforelist + self.__ls(text + "*") + self.afterlist
    try:
      return self.__files[self.__completes][self.__filename]
    except IndexError:
      return None
    
def testsuite():
  t = tagfs(testdata)
  print t
  print "ls bandname :", t.ls("bandname")
  print "ls !bandname :", t.ls("!bandname")
  print "ls -l file.txt :", t.ls("file.txt", "-l")
  print "ls notag :", t.ls("notag")
  print "ls test/music :", t.ls("test/music")
  print "ls music text :", t.ls("music text")
  print "ls test/text bandname :", t.ls("test/text bandname")
  t.cp("file.txt", "bandname")
  print "cp file.txt bandname :", t.ls("file.txt", "-l"), t.ls("bandname")
  t.cp("file.txt", "newtag")
  print "cp file.txt newtag :", t.ls("file.txt", "-l"), t.ls("newtag")
  t.rm("file.txt", "bandname")
  print "rm file.txt bandname", t.ls("file.txt", "-l"), t.ls("bandname")
  t.savesearch("bandnews", "bandname/:last2months")
  t.saveDB("pickle.tagfs")
  t.loadDB("pickle.tagfs")
  print "ls test/text bandname :", t.ls("test/text bandname")
  # t.exportXML("tagfs.xml")
  print "ls :atleast2megabytes", t.ls(":atleast2megabytes")
  print "ls :atmost20bytes", t.ls(":atmost20bytes")  
  print "ls :atleast3tags", t.ls(":atleast3tags")
  print "ls :last2months", t.ls(":last2months")
  print "ls :thisweek", t.ls(":thisweek")
  print "ls :today", t.ls(":today")
  print "ls :yesterday", t.ls(":yesterday")
  print "ls ::bandnews", t.ls("::bandnews")
  print "ls (bandname )", t.ls("(bandname )")
  print "ls test (bandname) :", t.ls("test/(text bandname)")
  t.cd("bandname")
  print "pwd : ", t.pwd()
  print "ls test : ", t.ls("test")
  print "open test : ", t.open("test")
  t.refresh()
  t.cd("..")
  print "ls test : ", t.ls("test", "-l")
  print "ls temp/python (International/text) : ", t.ls("temp/python (International/text)")
  print "wildcard te?? : ", t.testwildcards("te??")
  print "wildcard b* : ", t.testwildcards("b*")
  print "wildcard ?*t*? :", t.testwildcards("?*t*?")
  print "ls te?? : ", t.ls("te??")
  print "ls Java : ", t.ls("Java")
  print "open Java :::"
  javas = t.open("Java")
  for j in javas:
    print j.readline()
    j.close()
    
if __name__ == "__main__":
  testsuite()
