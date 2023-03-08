# Defines a set of functions I've found useful
import string

def listfind(ll, value):
  """ listfind(ll, value) -> integer
  
  Returns the index of the first occurance of value in the list ll
  or -1 if it was not found. Use this to avoid exception handling
  in the list.index() function.
  """
  index = 0
  for next in ll:
	if next == value:
	    return index
	index = index + 1
	
  return -1

def listfindnocase(stringlist, stringvalue):
  """ listfindnocase(stringlist, stringvalue) -> integer
  
  Returns the index of the first occurance of value in the list ll
  or -1 if it was not found. Use this to avoid exception handling
  in the list.index() function.
  
  Unlike listfind(), this function is case insensitive but only works
  on lists containing only strings.
  """
  index = 0
  value = string.lower(stringvalue);
  for next in stringlist:
	if string.lower(next) == value:
	  return index
	index = index + 1
	
  return -1

def loadraw(filename):
  """ loadraw(filename) -> string
  """
  
#   print 'File:', filename
  try:
    f = open(filename)
  except IOError:
    print 'Cannot open file:', filename
    return ''
  else:
    raw = f.read()
    f.close()
    return raw

def saveraw(filename, data):
  """ saveraw(filename, data) -> None
  
  Replaces or creates filename with the contents of data
  """
  try:
    f = open(filename, "w")
  except IOError:
    print 'Cannot open file:', filename
    return -1
  else:
    f.write(data)
    f.close()
    return 0
  
def defaultget(dict, key, defaultvalue):
  if dict.has_key(key):
    return dict[key]
  else:
    return defaultvalue

def find_placeholder(data, start, startquote='%%', endquote='%%', excludelist=[]):
  """ find_placeholder(data, start, startquote, endquote, excludelist) -> string

  Searched the string 'data', from position 'start' for the two quote
  symbols. Returns the text between startquote and nearest endquote for
  the first match not in excludelist and returns None if no
  such match is found.
  """
  
  tag_start = string.find(data, startquote, start)
  if tag_start == -1:
    return None
  tag_close = string.find(data, endquote, tag_start+1)
  if tag_close == -1:
    return None
  placeholder = data[tag_start+len(startquote):tag_close]
  if placeholder not in excludelist:
    return placeholder
  else:
    if verbose > 1:
      print 'Ignoring placeholder:', placeholder
    newstart = tag_start + len(startquote + placeholder + endquote)
    return find_placeholder(data, newstart, startquote, endquote, excludelist)

def mergedict(dict1, dict2):
  """ mergedict(dict1, dict2) -> dict3

  includes all elements of dict1 and those
  elements of dict2 whos keys do not match
  any in dict1.
  """
  
  dict3 = dict2.copy()
  process = dict1.keys()
  for key in process:
    dict3[key] = dict1[key]

  return dict3

def sort_tuple_on(idx, reverse=0):
  if reverse:
	reverse = -1
  else:
	reverse = 1
	
  def comp(a,b,n=idx,rev=reverse):
	if a[n] < b[n]:
	  return -1*rev
	elif a[n] > b[n]:
	  return 1*rev
	else:
	  return 0
	
  return comp

def safe_multisort_dict_on(idxs, reverse=[1]):
  """ Use this with list.sort to sort on multiple keys with defined order
  
  Args: idxs - list of keys to sort on, in order
	reverse - list of {-1,1} entries defining forward (1) or reverse (-1)
	ordering for the related entry in idxs.
	If reverse is shorter than idxs, it is padded with its last value.
  """
  if type(reverse) != type([]):
	reverse = [1]
  while len(reverse) < len(idxs):
	reverse.append(reverse[-1])
	
  def multicomp(a,b,ns=idxs,rever=reverse):
	if len(ns) == 0:
	  return 0
	
	def comp(a,b,n=ns[0],rev=rever):
	  if a.has_key(n) and b.has_key(n):
		if a[n] < b[n]:
		  return -1*rev
		elif a[n] > b[n]:
		  return 1*rev
		else:
		  return 0
		# If key does not exist, sort at end
	  elif a.has_key(n):
		return -1*rev
	  elif b.has_key(n):
		return 1*rev
	  else:
		return 0
	
	for ind in range(0,len(ns)):
	  result = comp(a,b,ns[ind],rever[ind])
	  if result != 0:
		return result
	  
	return 0
	  
  return multicomp

def safe_multisort_list_on(idxs, reverse=[1]):
  """ Use this with list.sort to sort on multiple keys with defined order
  
  Use list for searching lists or tuples, use
  dict for searching dictionaries.
  
  Args: idxs - list of keys to sort on, in order
	reverse - list of {-1,1} entries defining forward (1) or reverse (-1)
	ordering for the related entry in idxs.
	If reverse is shorter than idxs, it is padded with its last value.
  """
  if type(reverse) != type([]):
	reverse = [1]
  while len(reverse) < len(idxs):
	reverse.append(reverse[-1])
	
  def multicomp(a,b,ns=idxs,rever=reverse):
	if len(ns) == 0:
	  return 0
	
	def comp(a,b,n=ns[0],rev=rever):
	  if len(a) > n and len(b) > n:
		if a[n] < b[n]:
		  return -1*rev
		elif a[n] > b[n]:
		  return 1*rev
		else:
		  return 0
		# If key does not exist, sort at end
	  elif len(a) > n:
		return -1*rev
	  elif len(b) > n:
		return 1*rev
	  else:
		return 0
	
	for ind in range(0,len(ns)):
	  result = comp(a,b,ns[ind],rever[ind])
	  if result != 0:
		return result
	  
	return 0
	  
  return multicomp

def stripquotes(quotedstring, quotes='"{}'):
  """ Removes whitespace and quotes from the start and end of the string
  """
  
  quotes = quotes + string.whitespace
  returnstring = string.strip(quotedstring)
  idx = 0
  while (idx < len(returnstring)) and (string.find(quotes, returnstring[idx]) >= 0):
	idx = idx + 1
	
  returnstring = returnstring[idx:]
  idx = len(returnstring)-1
  while(idx >= 0) and (string.find(quotes, returnstring[idx]) >= 0):
	idx = idx - 1
	
  returnstring = returnstring[:idx+1]

  return returnstring

def removeall(s, toremove):
  if type(toremove) == type(""):
	return string.replace(s, toremove, "")
  elif type(toremove) == type([]):
	for rem in toremove:
	  s = string.replace(s, rem, "")
	return s
  else:
	return s

def sanitise(s, accept):
  """ Removes all characters from s that are not in accept
  """
  sane = ""
  
  for c in s:
	if string.find(accept, c) > -1:
	  sane = sane + c
	  
  return sane
	
def close_bracket(bracket):
  """ Returns the bracket that closes the given argument
  
  Known brackets are:    { }    ( )   [ ]   < >  " "
  """
  if bracket == "{":
	return "}"
  elif bracket == "(":
	return ")"
  elif bracket == "[":
	return "]"
  elif bracket == "<":
	return ">"
  elif bracket == "\"":
	return "\""
  else:
	return ""


def string_find_next_of(s, findlist, start=0, end=None):
  if end == None:
	end = len(s)
  lowest_index = -1
  for substr in findlist:
	lowest_index = positivemin(lowest_index, string.find(s, substr, start, end))
  return lowest_index

def string_replace_dict(s, d):
  """ string_replace_dict(s, d) -> string
  
  Replaces every key in d found in a copy of s with the corresponding entry
  Returns the new string
  """
  out = s[:]
  
  for p in d.items():
	out = string.replace(out, p[0], p[1])
  return out
	
def splitstring_close_bracket(s, bracket, start=0, end=None, allbrackets=0):
  """ For a given string, return the string up to the given bracket,
    the string enclosed between the given bracket and the bracket 
	that closes it, and the rest of the string as a tuple.
	
  Known brackets are:    { }    ( )   [ ]   < >  " "
  """
  if end == None:
	end = len(s)
  
  bracketpos = string.find(s, bracket, start, end)
  if (bracketpos == -1) or (close_bracket(bracket) == ""):
	return (s, "", "")
  
  first = s[:bracketpos]
  bracketstack = [bracket]
  # Use second option only when you know it's safe
  if allbrackets == 0:
	bracketlist = [bracket, close_bracket(bracket)]
	openbrackets = bracket
  else:
	bracketlist = ["{","}","(",")","[","]","<",">","\""]
	openbrackets = "{([<\""
  
  middle = s[bracketpos:]
  while len(bracketstack) > 0:
	bracketpos = string_find_next_of(s, bracketlist, bracketpos+1, end)
	if bracketpos == -1: # no closing bracket
	  return (s, "", "")
	if s[bracketpos] == close_bracket(bracketstack[-1]):
	  bracketstack.pop()
	elif string.find(openbrackets, s[bracketpos]) >= 0:
	  bracketstack.append(s[bracketpos])
	else: # unmatched closing bracket
	  return (s, "", "")
  
  middle = s[string.find(s,bracket,start,end):bracketpos+1]
  last = s[bracketpos+1:]
  
  return (first, middle, last)

def positivemin(a, b):
  """ If a>0 and b>0, returns min(a,b), otherwise returns max(a,b)
  """
  if min(a,b) > 0:
	return min(a,b)
  else:
	return max(a,b)
  
  
def removeduplicates(l):
  """ removeduplicates removes all duplicates from the list except the first.
  
  Returns a seperate list with the duplicates removed.
  If an object other than a list is provided, it is returned unchanged
  """
  if type(l) != type([]):
	return l
  founditems = []
  for item in l:
	if item not in founditems:
	  founditems.append(item)
	  
  return founditems

def smartsplit(s, sep=',', quotes=[('(', ')'), ('{', '}'), ('"', '"')], esc = '\\', removequotes = 0):
  """ reads in a line in csv format and creates a list.
  
  Each element of the list is terminated by the comma
  character, except where that character appears
  within a pair of quotes.
  
  Note: Currently cannot cope with escaped commas and quotes
  """
  openquotes = map(lambda x: x[0], quotes)
  record = []
  quotestring = reduce(lambda x, y: x + y[0] + y[1], quotes, "")
  
  while string.find(s, ',') > -1:
	nextquote = string_find_next_of(s, openquotes)
	nextsep = string.find(s, sep)
	if nextquote < 0 or nextsep < nextquote:
	  fields = string.split(s, sep, 1)
	  record.append(string.strip(fields[0]))
	  s = fields[1]
	else:
	  fields = splitstring_close_bracket(s, s[nextquote])
	  if removequotes:
		record.append(stripquotes(fields[1], quotestring))
	  else:
		record.append(fields[1])
	  s = fields[2][string.find(fields[2],sep)+1:]
	  
  if removequotes:
	record.append(stripquotes(string.strip(s),quotestring))
  else:
	record.append(string.strip(s))
	
  return record

##########################################
## All these convert... functions
## are for the argstovariables
## function
##########################################

def atobool(s):
  """ Converts a string to a bool
  
	'yes', 'true', '1' (or any non-zero int), 'on' -> 1
	'no', 'false', '0', '', (any other string) -> 0
  """
  try:
	return string.atol(s) != 0
  except ValueError:
	if string.lower(s) in ['yes', 'y', 'true', 't', 'on']:
	  return 1
	else:
	  return 0

def convertstring(s, basictype):
  if type(s) != type(""):
	return None
  if basictype == 'bool':
	return atobool(s)
  if type(basictype) == type(""):
	return s
  elif type(basictype) == type(0.0):
	return string.atof(s)
  elif type(basictype) == type(0):
	return string.atoi(s)
  elif type(basictype) == type(0L):
	return string.atol(s)
  elif type(basictype) == type([]):
	return smartsplit(s)
  elif type(basictype) == type(()):
	return tuple(smartsplit(s))
  elif type(basictype) == type({}):
	data = smartsplit(s)
	out = {}
	for entry in data:
	  e = string.split(entry, ':')
	  if len(e) == 1:
		out[string.strip(e[0])] = None
	  else:
		out[string.strip(e[0])] = string.strip(e[1])
	  return out
	else:
	  return None

def convertdict(d, basictype):
  for n in d.keys():
	if type(d[n]) == type(""):
	  try:
		d[n] = convertstring(d[n], basictype)
	  except ValueError:
		d[n] = None
	elif type(d[n]) in [type([]), type(())]:
	  d[n] = convertlist(d[n], basictype)
	elif type(d[n]) == type({}):
	  d[n] = convertdict(d[n], basictype)
	else:
	  d[n] = d[n]		    
  return d
	
def converttuple(t, basictype):
  for n in range(0, len(t)):
	if type(t[n]) == type(""):
	  try:
		value = convertstring(t[n], basictype)
	  except ValueError:
		value = None
	elif type(t[n]) == type({}):
	  value = convertdict(t[n], basictype)
	elif type(t[n]) in [type([]), type(())]:
	  value = convertlist(t[n], basictype)
	else:
	  value = t[n]
	  
	if (n < len(t)-1):
	  t = t[:n] + (value,) + t[n+1:]
	else:
	  t = t[:n] + (value,)
	  
    return t

def convertlist(l, basictype):
  if type(l) == type(()):
	return converttuple(l, basictype)
  for n in range(0, len(l)):
	if type(l[n]) == type(""):
	  try:
		l[n] = convertstring(l[n], basictype)
	  except ValueError:
		l[n] = None
	elif type(l[n]) == type({}):
	  l[n] = convertdict(l[n], basictype)
	elif type(l[n]) in [type([]), type(())]:
	  l[n] = convertlist(l[n], basictype)
	else:
	  l[n] = l[n]
  return l
  
def argstovariables(descriptions, args):
  """ Converts args to a dict variable list, based on descriptions.
  
  args is a dict of where args['variable name'] = 'a string'
  descriptions is a dict of tuples where:
	descriptions['variable name'] = (type, default value)
	
	type is a list of types.
	
	e.g. [[]] is a list of anything
	[[], (,), ""] is a list of tuples of 2 strings
	[""] is a string
	
	the special type 'bool' will convert
	  'yes', 'true', '1' (or any non-zero int), 'on' -> 1
	  'no', 'false', '0', '', (any other string) -> 0
  """
  variables = {}
  
  for v in descriptions.keys():
	if args.has_key(v):
	  s = args[v]
	  vartype = descriptions[v][0]
	  if type(s) != type(""):
		variables[v] = s
	  elif type(vartype) != type([]) or vartype == []:
		variables[v] = None
	  else:
		temp = s
		for nexttype in vartype:
		  if type(temp) == type({}):
			temp = convertdict(temp, nexttype)
		  elif type(temp) == type([]) or type(temp) == type (()):
			temp = convertlist(temp, nexttype)
		  elif type(temp) == type(""):
			try:
			  temp = convertstring(temp, nexttype)
			except ValueError:
			  temp = descriptions[v][0]
		  else: # leave it alone
			temp = temp
			
		variables[v] = temp
	else:
	  variables[v] = descriptions[v][1]
  
  return variables
