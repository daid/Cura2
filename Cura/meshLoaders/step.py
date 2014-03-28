"""
Attempt to implement STEP file reading.
STEP files are a complex file format that can properly describe curves.
Currently only the basic structure is read, no mesh data is parsed yet.
"""
__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import sys
import re

def splitParamString(data):
	ret = []
	m = 0
	b = 0
	q = False
	for n in xrange(0, len(data)):
		if data[n] == '\'':
			q = not q
		if not q and data[n] == '(':
			b += 1
		if not q and data[n] == ')':
			b -= 1
		if b == 0 and data[n] == ',':
			ret.append(parseData(data[m:n]))
			m = n + 1
	ret.append(parseData(data[m:]))
	return ret

def splitGroups(data):
	ret = []
	b = 0
	q = False
	m = 0
	for n in xrange(0, len(data)):
		if data[n] == '\'':
			q = not q
		if not q and data[n] == '(':
			b += 1
		if not q and data[n] == ')':
			b -= 1
			if b == 0:
				ret.append(parseData(data[m:n+1]))
				m = n + 1
	ret.append(parseData(data[m:]))
	return ret

def parseData(data):
	data = data.strip()
	if data.startswith('(') and data.endswith(')'):
		data = data[1:-1]
		return splitParamString(data)
	m = re.match('([A-Za-z0-9_]*) *\((.*)\)', data)
	if m is not None:
		return {'type': m.group(1), 'params': splitParamString(m.group(2))}
	try:
		return float(data)
	except ValueError:
		pass
	return data

def parseMainData(data):
	data = data.strip()
	if data.startswith('(') and data.endswith(')'):
		data = data[1:-1]
		return splitGroups(data)
	return parseData(data)

def setParent(l, nr, d):
	if type(d) is dict:
		for i in d['params']:
			setParent(l, nr, i)
	elif type(d) is list:
		for i in d:
			setParent(l, nr, i)
	elif type(d) is str and d.startswith('#'):
		l[int(d[1:])]['parent'] = nr

def loadStep(filename):
	dataList = {}

	f = open(filename, "r")
	for line in f:
		line = line.strip()
		if line == 'DATA;':
			for line in f:
				line = line.strip()
				if line == 'ENDSEC;':
					break

				m = re.match('#([0-9]+) *= *(.+);', line)
				if m is None:
					print 'Error parsing data: %s' % line
					continue

				nr = int(m.group(1))
				dataList[nr] = {'dataString': m.group(2)}
	f.close()

	for nr in dataList.keys():
		dataList[nr]['parent'] = None
	for nr in dataList.keys():
		dataList[nr]['data'] = parseMainData(dataList[nr]['dataString'])
		setParent(dataList, nr, dataList[nr]['data'])
	for nr in dataList.keys():
		if dataList[nr]['parent'] is None:
			print nr, dataList[nr]['dataString']

if __name__ == '__main__':
	loadStep(sys.argv[1])