#!/usr/bin/python

import os
from Tkinter import *
from tkColorChooser import askcolor              
import copy
import math
import numpy as np

mncDir = "/home/jeremy/graphics/mnc"
snapDir = mncDir + "/snapshots"
ribFile = mncDir + "/mnc.rib"
tifRen = mncDir + "/img.tif"
gifRen = mncDir + "/img.gif"
textImg = mncDir + "/gimp/text.png"
textImgClr = mncDir + "/gimp/textClr.png"
titleImg = mncDir + "/gimp/title.png"
titleImgClr = mncDir + "/gimp/titleClr.png"
infoImg = mncDir + "/gimp/info.png"
infoImgClr = mncDir + "/gimp/infoClr.png"
logoImg = mncDir + "/gimp/logo.png"
logoImgClr = mncDir + "/gimp/logoClr.png"
tempImg = mncDir + "/gimp/temp.png"
parmsFile = mncDir + "/parms"

def mix (a, b, m):
	return b*m + a*(1-m)

def mixV (a, b, m):
	ret = []
	for i in range(len(a)):
		ret.append(mix(a[i], b[i], m))
	return ret

def vecToString(v):
	s = str(v[0])
	for vv in v[1:]:
		s += " " + str(vv)
	return s



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
		c = self.parmDic[k]
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

		globalScale =  float(self.parmDic["globalScale"])
		resScale = float(self.parmDic["resScale"])
		rad = float(self.parmDic["rad"])
		rotOffs = float(self.parmDic["rotOffs"])
		nStuds = int(float(self.parmDic["nStuds"]))
		nSpokes = int(float(self.parmDic["nSpokes"]))
		clrCent = self.parmDic["clrCent"]
		clrEdge = self.parmDic["clrEdge"]
		clrEdgeDisk = self.parmDic["clrEdgeDisk"]
		clrText = self.parmDic["clrText"]
		thick = float(self.parmDic["thick"])
		scaleMult = float(self.parmDic["scaleMult"])
		diskCFlip = int(float(self.parmDic["diskCFlip"]))
		diskCentral = float(self.parmDic["diskCentral"])
		logoOfs = self.parmDic["logoOfs"]
		infoOfs = self.parmDic["infoOfs"]
		titleOfs = self.parmDic["titleOfs"]
		logoSc = self.parmDic["logoSc"]
		infoSc = self.parmDic["infoSc"]
		titleSc = self.parmDic["titleSc"]

		rib = 'Display "' + tifRen + '" "file" "rgb"'
		rib += """
			Shutter 0.2 0.8 

			PixelSamples 3 3
			PixelFilter "sinc" 2 2
			Format """ + str(210*resScale) + " " + str(297*resScale) + """ 1
			Projection "orthographic"



			WorldBegin
			Translate 0 0 3
			Scale """ + str(globalScale) + " " + str(globalScale) + " " + str(globalScale) + """
			Rotate """ + str(90) + """ 0 0 1
		"""
		for i in range(nSpokes):
			rib += "\n			Rotate " + str(360.0/nSpokes) + " 0 0 1"
			cSc = 1
			undim = .5
			clrSc = 1
			rib += """
			TransformBegin
				#Translate 0 0 """ + str(thick*nStuds) + """
"""

			for j in range(nStuds):
				edgy = float(j)/(nStuds-1)
				clr = mixV(clrCent, clrEdge, edgy)
				dim = 1-undim
				dim *= .5
				dim = pow(dim, .5)
				rib += "\n			Rotate " + str(rotOffs * 180.0/(nSpokes)) + " 0 0 1"
				tr = (j + 1 )*cSc
				cSc *= scaleMult
				minRad = thick/cSc
				rib += """
				Color """ + str(clr[0])  + " " + str(clr[1]) + " " + str(clr[2]) + """
				TransformBegin
					Translate """ + str(tr) + """ 0 """ + str(-minRad*2) + """
					Scale """ + str(cSc) + " " + str(cSc) + " " + str(cSc) + """
					Torus """ + str(rad) + """ """ + str(minRad) + """ 60 90 360 
				TransformEnd
				"""
				clrSc *= .5
				undim *= .5
			rib += """
			TransformEnd
"""

		k = 297.0/210
		k *= k
		rib += """
			Translate 0 0 1
			Color .05 .05 .05
			Surface "mnc"
			"uniform color cCent" [ """ + vecToString(clrEdgeDisk if diskCFlip == 0 else clrEdge) + """ ]
			"uniform color cEdge" [ """ + vecToString(clrEdge if diskCFlip == 0 else clrEdgeDisk) + """ ]
			"uniform float diskCentral" [ """ + str(diskCentral) + """ ]
			Disk 0 """ +  str(math.sqrt(1 + k)/globalScale) + """ 360
			WorldEnd
			"""

		f = open(ribFile, 'w')
		f.write(rib)
		f.close()

#cmd = "renderdl -progress -stats3 -statsfile /tmp/renOut " + ribFile + "\n"
		cmd = "renderdl " + ribFile + "\n"
		print "executing", cmd
		os.system(cmd)

#convert -gravity center -geometry +0+500 img.gif text.png -compose Lighten -composite tmp.png; convert -gravity center -geometry +0-600 tmp.png logo.png -compose Lighten -composite test.png 
		#cmd = "convert " + textImg + " -fill " + rgb_to_hex(.5, 1, 0) + " " + textImgClr

		cmd = "convert " + tifRen + " " + gifRen
		print "\nExecuting " + cmd + "..."
		os.system(cmd)
		print

		for img,ofs,sc in [(logoImg, logoOfs, logoSc), (titleImg, titleOfs, titleSc), (infoImg, infoOfs, infoSc)]:
		#cmd = "convert " + logoImg + " -fill '" + rgb_to_hex(clrText[0], clrText[1], clrText[2]) + "' -colorize 100% " + logoImgClr + "; "
		#cmd += "composite " + logoImg + " -compose Multiply " + logoImgClr + " " + logoImgClr
		#print "\nExecuting " + cmd + "..."
		#os.system(cmd)
		#print

			cmd = "convert " + img + " -resize " + sc + "% -fill '" + rgb_to_hex(clrText[0], clrText[1], clrText[2]) + "' -colorize 100% " + textImgClr + "; "
			cmd += "composite " + img + " -resize " + sc + "% -compose Multiply " + textImgClr + " " + tempImg
			print "\nExecuting " + cmd + "..."
			os.system(cmd)
			print

			cmd = "convert -gravity center -geometry +0-" + ofs + " " + gifRen + " " + tempImg + " -compose Lighten -composite " + gifRen + ";"
			print "\nExecuting " + cmd + "..."
			os.system(cmd)
			print

		#cmd += "convert -gravity center -geometry +0-" + logoOfs + " " + tempImg + " " + logoImgClr + " -compose Lighten -composite " + gifRen

		print "\nExecuting " + cmd + "..."
		os.system(cmd)
		print

		cmd = "convert " + gifRen + " -resize 50% " + gifRen
		print "\nExecuting " + cmd + "..."
		os.system(cmd)
		print


		#cmd = "convert " + tifRen + " " + gifRen
		#print "Executing " + cmd + "..."
		#os.system(cmd)
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
		cmd = "cp img.gif parms ren.py mnc.sl " + nex
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
