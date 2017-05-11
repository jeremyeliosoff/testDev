#!/usr/bin/python

import os
from Tkinter import *
from tkColorChooser import askcolor              
import copy
import math
import numpy as np

xByY = float(630)/891
mncDir = "/home/jeremy/graphics/mnc"
snapDir = mncDir + "/snapshots"
ribFile = mncDir + "/mnc.rib"
tifRen = mncDir + "/img.tif"
gifRen = mncDir + "/img.gif"
gifRenDisplay = mncDir + "/imgDisplay.gif"
tifRenPost = mncDir + "/imgPost.tif"
gifRenPost = mncDir + "/imgPost.gif"
gifRenPostDisplay = mncDir + "/imgPostDisplay.gif"
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

checkParms = ["compText", "renPre", "renPost"]

def exeCmd(cmd):
	print "executing", cmd
	os.system(cmd)

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


def loadParmDic(thisParmsFile=parmsFile):
	parmDic, parmsOrdered = loadThisParmDic(parmsFile)

	if not thisParmsFile == parmsFile:
		thisParmDic, thisParmsOrdered = loadThisParmDic(thisParmsFile)

		for k,v in parmDic.items():
			print "k:", k
			if k in thisParmDic.keys():
				print "OLD:", parmDic[k]
				parmDic[k] = thisParmDic[k]
				print "THS:", thisParmDic[k]
				print "NEW:", parmDic[k]
				print

	return parmDic, parmsOrdered


def loadThisParmDic(thisParmsFile):
	print "\nLoading", thisParmsFile
	parmDic = {}
	parmsOrdered = []
	f = open(thisParmsFile, 'r')
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

class renWin():
	def saveParmDic(self):
		print "\nin saveParmDic"
		f = open(parmsFile, 'w')
		#for k,v in self.parmDic.items():
		for k in self.parmsOrdered:
			v = self.parmDic[k]
			ent = self.entDic[k]
			print "k:", k, ", v:", v
			if type(v) == type([]): # is it a list?
				v = self.parmDic[k]
				f.write(k + " " + str(v[0]))
				for vv in v[1:]:
					f.write("," + str(vv))
				f.write("\n")
			else:
				if k in checkParms:
					v = self.parmVars[k].get()
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

	def renPreProcess(self):
		#print "\nin renPreProcess, self.entDic:", self.entDic
		print "\nin renPreProcess"
		self.saveParmDic()

		ty =  float(self.parmDic["ty"])
		globalScale =  float(self.parmDic["globalScale"])
		diskScale =  float(self.parmDic["diskScale"])
		resScale = float(self.parmDic["resScale"])
		displayY = float(self.parmDic["displayY"])
		rad = float(self.parmDic["rad"])
		rotOffs = float(self.parmDic["rotOffs"])
		nStuds = int(float(self.parmDic["nStuds"]))
		nSpokes = int(float(self.parmDic["nSpokes"]))
		clrCent = self.parmDic["clrCent"]
		clrEdge = self.parmDic["clrEdge"]
		clrCentDisk = self.parmDic["clrCentDisk"]
		clrEdgeDisk = self.parmDic["clrEdgeDisk"]
		clrText = self.parmDic["clrText"]
		thick = float(self.parmDic["thick"])
		scaleMult = float(self.parmDic["scaleMult"])
		diskCFlip = int(float(self.parmDic["diskCFlip"]))
		clrFadeCentral = float(self.parmDic["clrFadeCentral"])
		fadeCentral = float(self.parmDic["fadeCentral"])
		logoOfs = self.parmDic["logoOfs"]
		infoOfs = self.parmDic["infoOfs"]
		titleOfs = self.parmDic["titleOfs"]
		logoSc = self.parmDic["logoSc"]
		infoSc = self.parmDic["infoSc"]
		titleSc = self.parmDic["titleSc"]
		edgeFade = self.parmDic["edgeFade"]

		rib = 'Display "' + tifRen + '" "file" "rgb"'
		rib += """
			Shutter 0.2 0.8 

			PixelSamples 3 3
			PixelFilter "sinc" 2 2
			#Format """ + str(210*resScale) + " " + str(297*resScale) + """ 1
			Format """ + str(self.res[0]) + " " + str(self.res[1]) + """ 1
			Projection "orthographic"


			WorldBegin
			Translate 0 """ + str(ty) + """ 3
			Scale """ + str(globalScale) + " " + str(globalScale) + " " + str(globalScale) + """
			Rotate """ + str(90) + """ 0 0 1
		"""
		for i in range(nSpokes):
			rib += "\n			Rotate " + str(360.0/nSpokes) + " 0 0 1"
			cSc = 1
			undim = .5
			clrSc = 1
			rib += """
			Surface "edgeFade"
			"uniform float ndcFadeEdge" [ """ + str(edgeFade) + """ ]
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
			Surface "disk"
			"uniform color cCent" [ """ + vecToString(clrCentDisk) + """ ]
			"uniform color cEdge" [ """ + vecToString(clrEdgeDisk) + """ ]
			"uniform float clrFadeCentral" [ """ + str(clrFadeCentral) + """ ]
			"uniform float fadeCentral" [ """ + str(fadeCentral) + """ ]
			Disk 0 """ +  str(math.sqrt(1 + k)*diskScale) + """ 360
			WorldEnd
			"""

		f = open(ribFile, 'w')
		f.write(rib)
		f.close()
		
		self.renRib(ribFile)

		cmd = "convert " + tifRen + " " + gifRen
		exeCmd(cmd)
		print

		if self.parmDic["compText"] == 1:
			for img,ofs,sc in [(logoImg, logoOfs, logoSc), (titleImg, titleOfs, titleSc), (infoImg, infoOfs, infoSc)]:
			#cmd = "convert " + logoImg + " -fill '" + rgb_to_hex(clrText[0], clrText[1], clrText[2]) + "' -colorize 100% " + logoImgClr + "; "
			#cmd += "composite " + logoImg + " -compose Multiply " + logoImgClr + " " + logoImgClr
			#print "\nExecuting " + cmd + "..."
			#os.system(cmd)
			#print

				print "----- sc", sc
				scFl = float(sc)
				print "----- scFl", scFl
				print "----- self.res[1]", self.res[1]
				scRel = str(scFl * float(self.res[1])/1782)
				cmd = "convert " + img + " -resize " + scRel + "% -fill '" + rgb_to_hex(clrText[0], clrText[1], clrText[2]) + "' -colorize 100% " + textImgClr + "; "
				cmd += "composite " + img + " -resize " + scRel + "% -compose Multiply " + textImgClr + " " + tempImg
				exeCmd(cmd)
				print

				cmd = "convert -gravity center -geometry +0-" + str(int(float(ofs) * self.res[1])) + " " + gifRen + " " + tempImg + " -compose Lighten -composite " + gifRen + ";"
				exeCmd(cmd)
				print

		if displayY > 0:
			cmd = "convert " + gifRen + " -resize " + str(int(displayY * xByY)) + "x" + str(displayY) + " " + gifRenDisplay
		else:
			cmd = "cp " + gifRen + " " + gifRenDisplay
		exeCmd(cmd)
		print

		cmd = "tdlmake " + gifRen + " " + mncDir + "/img.tdl"
		exeCmd(cmd)
		print


		#cmd = "convert " + tifRen + " " + gifRen
		#print "Executing " + cmd + "..."
		#os.system(cmd)
		#print "BBBBB self.entDic:", self.entDic
		self.updateUi()
		#print "end renPreProcess, self.entDic:", self.entDic
		print
	
		
	def renRib(self, ribFile):
		exeCmd("shaderdl *sl")
		cmd = "renderdl " + ribFile + "\n"
		exeCmd(cmd)

	def renPostProcess(self):
		#print "\nin renPostProcess, self.entDic:", self.entDic
		print "\nin renPostProcess"
		self.saveParmDic()

		postAddBlur = self.parmDic["postAddBlur"]
		postTexMult = self.parmDic["postTexMult"]
		postK = self.parmDic["postK"]
		resScale = float(self.parmDic["resScale"])
		displayY = float(self.parmDic["displayY"])

		rib = 'Display "' + tifRenPost + '" "file" "rgb"'
		rib += """
			Shutter 0.2 0.8 

			PixelSamples 3 3
			PixelFilter "sinc" 2 2
			Format """ + str(210*resScale) + " " + str(297*resScale) + """ 1
			Projection "orthographic"
			Imager "mncImg"
			"uniform float addBlur" [ """ + str(postAddBlur) + """ ]
			"uniform float texMult" [ """ + str(postTexMult) + """ ]
			"uniform float intens" [ """ + str(postK) + """ ]
			ShadingRate .05
			WorldBegin
			WorldEnd
			"""

		f = open(ribFile, 'w')
		f.write(rib)
		f.close()

		self.renRib(ribFile)


		cmd = "convert " + tifRenPost + " " + gifRenPost
		print "\nExecuting " + cmd + "..."
		os.system(cmd)
		print

		if displayY > 0:
			cmd = "convert " + gifRenPost + " -resize " + str(int(displayY * xByY)) + "x" + str(displayY) + " " + gifRenPostDisplay
		else:
			cmd = "cp " + gifRenPost + " " + gifRenPostDisplay
		exeCmd(cmd)
		print

		self.updateUi()
		print

	def ren(self):
		if self.parmDic["renPre"] == 1:
			self.renPreProcess()
		if self.parmDic["renPost"] == 1:
			self.renPostProcess()

	def updateParmUi(self):
		for k, ent in  self.entDic.items():
			if k in checkParms:
				continue
			else:
				v = self.parmDic[k]
				print "Udating", k, "to", v
				if type(v) == type([]): # is it a list?
					hx = rgb_to_hex(v[0],v[1],v[2])
					ent.configure(bg=hx)
				else:
					ent.delete(0, "end")
					ent.insert(0, str(v))


	def updateUi(self):
		#print "in updateUi, self.entDic:", self.entDic
		resScale = float(self.parmDic["resScale"])
		self.res = (210*resScale, 297*resScale)
		if self.parmDic["renPost"] == 1:
			self.photo.configure(file=gifRenPostDisplay);
		else:
			self.photo.configure(file=gifRenDisplay);
		self.imgBut.configure(image=self.photo)
	
	def checkCmd(self, args):
		print "------------- args:", args
		k = args
		v = self.parmVars[k].get()
		print "v", v
		print
		self.parmDic[k] = v
		self.saveParmDic()
	
	def getLatestSnapdir(self, ofs=0):
		snapDirs = os.listdir(snapDir)
		snapDirs.sort()
		latest = snapDirs[-1]
		nexNumStr = ("%03d" % (int(latest) + ofs))
		nexDir = snapDir + "/" + nexNumStr
		return nexDir

	def restore(self):
		parmDir = snapDir + ("/%03d/parms" % int(self.restoreEntry.get()))
		print "\nRestoring", parmDir
		self.parmDic, self.parmsOrdered = loadParmDic(parmDir)
		print "self.parmDic", self.parmDic
		self.updateParmUi()
		self.updateUi()

	def snapshot(self):
		nexDir = self.getLatestSnapdir(1)

		os.makedirs(nexDir)
		cmd = "cp"
		for i in ["parms", "ren.py", "*sl"]:
			cmd += " " + mncDir + "/" + i
		cmd += " " + nexDir
		print "executing", cmd
		os.system(cmd)

		nexNumStr = nextDir.split("/")[-1]
		cmd = "cp " + gifRen + " " + nexDir + "/img." + nexNumStr + ".gif"
		print "executing", cmd
		os.system(cmd)

		
	def __init__(self):
		self.parmDic, self.parmsOrdered = loadParmDic()
		self.parmVars = {}
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
			lab = Label(frameControls, text=k)
			lab.grid(row=row, column=0)
			if k in checkParms:
				self.parmVars[k] = IntVar()
				#print "SSSSSS self.parmDic[k]", self.parmDic[k]
				self.parmVars[k].set(int(self.parmDic[k]))
				ent = Checkbutton(frameControls, variable=self.parmVars[k], command=lambda args=(k): self.checkCmd(args))
				ent.grid(row=row, column=1)
			elif type(v) == type([]): # is it a list?
				hx = rgb_to_hex(v[0],v[1],v[2])
				ent = Button(frameControls, width=10, bg=hx,command=lambda args=(k,v): self.btn_getColor(args))
				ent.grid(row=row, column=1)
			else:
				ent = Entry(frameControls)
				ent.insert(0, str(v))
				ent.grid(row=row, column=1)
				print "k:", k, "; ent.get(): ", ent.get()
			self.entDic[k] = ent
			row +=1

		self.snapBut = Button(frameControls, text="snapshot", command=lambda:self.snapshot())
		self.snapBut.grid(row=row, column=0)
		row += 1

		self.restoreBut = Button(frameControls, text="restore", command=lambda:self.restore())
		self.restoreBut.grid(row=row, column=0)

		latestVerDir = self.getLatestSnapdir()
		latestVer = int(latestVerDir.split("/")[-1])
		self.restoreEntry = Entry(frameControls)
		self.restoreEntry.insert(0, latestVer)
		self.restoreEntry.grid(row=row, column=1)


		#print "before renPreProcess, entDic:", self.entDic
		self.imgBut.configure(command=lambda:self.ren())
		self.imgBut.grid(row=0, column=1)
		self.updateUi()
		
		mainloop() 

renWin()
