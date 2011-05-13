#FLM: Rename glyphs
__copyright__ =  """
Copyright (c) David Brezina (brezina@davi.cz), 2010. All rights reserved.
Redistribution and use of the script is limited by the BSD licence (http://creativecommons.org/licenses/BSD/).
"""

__version__ = "1.1"

__doc__ = """
Rename glyphs

**Rename glyphs** is a macro for batch glyph rename. Similarly to [FontLab on steroids](http://steroids.fontlab.net/), it uses *renaming schemes* (list of records: old glyphname<tab>new glyphname, example of such scheme is distributed with the installer). It renames all glyphs in the selection according to the scheme. The main advantage of this macro is that it changes not only the glyph names, but also any occurence of the old glyphname in classes, OpenType classes, and OpenType features is replaced with the new glyphname. That means that you can start developing your classes and features at any point during your workflow. Secondary, if the new names are unicode-based (uniXXXX or uXXXX), correct unicode is assigned to the glyph. That obviously does not apply to ligatures and stylistic variants (usually with some suffix) which typically are not supposed to have any unicode. **The macro is distributed for free.**

Note: switch of the OT palette when using this script.

Redistribution and use of the macro is limited by the BSD licence (http://creativecommons.org/licenses/BSD/). If you use it commercially, be nice and buy me a drink at ATypI or anywhere else we might meet. Any suggestions for improvements are welcome. The macro is distributed as is without any warranty, however any feedback is welcome at <brezina@davi.cz>.

"""

from robofab.interface.all.dialogs import GetFile
from dialogKit import *
import os
import re

def readRenamingScheme(path):
	"""
	Reads file with renaming scheme, creates dict newNames used for translation
	"""
	
	newNames = {}
	full = re.compile("^([^\s]+)\s+([^\s]+)\s*$")
	
	infile = file(path, "r")
	if infile:
		for line in infile.readlines():
			mFull = full.match(line)
			if line[0] != "%" and mFull:
				name = mFull.group(1)
				newNames[name] = mFull.group(2)
		infile.close()
		return newNames
	else:
		return False

def renameGlyph(font, oldName, newName, newOTClasses):
	"""
	Substitute new glyph name for all occurences
	of old glyph name in Classes, OT Features and OT Classes.
	Change Glyph name to the new name and assign unicode
	if new name is unicode-based.
	"""
	
	# regular expression for substituting the newName for the oldName when not part of any bigger glyph name
	# the trick with finial space is also necessary
	substituteName = lambda x: re.sub(r"([^\w,\.,\-,\_])%s(?=([^\w,\.,\-,\_]))" % re.escape(oldName), r"\1%s" % newName, x + " ").strip()
	
	# 0. find the glyph object
	gl = font[font.FindGlyph(oldName)]
	
	# 1a. assign new name
	gl.name = newName

	# 1b. add unicode for unicode-based names if there is not any
	if (newName[0:3] == "uni") and (len(newName) == 7) and (gl.unicodes == []):
		try:
			gl.unicodes = [int(newName[3:7], 16)]
		except:
			gl.unicodes = []
	elif (newName[0] == "u") and (len(newName) == 5) and (gl.unicodes == []):
		try:
			gl.unicodes = [int(newName[1:5], 16)]
		except:
			gl.unicodes = []
	
	# 2. change names in Classes
	oldClasses = font.classes
	newClasses = []
	for glyphClass in oldClasses:
		newClasses.append(substituteName(glyphClass))
	font.classes = newClasses

	# 3. change names in OT Features
	# read old features and substitute names
	newFeatures = []
	for oldFeature in font.features:
		newTag = oldFeature.tag
		newValue = oldFeature.value.replace("\r","\n").replace("\n\n","\n").replace("\n\n\n\n\n","\n")
		newValue = substituteName(newValue)
		newFeatures.append((newTag, newValue))
	# delete the old features
	for oldFeature in range(len(font.features) -1,-1,-1):
		del font.features[oldFeature]
	# write the new features
	for newFeature in newFeatures:
		newTag, newValue = newFeature
		font.features.append(Feature(newTag, newValue))

	# 4. change names in OT Classes
	if font.ot_classes is not None:
		newOTClasses = substituteName(newOTClasses)
		font.ot_classes = newOTClasses
	
	return newOTClasses


#################### Local Dialog, Functions & Constants ####################

def processGlyph(font, gl, index):
	"""
	Adds glyph to lists of selected glyphs and composites.
	"""

	selected.append(gl.name) # selected is global
	return True


#################### Program ####################

if __name__ == '__main__':
	processedGlyphs=0
	changedGlyphs=0
	font = fl.font
	newOTClasses = font.ot_classes

	# 1a. get the selection
	selected = []
	fl.ForSelected(processGlyph)

	if not selected:
		print "Select some glyphs first."
	else:
		# sort out the selection from the longest to the shortest glyph name
		# it is important for the name replacement to work properly
		selected.sort(lambda x, y: len(y) - len(x)) # optimalization of the previous

		path = GetFile("Select a renaming scheme to use:")

		if path:
			newnames = readRenamingScheme(path)
			if newnames:
				fl.output = ""
				print "This may take a while..."
				
				for glyphName in selected:
					processedGlyphs+=1
					if newnames.has_key(glyphName):
						if glyphName != newnames[glyphName]:
							newOTClasses = renameGlyph(font, glyphName, newnames[glyphName], newOTClasses)
							changedGlyphs+=1
			fl.UpdateFont()
			fl.output = ""
			print "Done:\n%d glyphs processed\n%d glyphs changed" % (processedGlyphs, changedGlyphs)