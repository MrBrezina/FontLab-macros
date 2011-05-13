#FLM: Extract Mapping
__copyright__ =  """
Copyright (c) David Brezina (brezina@davi.cz), 2010. All rights reserved.
Redistribution and use of the script is limited by the BSD licence (http://creativecommons.org/licenses/BSD/).
"""

__version__ = "1.0"

__doc__ = """
Extract Mapping from the current font

"""

#################### Local Dialog, Functions & Constants ####################

def processGlyph(font, gl, index):
	"""
	Adds glyph to lists of selected glyphs and composites.
	"""

	selected.append(gl) # selected is global
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
		for gl in selected:
			if gl.unicode:
				U =	"0000" + str(hex(gl.unicode))[2:]
				print "0x%s\t%s" % (U[-4:].upper(), gl.name)
			else:
				print"\t%s" % gl.name