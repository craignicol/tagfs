""" tagfs.py - demo for tagged filesystem

See tagfs.txt for more details.
This is probably quite inefficient for now.

Since this uses ls to retrieve file info, it is Unix only
"""
import utils
import string
import pickle
import os

testdata = { "file.txt" : (["user","group"], ["text","test"]),
             "music,mp3" : (["user", "share"], ["music","test","bandname"]),
             "web.html" : (["user", "httpd"], ["test","blog","bandname"]) }

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

class tagfs:
    __files = {}
    __tags = {}
    __searches = {}
    __fileformat = "pickle"

    def __tagsfromfiles(self, files):
        self.__tags = {} 
        for f in files.keys():
            filetags = files[f][0][:]
            filetags.extend(files[f][1])
            for t in filetags:
                if self.__tags.has_key(t):
                    self.__tags[t].append(f)
                else:
                    self.__tags[t] = [f]
    
    def __file2uid(self, file):
	""" private self.file2uid(file) -> uid
	
	Finds the unique id for the given file and tags
	"""
	return file
    
    def __uid2file(self, uid):
	""" private self.uid2file(uid) -> file
	
	Returns the filename of the file with the given unique id
        """
	return uid

    def __loadPickleDB(self, filename):
	f = open(filename)
	self.__files = pickle.load(f)
	self.__tagsfromfiles(self.__files)
	f.close()
	
    def __savePickleDB(self, filename):
	f = open(filename, "w")
	pickle.dump(self.__files, f)
	f.close()
    
    def __loadXMLDB(self, filename):
	utils.loadraw(filename)
	# Do XML processing here
	
    def __saveXMLDB(self, filename):
	outstr = "<tagfs>"
	for file in self.__files.keys():
	    outstr = outstr + "<file><name>" + self.__uid2file(file) \
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

    __fileperm = 0
    __filelinks = 1
    __fileowner = 2
    __filegroup = 3
    __filesize = 4
    __fileday = 5
    __filemonth = 6
    __filedate = 7
    __filetime = 8
    __fileyear = 9
    __filename = 10
    
    def __getfileinfo(self):
	""" self.__getfileinfo() -> list of lists from ls command 
	
	Format is:
	    [[permissions, links, owner, group, size, 
	      Day, Mon(th), date, hh:mm:ss, year, filename],
	     [...]
	    ]
	    
	"""
	
	# Investigate date command perhaps?
	
	commandstring = "ls -l --full-time"
#	for file in self.__files.keys():
#	    commandstring = commandstring + file + " "
	files = os.popen(commandstring)
	output = files.read()
	files.close()
	
	filelist = []
	list = string.split(output, '\n')
	for file in list:
	    if len(file) > 2 and file[:2] != "ls": # No such file...
		fileinfo = string.split(file)
		# Only add files we are managing with tags
		if (self.__files.has_key(fileinfo[-1])):
		    filelist.append(fileinfo)
		
	return filelist
	
	
    def __getsystemtag(self, tag):
	""" self.__getsystemtag(tag) -> list of filenames """
	# Need to keep i18n in mind for tags...
	
	secondssincemidnight = 2000 # Need system call for this
	secondsperday = 60*60*24
	
	if tag == "today":
	    tag = "last" + secondssincemidnight + "seconds"
	if tag == "yesterday":
	    return self.ls(":") # construct new search?
	
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
	if (bytestart > -1):
	    numberstart = utils.string_find_next_of(tag, string.digits)
	    numberend = utils.string_find_next_of(tag, string.letters, numberstart) 
	    val = int(tag[numberstart:numberend])
	    filelist = self.__getfileinfo()
	    # print val, filelist
	    outlist = []
	    if tag[1:numberstart] == "atleast":
		fun = lambda a,b: a > b
	    elif tag[1:numberstart] == "atmost":
		fun = lambda a,b: a < b
	    else:
		fun = lambda a,b: a == b
	    
	    # print tag[:numberstart], fun(0,1), fun(1,0), fun(0,0)
	    
	    for file in filelist:
		# print val, file[self.__filesize], file
		if fun(val, file[self.__filesize]):
		    outlist.append(file[self.__filename])
		    
	    return outlist
	    
	return []
    
    def gettag(self, tag):
	""" self.gettag(tag) -> list of filenames
	
	Returns a list of files that match the given simple tag.
        For multiple tags, use self.ls(tags)
	"""
	if tag[0] == ":": # System tag
	    if tag[1] == ":": # It's a search
		return self.ls(self.__getsearch(tag[2:]))
	    else: # We need to do some fs handling
		return self.__getsystemtag(tag)
        elif self.__tags.has_key(tag):
            return self.__tags[tag]
        else:
            return []

    def getfile(self, file):
        if self.__files.has_key(tag):
            return self.__files[tag]
        else:
            return []

    def __simplels(self, tag):
        if self.__tags.has_key(tag):
            return self.__tags[tag]
        elif self.__files.has_key(tag):
            return self.__files[tag]
        else:
            return []

    def ls(self, tag):
	""" self.ls(tag) -> list of files
	
	tag can be:
	    a single word
	    a list of words seperated by / and space where:
		space indicates an OR operation
		/ indicates an AND operation
	
	word can be:
	    a string of alphanumeric characters
	    a system tag starting with :
	    a saved-search tag starting with ::
	"""
        if utils.string_find_next_of(tag, ":/ ") == -1:
            return self.__simplels(tag)
        # TODO: Need to allow wildcards
        else:
	    orlist = string.split(tag)
	    filelist = []
	    for ortag in orlist:
		andlist = string.split(ortag, '/')
		andfiles = self.__files.keys()
		for andtag in andlist:
		    andfiles = setintersection(andfiles, self.gettag(andtag))
		filelist = setunion(filelist, andfiles)
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
	
    def cp(self, file, tag):
        if self.__files.has_key(file):
            setappend(self.__files[file][1], tag)
        else:
            self.__files[file] = (["user"], [tag])
            
        if self.__tags.has_key(tag):
            setappend(self.__tags[tag], file)
        else:
            self.__tags[tag] = [file]        

    def rm(self, file, tag):
        if self.__files.has_key(file):
            setremove(self.__files[file][1], tag)
        if self.__tags.has_key(tag):
            setremove(self.__tags[tag], file)

def testsuite():
    t = tagfs(testdata)
    print "ls bandname :", t.ls("bandname")
    print "ls file.txt :", t.ls("file.txt")
    print "ls notag :", t.ls("notag")
    print "ls test/music :", t.ls("test/music")
    print "ls music text :", t.ls("music text")
    print "ls test/text bandname :", t.ls("test/text bandname")
    t.cp("file.txt", "bandname")
    print "cp file.txt bandname :", t.ls("file.txt"), t.ls("bandname")
    t.cp("file.txt", "newtag")
    print "cp file.txt newtag :", t.ls("file.txt"), t.ls("newtag")
    t.rm("file.txt", "bandname")
    print "rm file.txt bandname", t.ls("file.txt"), t.ls("bandname")
    t.saveDB("pickle.tagfs")
    t.loadDB("pickle.tagfs")
    print "ls test/text bandname :", t.ls("test/text bandname")
    t.exportXML("tagfs.xml")
    print "ls :atleast2megabytes", t.ls(":atleast2megabytes")
    print "ls :atmost20bytes", t.ls(":atmost20bytes")    
    
if __name__ == "__main__":
    testsuite()
