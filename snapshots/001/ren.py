#!/usr/bin/python

import os
from Tkinter import *
from tkColorChooser import askcolor              
import copy
import numpy as np

mncDir = "/home/jeremy/graphics/mnc"
snapDir = mncDir + "/snapshots"
ribFile = mncDir + "/mnc.rib"
tifRen = mncDir + "/img.tif"
gifRen = mncDir + "/img.gif"
parmsFile = mncDir + "/parms"

def mix (a, b, m):
	return b*m + a*(1-m)

def mixV (a, b, m):
	ret = []
	for i in range(len(a)):
		ret.append(mix(a[i], b[i], m))
	return ret


def loadParmDic():
	parmDic = {}
	parmsOrdered = []
	f = open(parmsFile, 'r')
	for line in f.readlines():
		k,v = line.split(" ")
		parmsOrdered.append(k)
		if "," in v:
			vVecFlt = []
			for st in v.split(','):
				vVecFlt.append(float(st))
			parmDic[k] = vVecFlt
		else:
			parmDic[k] = float(v)
	f.close()
	return parmDic, parmsOrdered

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

#writeRib()
class renWin():
	def saveParmDic(self):
		print "in saveParmDic, self.entDic:", self.entDic
		f = open(parmsFile, 'w')
		#for k,v in self.parmDic.items():
		for k in self.parmsOrdered:
			v = self.parmDic[k]
			print "k:", k, ", v:", v
			ent = self.entDic[k]
			print "ent:", ent
			if type(v) == type([]): # is it a list?
				v = self.parmDic[k]
				f.write(k + " " + str(v[0]))
				for vv in v[1:]:
					f.write("," + str(vv))
				f.write("\n")

			else:
				v = ent.get()
				self.parmDic[k] = v
			#self.entDic[k] = v
				f.write(k + " " + str(v) + "\n")
		f.close()

	def btn_getColor(self, args):
		k,c = args
		print "c:", c
		hx = rgb_to_hex(c[0], c[1], c[2])
		color = askcolor(color=hx) 
		print "color", color
		clrInt = color[0]
		clrDec = rgb_int_to_dec(clrInt[0], clrInt[1], clrInt[2])
		print "clrDec", clrDec
		self.parmDic[k] = list(clrDec)
		self.entDic[k].configure(bg=color[1])
		self.saveParmDic()

	def writeRib(self):
		print "\nin writeRib, self.entDic:", self.entDic
		self.saveParmDic()
		print "AAA self.entDic:", self.entDic

		Gsc =  int(float(self.parmDic["globalScale"]))
		resScale = int(float(self.parmDic["resScale"]))
		nStuds = int(float(self.parmDic["nStuds"]))
		nSpokes = int(float(self.parmDic["nSpokes"]))
		clrCent = self.parmDic["clrCent"]
		clrEdge = self.parmDic["clrEdge"]



		wid = .015
		rib = 'Display "' + tifRen + '" "file" "rgb"'
		rib += """
			Shutter 0.2 0.8 

			PixelSamples 3 3
			PixelFilter "sinc" 2 2
			Format """ + str(210*resScale) + " " + str(297*resScale) + """ 1
			Projection "orthographic"



			WorldBegin
			Translate 0 0 3
			Scale """ + str(Gsc) + " " + str(Gsc) + " " + str(Gsc) + """
			Rotate """ + str(90) + """ 0 0 1
		"""
		for i in range(nSpokes):
			rib += "Rotate " + str(360.0/nSpokes) + " 0 0 1"
			cSc = 1
			undim = .5
			clrSc = 1
			for j in range(nStuds):
				edgy = float(j)/(nStuds-1)
				clr = mixV(clrCent, clrEdge, edgy)
				dim = 1-undim
				dim *= .5
				dim = pow(dim, .5)
				rib += "Rotate " + str(360.0/(nSpokes*2)) + " 0 0 1"
				tr = (j + 1 )*cSc
				cSc *= .7
				c1 = str(dim)
				c2 = str((1-clrSc*cSc)*dim)
				c3 = str(clrSc*cSc*dim)
				rib += """
				Color """ + str(clr[0])  + " " + str(clr[1]) + " " + str(clr[2]) + """
				TransformBegin Translate """ + str(tr) + """ 0 0
				Scale """ + str(cSc) + " " + str(cSc) + " " + str(cSc) + """
				Torus 1 """ + str(wid/cSc) + """ 60 90 360 
				TransformEnd
				"""
				clrSc *= .5
				undim *= .5

		rib += """
			Translate 0 0 1
			Color .05 .05 .05
			Disk 0 20 360
			WorldEnd
			"""

		f = open(ribFile, 'w')
		f.write(rib)
		f.close()

#cmd = "renderdl -progress -stats3 -statsfile /tmp/renOut " + ribFile + "\n"
		cmd = "renderdl " + ribFile + "\n"
		print "executing", cmd
		os.system(cmd)

		cmd = "convert " + tifRen + " " + gifRen
		print "Executing " + cmd + "..."
		os.system(cmd)
		print "BBBBB self.entDic:", self.entDic
		self.updateUi()
		print "end writeRib, self.entDic:", self.entDic
		print

	def updateUi(self):
		print "in updateUi, self.entDic:", self.entDic
		self.photo.configure(file=gifRen);
		self.imgBut.configure(image=self.photo)
	
	def snapshot(self):
		snapDirs = os.listdir(snapDir)
		snapDirs.sort()
		latest = snapDirs[-1]
		nex = snapDir + "/" + ("%03d" % (int(latest) + 1))

		os.makedirs(nex)
		cmd = "cp img.gif parms ren.py " + nex
		print "executing", cmd
		os.system(cmd)

		
	
	def __init__(self):
		self.parmDic, self.parmsOrdered = loadParmDic()
		self.entDic = {}
		self.root = Tk()
		self.root.bind('<Escape>', lambda e: self.root.destroy())
		self.photo = PhotoImage(file=gifRen);
		self.frameMaster = Frame(self.root)
		self.frameMaster.grid()
		self.imgBut = Button(self.frameMaster, image=self.photo)
		frameControls = Frame(self.frameMaster)
		frameControls.grid(row=0, column=0)

		row = 1
		#for k,v in self.parmDic.items():
		for k in self.parmsOrdered:
			v = self.parmDic[k]
			if type(v) == type([]): # is it a list?
				hx = rgb_to_hex(v[0],v[1],v[2])
				ent = Button(frameControls, text=k, bg=hx,command=lambda args=(k,v): self.btn_getColor(args))
				ent.grid(row=row, column=1)
			else:
				lab = Label(frameControls, text=k)
				lab.grid(row=row, column=0)
				ent = Entry(frameControls)
				ent.insert(0, str(v))
				ent.grid(row=row, column=1)
				print "k:", k, "; ent: ", ent
			self.entDic[k] = ent
			row +=1

		self.snapBut = Button(frameControls, text="snapshot", command=lambda:self.snapshot())
		self.snapBut.grid(row=row, column=0)

		print "before writeRib, entDic:", self.entDic
		self.imgBut.configure(command=lambda:self.writeRib())
		self.imgBut.grid(row=0, column=1)
		
		mainloop() 

renWin()
