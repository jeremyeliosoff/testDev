#!/usr/bin/python

execfile("/home/jeremy/curves/common.py")


clrTestRib = "/home/jeremy/curves/clrSpace.rib"
clrTestDir = "/home/jeremy/curves/ren/clrSpace"
clrTestTiff = clrTestDir + "/clrSpace.tiff"


def writeRib(tex, clrs):
	print "Writing rib with", tex
	rib = """	
Display """ + "\"" + clrTestTiff + "\""  + """ "file" "rgba" 
Shutter 0 1

PixelSamples 3 3
PixelFilter "sinc" 2 2
Format 888 500 1
Projection "orthographic"

Scale 0.975 0.975 1 # from GXFsc
Translate 0 0 1

Option "limits" "bucketsize" [16 16]
ShadingRate 1


WorldBegin
Scale 1.77777777778 1 1

	Surface "clrTest"
"""

	rib += "\"uniform string tex\" \"" + tex + "\"\n"
	for clr in clrs:
		rib += "\"uniform color " + clr[0] + "\" [ %f %f %f ]\n" % tuple(clr[1])
	rib += """
	Translate 0.0 0.0 0
	Color 1 0 0
	Polygon "P" [ 1.0 -1.0 0.0  1.0 1.0 0.0  -1.0 1.0 0.0   -1.0 -1.0 0.0 ]
WorldEnd

"""

	f = open(clrTestRib, 'w')
	f.write(rib)
	f.close()

def renRib(activeImg):
	cmd="shaderdl -d " + GdevDir + " " + GdevDir + "/*sl"
	print "executing " +cmd
	os.system(cmd)

	cmd = "renderdl " + clrTestRib
	print "executing " +cmd
	os.system(cmd)

	cmd = "convert " + clrTestTiff + " " + activeImg
	print "executing " +cmd
	os.system(cmd)
	print "Done.\n"
	

def writeClrSpaceDic(dic):
	f = open(clrSpaceDicFile, 'w')
	
	keys = dic.keys()
	keys.sort()
	for seq in keys:
		line = seq + "_vig"  # For backwards compatibility
		clrPairs = dic[seq]
		for name,clr in clrPairs.items():
			line += " " + name + ":" + str(clr[0]) + "," + str(clr[1]) + "," + str(clr[2])
		f.write(line + "\n")
	f.close()

from Tkinter import *
from tkColorChooser import askcolor              
import copy
import numpy as np

#from PIL import ImageTk, Image
import os



def hex_to_rgbInt(value):
	"""Return (red, green, blue) for the color given as #rrggbb."""
	value = value.lstrip('#')
	lv = len(value)
	return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgbInt_to_hex(red, green, blue):
	"""Return color as #rrggbb for the given color values."""
	return '#%02x%02x%02x' % (red, green, blue)

def rgb_dec_to_int(r, g, b):
	return int(r*255), int(g*255), int(b*255)

def rgb_int_to_dec(r, g, b):
	return float(r)/255, float(g)/255, float(b)/255

def hex_to_rgb(value):
	r,g,b = hex_to_rgbInt(value)
	return rgb_dec_to_int(r,g,b)

def rgb_to_hex(r, g, b):
	rr,gg,bb = rgb_dec_to_int(r, g, b)
	return rgbInt_to_hex(rr, gg, bb)

def limitClr(c):
	rComp, gComp, bComp = c
	rComp = max(0, rComp)
	gComp = max(0, gComp)
	bComp = max(0, bComp)

	ret = [rComp, gComp, bComp]
	if rComp > 1:
		ret = vMult(ret, 1.0/rComp)
	if gComp > 1:
		ret = vMult(ret, 1.0/gComp)
	if bComp > 1:
		ret = vMult(ret, 1.0/bComp)
	return ret


def getClrSum(rgb, c):
	# Treat this as a ray-plane intersection, where:
	# r and g define a plane (r^g is N)
	# c and b define point and vector of ray, respectively.
	r,g,b = rgb
	rN = normalize(r)
	gN = normalize(g)
	bN = normalize(b)
	n = np.cross(rN, gN);
	distCtoPlaneOnN = np.dot(c, n)
	distCtoPlaneOnBn = distCtoPlaneOnN/np.dot(bN, n)
	cToPlane = vMult(n, distCtoPlaneOnBn)
	intersect = vAdd(c, cToPlane)
	rComp = np.dot(rN, intersect)
	rComp *= 1.0/length(r)
	gComp = np.dot(gN, intersect)
	gComp *= 1.0/length(g)
	bComp = distCtoPlaneOnBn/length(b)

	return limitClr((rComp, gComp, bComp))


def getLatestKeyRen(seq):
	print "\n-------getLatestKeyRen"
	print "seq", seq
	seqVig = seq + "_vig"
	vDirs = glob.glob(GrenDir + "/" + seqVig + "/*")
	vDirs.sort()
	print "vDirs", vDirs
	rvDirs = glob.glob(vDirs[-1] + "/*")
	rvDirs.sort()
	print "rvDirs", rvDirs

	keyTiff = rvDirs[-1] + "/" + seqVig + "." + ("%04d" % getKey(seq)) + ".tiff"
	print "keyTiff", keyTiff
	latestKey = glob.glob(keyTiff)
	if len(latestKey) == 0:
		globStr = rvDirs[-1] + "/" + seqVig + ".*.tiff"
		print "globStr", globStr
		latestKeys = glob.glob(globStr)
		latestKeys.sort()
		if latestKeys[-1] < keyTiff:
			latestKey = [latestKeys[-1]]
		else:
			latestKey = [latestKeys[0]]

	print "latestKey", latestKey
	return latestKey[0]

	

	

class clrSpace():
	def btn_interactiveRen(self):
		print "\n-------btn_updateLatestKeyRen"
		seq = self.active

		cmd = GdevDir + "/mkCurves.py clrTestSeq=" + seq
		print "Executing " + cmd + "..."
		os.system(cmd)

		destImg = GrenDir + "/clrSpace/fullRen/" + seq + ".gif"
		cmd = "convert " + clrSpaceFullRen + " " + destImg
		print "Executing " + cmd + "..."
		os.system(cmd)
		self.imgInteractiveRen = PhotoImage(file=destImg);
		self.panelInteractiveRen.configure(image=self.imgInteractiveRen)

	def btn_updateLatestKeyRen(self,reconvert):
		print "\n-------btn_updateLatestKeyRen"
		seq = self.active
		latestKey = getLatestKeyRen(seq)
		destImg = GrenDir + "/clrSpace/latest/" + seq + ".gif"
		if reconvert:
			cmd = "convert -resize 355x200 " + latestKey + " " + destImg
			print "Executing", cmd
			os.system(cmd)
		self.imgLatest = PhotoImage(file=destImg);
		self.panelLatestRen.configure(image=self.imgLatest)
		#panel = Label(frameInteractiveRen, image = self.imgLatest)

	def center_window(self, width=300, height=200):
		# get screen width and height
		screen_width = self.root.winfo_screenwidth()
		screen_height = self.root.winfo_screenheight()

		# calculate position x and y coordinates
		x = (screen_width/2) - (width/2)
		y = (screen_height/2) - (height/2)
		self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

	def btn_renderAll(self):
		seqs = self.dic.keys()
		for seq in seqs:
			self.render(seq)
		self.updateUi()

	def btn_render(self):
		seq = self.active
		self.render(seq)
		self.updateUi()

	def render(self, seq):
		print "rendering", seq
		seqVig = seq + "_vig"
		imgRoot = GseqDir + "/" + seqVig + "/" + seqVig + "." + ("%04d" % getKey(seq))
		tex = imgRoot + ".tex"
		tiff = imgRoot + ".tiff"
		clrs = self.dic[seq].items()
		writeRib(tex, clrs)
		renRib(self.activeImg)

	def btn_getColor(self, args):
		seq, clrName, dic, butNum = args

		c = dic[seq][clrName]
		hx = rgb_to_hex(c[0], c[1], c[2])
		color = askcolor(color=hx) 
		print "color", color
		clrInt = color[0]
		if clrInt:
			clrDec = rgb_int_to_dec(clrInt[0], clrInt[1], clrInt[2])
			dic[seq][clrName] = clrDec
			self.buts[butNum].configure(bg = color[1])
			writeClrSpaceDic(dic)
			self.dic=dic

	def btn_getColorSum(self, args):
		seq, clrName, dic, butNum = args
		thisClrs = dic[seq]
		rgb = [thisClrs["r"], thisClrs["g"], thisClrs["b"]]
		print "rgb pos", rgb
		print

		c = dic[seq][clrName]
		hx = rgb_to_hex(c[0], c[1], c[2])
		color = askcolor(color=hx) 
		clrInt = color[0]
		if clrInt:
			clrDec = rgb_int_to_dec(clrInt[0], clrInt[1], clrInt[2])
			rgbCspace = getClrSum(rgb, clrDec)
			print "rgb:", rgb
			print "rgbCspace:", rgbCspace
			reconstruct = toClrSpace(rgb[0], rgb[1], rgb[2], rgbCspace)
			print "orrrrrrrrig", clrDec
			print "reconstruct", reconstruct
			reconstruct = limitClr(reconstruct)
			print "limiteeeeed", reconstruct
			dic[seq][clrName] = reconstruct
			reconHex = rgb_to_hex(reconstruct[0],reconstruct[1],reconstruct[2])
			self.buts[butNum].configure(bg = reconHex)
			writeClrSpaceDic(dic)
			self.dic=dic
	
	def btn_setActive(self, args):
		seq, butNum = args
		self.active = seq
		for sq,but in self.seqButs.items():
			print "seq", seq, "sq", sq
			if sq == seq:
				but.configure(bg='#666666')
				but.configure(fg='#EEEEEE')
			else:
				but.configure(bg='#CCCCCC')
				but.configure(fg='#111111')

		self.updateUi()

	def updateUi(self):
		self.label.configure(text=self.active)
		self.activeImg = clrTestDir + "/" + self.active + ".gif"
		self.img.configure(file=self.activeImg)

		self.btn_updateLatestKeyRen(reconvert=False)

		#self.imgPathLatestRen =  clrTestDir + "/latest/" + self.active + ".gif"
		#self.imgLatestRen = PhotoImage(file=self.imgPathLatestRen);
		#self.panelLatestRen.configure(image=self.imgLatestRen)

		self.imgPathInteractive =  clrTestDir + "/fullRen/" + self.active + ".gif"
		self.imgInteractiveRen = PhotoImage(file=self.imgPathInteractive);
		self.panelInteractiveRen.configure(image=self.imgInteractiveRen)
	

	def __init__(self):
		#sys.exit()
		dic = loadClrSpaceDic()

		self.root = Tk()
		self.center_window(1300, 800)
		self.active = orderedSeqs[0]
		self.activeImg = clrTestDir + "/" + self.active + ".gif"
		#self.updateUi()

		frameClr = Frame(self.root)
		frameClr.grid(row =0, column=0)


		rw = 0
		self.buts = []
		self.seqButs = {}
		self.dic = dic
		#seqs = dic.keys()
		#seqs.sort()
		for seqAbbrev in orderedSeqs:
			seq = seqAbbrev# + "_vig"
			clrs = dic[seq]
			clm = 0
			rgb = []
			for btnName in ["cUntrip",  "cUntripBright", "cTrip", "SELECT"]:
				if btnName == "SELECT":
					btnNameFull = seq
					but = Button(frameClr, text=btnNameFull, command=lambda args=(seqAbbrev, butNum): self.btn_setActive(args))
					but.grid(row=rw, column=clm)
					self.seqButs[seq] = but
				else:
					clr = clrs[btnName]
					hx = rgb_to_hex(clr[0], clr[1], clr[2])
					butNum = len(self.buts)
					if btnName == "cUntrip":
						but = Button(frameClr, text=btnName, bg=hx, command=lambda args=(seq, btnName, dic, butNum): self.btn_getColorSum(args))
					elif btnName == "cTrip":
						but = Button(frameClr, text=btnName, bg=hx, command=lambda args=(seq, btnName, dic, butNum): self.btn_getColorSum(args))
					else:
						rgb.append(clr)
						but = Button(frameClr, text=btnName, bg=hx, command=lambda args=(seq, btnName, dic, butNum): self.btn_getColor(args))
					but.grid(row=rw, column=clm)
					self.buts.append(but)

				clm += 1


				
			rw += 1

		print "self.seqButs"
		print self.seqButs
		print
		frameTestImg = Frame(self.root)
		frameTestImg.grid(row =0, column=1)

		butFrame = Frame(frameTestImg)
		butFrame.grid(sticky=W+E)
		self.label = Label(butFrame, text="You want me")
		self.label.grid(row=0,column=0,sticky=W+E)
		but = Button(butFrame, text="RENDER APPROX", command=lambda:self.btn_render())
		but.grid(row=0,column=1,sticky=W+E)
		#but = Button(butFrame, text="RENDER ALL", command=lambda:self.btn_renderAll())
		#but.grid(row=0,column=2,sticky=W+E)
		self.img = PhotoImage(file=self.activeImg);
		panel = Label(frameTestImg, image = self.img)
		panel.grid(row=1, column=0)

		frameLatestRen = Frame(self.root)
		frameLatestRen.grid(row =1, column=0)
		self.imgLatest = PhotoImage(file=GrenDir + "/clrSpace/latest/sunbeamCu.gif");
		self.panelLatestRen = Label(frameLatestRen, image=self.imgLatest)
		self.panelLatestRen.grid(row=0, column=0)
		but = Button(frameLatestRen, text="UPDATE LATEST", command=lambda:self.btn_updateLatestKeyRen(reconvert=True))
		but.grid(row=1,column=0,sticky=W+E)

		frameInteractiveRen = Frame(self.root)
		frameInteractiveRen.grid(row =1, column=1)
		self.panelInteractiveRen = Label(frameInteractiveRen, image = self.imgLatest)
		self.panelInteractiveRen.grid(row=0, column=0)
		but = Button(frameInteractiveRen, text="INTERACTIVE RENDER", command=lambda:self.btn_interactiveRen())
		but.grid(row=1,column=0,sticky=W+E)
		
		mainloop() 
clrSpace()
