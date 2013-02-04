#Matthias Pall Gissurarson/Tritlo's Assembly Compiler for the DCPU-16 	22. april 2012
#Use at your own risk.

import sys
import argparse 

#Tekur inn hex int, skilar lista af lengd n
def hexToBin(hexint, n):
	v = int(hexint,16)
	l = [0]*n
	for i in range(n):
		l[n -1 -i]= (v%2)
		v = v/2
	return l

def hexToBinaryString(hexstring):
	out = ''
	for i in hexstring:
		k =  bin(int(i,16))
		k = k.lstrip('0b')
		while len(k) < 4:
			k = '0'+k
		if littleendian:
			k = list(k)
			k.reverse()
			k = ''.join(k)
		out = out + k
	return out	

#tekur inn lista
def listToHex(c,n):
	l = []
	for i in c:
		l.append(i)
	s = []
	for i in range(n):
		s.append(0)
	
	for j in range(n):
		for i in range(4):
			try:
				s[j] = s[j] + int(l.pop())*2**(i)
			except IndexError:
				pass
	s.reverse()
	ret = ''
	for i in range(n):
		ret = ret+hex(s[i]).split('x')[1]
	return ret 

def include(filename,linur,lineplace):
	filename = filename.strip('"<>')	
	try :
		f = open(filename, 'r')
		innlinur = f.read().split('\n')
		f.close()
	except IOError :
		print ' Could not open included file' , filename
		sys.exit(0)
	innlinur.reverse()
	for line in innlinur:
		linur.insert(lineplace,line)

#Currently Supports Include
def PreProcess(linur):
	for i in range(len(PPLines)):
		ppl = PPLines[i].split(';')[0].split('/*')[0].split('#')[1]
		p  = ppl.split()
		first = p.pop(0)
		PPARGS[first](' '.join(p),linur,i)
	global PreProcessed
	PreProcessed = True

def Compile(linur):
	out = []
	outlist = []
	count,i , linecounter = 0,0,0
	while i < len(linur):
		linecounter = linecounter + 1
		c = linur[i].split(';')
		if len(c[0]) > 1:
			pp = c[0].split('#')
			if len(pp) > 1:
				PPLines.append(linur.pop(i))
				continue
			elif not PreProcessed:
				PreProcess(linur)

			e = c[0].split()
			d = e[0].split(':')
			if len(d) > 1:			
				e.remove(':'+d[1])
				c[0] = ' '.join(e)
			try:
				p, co = Assembler(c[0])
			except Exception:
				print 'Error in line %d: %s' %(linecounter,linur[i])
				return
			if len(d) > 1:
				labelList.append(d[1])
				labelPlace.append(hex(count))
			count = co + count
			outlist.append(p)
		i = i+1

	PreLabler(outlist)

	#Replace the labels
	faulty = False
	for i in range(len(outlist)):
		c = Labler(outlist[i])	
		out.extend(c)
		for h in c:
			if len(h) is not 4:
				faulty = True
				print 'Error in codeline %d, no such label %s: %s' %(i,h,outlist[i])

	if faulty:
		return

	return ' '.join(out)

#Assemble, without labels.
def Assembler(inp):
		
		#Replace comma's with spaces
		c = inp.replace(',',' ').split()
		#Convert the second to a hex number
		try:
			c[2] = hex(int(c[2]))
		except ValueError:
			pass
		
		except IndexError:
			try:
				c[1] = hex(int(c[1]))
			except ValueError:
				pass		

		inp = ' '.join(c)

		#Take out the next word values
		nw = []
		for j in range(len(c)):
			if c[j] not in VAL and c[j] not in OP:
				for i in range(-int(0xffff),-int(0x1f)):#0)):
					if inp.count(hex(-i)) > 0:
						for j in range(inp.count(hex(-i))):
							j = ''+hex(-i)
							j = j.split('x')[1]
							while len(j) < 4:
								j = '0'+j
							nw.append(j)
							inp = inp.replace(hex(-i),'nw',1)
		
		c = inp.replace(',',' ').split()
		lab = []
		labelAt = []
		for i in range(1,len(c)):
			if c[i] not in VAL:
				lab.append(c[i])
				labelAt.append(i)
		comb = []	
		for k in range(-len(c)+1,0):
			if -k in labelAt:
				comb.append(lab.pop())
			elif len(nw) > 0:
				comb.append(nw.pop())

		comb.reverse()
		b = []
		try:
			code = []
			for i in range(-len(c)+1,0):
				if -i not in labelAt:
					code.extend(hexToBin(VAL[c[-i]],6))
				else:
					code.extend(hexToBin(VAL['nw'],6))
			code.extend(hexToBin(OP[c[0]],4))
		except KeyError:
			code = []
			if 1 not in labelAt:
				code.extend(hexToBin(VAL[c[1]],6))
			else:
				code.extend(hexToBin(VAL['nw'],6))

			code.extend(hexToBin(NB[c[0]],6))
			code.extend([0,0,0,0])

		p = listToHex(code,4)
		for i in comb:
			p = p +' '+ i
		return p,(1+len(comb))

#Set in labels and transform into shortform if neccessary.
def Labler(line):
	c = line.split()
	i = 0
	poplist = []
	while i < len(c):
		if c[i] in labelList:
			lp = labelPlace[labelList.index(c[i])] 
			if int(lp,16) > 0x1f:
				c[i] = lp.split('x')[1]
				while len(c[i]) < 4:
					c[i] = '0'+c[i]

			else:
				poplist.append(i)
				k = hexToBin(c[0],16)
				l = list(c[0])
				
				if l[3] is '0':
					a = []
					for q in range(6):
						a.append(k.pop(0))
					tala = listToHex(a,2)
					result = int(tala,16)+int(lp,16) +1
					hr = hex(result)
					a = hexToBin(hr,6)
					for q in range(6):
						k.insert(0,a.pop(0))
					c[0] = listToHex(k,4)
					break;
				else:
					b = []
					for q in range(6):
						b.append(k.pop((i-1)*6))
					tala = listToHex(b,2)
					result = int(tala,16)+int(lp,16) +1
					hr = hex(result)
					a = hexToBin(hr,6)
					for q in range(6):
						k.insert((i-1),a.pop(0))
				c[0] = listToHex(k,4)
		i = i+1					
	poplist.reverse()
	for h in poplist:
		c.pop(h)
	return c

#We need to run this to get shortform labels
def PreLabler(inp):
	count = 0
	out = []
	#Update the location in memory based on how much we will shorten by shortform labels
	for i in range(len(inp)):
		#Split every line into it's components, after we've preassembled
		c = inp[i].split()
		for i in range(len(c)):
			if c[i] in labelList:
				k = labelList.index(c[i])
				#We know that if the label is from (0x0 to 0x20), we can make a short form of it, so we update the posistion of every label that appears later in the code
				if int(labelPlace[k],16) in range(0x20):
					for j in range(len(labelPlace)):
						if int(labelPlace[j],16) > count:
							labelPlace[j] = hex(int(labelPlace[j],16) - 1)
			count = count + 1

Ops = ['NonBasic','SET', 'ADD', 'SUB', 'MUL', 'DIV', 'MOD', 'SHL', 'SHR', 'AND', 'BOR', 'XOR', 'IFE', 'IFN', 'IFG', 'IFB']
OP=dict()
for i in range(16):
	OP[Ops[i]] = hex(i)

NB = {'RES':'0x0', 'JSR':'0x1'}

Vals = ['A','B','C','X','Y','Z','I','J','[A]','[B]','[C]','[X]','[Y]','[Z]','[I]','[J]','[nw+A]','[nw+B]','[nw+C]','[nw+X]','[nw+Y]','[nw+Z]','[nw+I]','[nw+J]','POP','PEEK','PUSH','SP','PC','O','[nw]','nw']
VAL = dict()
labelList = []
labelPlace = []
for i in range(64):
	if i < 32:
		VAL[Vals[i]] = hex(i)
	else:
		VAL[hex(i-32)] = hex(i)




PPARGS = {'include': include}
PPLines = []
PreProcessed = False


parser = argparse.ArgumentParser(description='Compiles DCPU-16 assembly into hexcode.')
parser.add_argument('-b', dest = 'binary', action ='store_true', help ='wether the output should be binary or hexcode')
parser.add_argument('-le', dest = 'littleendian', action ='store_true', help ='Add this flag if you want your output to be little endian')
parser.add_argument('infile', nargs=1, help='The assembly file to read from.')
parser.add_argument('outfile', nargs=1, help='The filename to write output to.')
args = parser.parse_args()
binary = args.binary
littleendian = args.littleendian



try :
	f = open(args.infile[0], 'r')
	linur = f.read().split('\n')
	f.close()
except IOError :
	print 'Could not open' , args.infile[0]
	sys.exit(0)

try:
	c = Compile(linur)
	if c is None:
		raise TypeError
except TypeError:
	sys.exit(0)
if binary:
	c = hexToBinaryString(''.join(c.split()))

if (not binary) and littleendian:
	c = hexToBinaryString(''.join(c.split()))
	c = list(c)
	c = list(listToHex(c,len(c)/4))
	out = ''
	for i in range(len(c)):
		if i >0 and i%4 is 0:
			out = out + ' '
		out = out + c[i]
	c = out
f = open(args.outfile[0],'w')
f.write(c)
f.close()
print c
