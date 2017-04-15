
# Identifier for basic image files
from identifier import Result

JPEG_PATTERNS = [
	'FF D8 FF E1',
	'FF D8 FF E1',
	'FF D8 FF FE',
]

GIF_PATTERNS = [
	'47 49 46 38 39 61',
	'47 49 46 38 37 61',
]

PNG_PATTERNS = [
	'89 50 4E 47'
]

class PngResolver:
	def identify(self, stream):
		return Result('PNG')

class JpegResolver:
	def identify(self, stream):
		return Result('JPEG')

class GifResolver:
	def identify(self, stream):
		return Result('GIF')

def load(hound):
	# Register JPEGs
	hound.add_matches(JPEG_PATTERNS, JpegResolver())
	# Register PNGs
	hound.add_matches(PNG_PATTERNS, PngResolver())
	# Register GIFs
	hound.add_matches(GIF_PATTERNS, GifResolver())
