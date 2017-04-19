
import io
from struct import unpack
import sys
from identifier import Result

#############
# Constants #
#############

PNG_CHUNK_IEND = b'IEND'
PNG_CHUNK_IHDR = b'IHDR'

#######################
# Identifier Patterns #
#######################

JPEG_PATTERNS = [
	'FF D8 FF E0',
	'FF D8 FF E1',
	'FF D8 FF FE',
]

GIF_PATTERNS = [
	'47 49 46 38 39 61',
	'47 49 46 38 37 61',
]

PNG_PATTERNS = [
	'89 50 4E 47 0D 0A 1A 0A'
]

BMP_PATTERNS = [
	'42 4D 62 25',
	'42 4D F8 A9',
	'42 4D 76 02',
]

ICO_PATTERNS = [
	'00 00 01 00'
]

def read4UB(stream):
	return unpack('>I', stream.read(4))[0]

class PngResolver:
	def next_chunk(self, stream):
		"""
		Assumes there is a chunk at the current position in the stream.
		Returns the name of the current chunk and its length.
		Also advances the stream to the start of the next chunk.
		"""
		chunk_len = read4UB(stream)
		chunk_name = stream.read(4)
		stream.seek(chunk_len + 4, io.SEEK_CUR)
		return (chunk_name, chunk_len)

	def identify(self, stream):
		try:
			origin = stream.tell()
			# Skip to the beginning of the first PNG chunk
			stream.seek(origin + 8)
			# Check to make sure the first chunk is the IHDR chunk
			chunk_name, chunk_len = self.next_chunk(stream)
			if chunk_name != PNG_CHUNK_IHDR or chunk_len != 0x0D:
				return

			# Loop through till we find the final chunk
			while chunk_name != PNG_CHUNK_IEND:
				chunk_name, chunk_len = self.next_chunk(stream)

			# Now calculate the actual file length
			end = stream.tell()
			length = end - origin
			return Result('PNG', 'PNG image file', length=length)
		except BaseException as e:
			print(e, file=sys.stderr)
			# Ignore all errors
			pass

class JpegResolver:
	def identify(self, stream):
		return Result('JPEG', 'JPEG image file')

class GifResolver:
	def identify(self, stream):
		return Result('GIF', 'GIF image file')

class BmpResolver:
	def identify(self, stream):
		return Result('BMP', 'BMP image file')

class IcoResolver:
	def identity(self, stream):
		return Result('ICO', 'Windows icon file')
	
def load(hound):
	# Register JPEGs
	hound.add_matches(JPEG_PATTERNS, JpegResolver())
	# Register PNGs
	hound.add_matches(PNG_PATTERNS, PngResolver())
	# Register GIFs
	hound.add_matches(GIF_PATTERNS, GifResolver())
	# Register BMPs
	hound.add_matches(BMP_PATTERNS, BmpResolver())
	# Register ICOs
	hound.add_matches(ICO_PATTERNS, IcoResolver())
