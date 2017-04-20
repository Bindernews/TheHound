
import io
import importlib
from struct import unpack
import sys

from identifier import *
import ioview

#################################
# Attempt to load PIL (or Pillow)
try:
    import PIL.Image
except ImportError:
    PIL = None
    print('Pillow not found, image support minimal')


#############
# Constants #
#############

PNG_CHUNK_IEND = b'IEND'
PNG_CHUNK_IHDR = b'IHDR'
JPEG_EOI = bytes.fromhex('FF D9')
IMAGE_MAX_SIZE = MEBIBYTE * 20

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

def pil_image_length(stream):
	try:
	    origin = stream.tell()
	    view = ioview.ReadView(stream, origin, stream.size)
	    img = PIL.Image.open(view, 'r')
	    # Force the image to load itself entirely
	    img.resize((2, 2))
	    # Reset stream back to origin for convenience
	    stream.seek(origin)
	    # Length is captured by view.max_pos
	    return view.max_pos - origin
	except IOError as e:
		return -1

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
            return Result('PNG', 'PNG image', length=length)
        except BaseException as e:
            print(e, file=sys.stderr)

class BasicImageResolver:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def identify(self, stream):
        if PIL:
            length = pil_image_length(stream)
        else:
            length = None
        return Result(self.name, self.description, length=length)
        
def load(hound):
    # Register PNGs
    hound.add_matches(PNG_PATTERNS, PngResolver())
    # Register JPEGs
    hound.add_matches(JPEG_PATTERNS, BasicImageResolver('JPEG', 'JPEG image'))
    # Register GIFs
    hound.add_matches(GIF_PATTERNS, BasicImageResolver('GIF', 'GIF image'))
    # Register BMPs
    hound.add_matches(BMP_PATTERNS, BasicImageResolver('BMP', 'Bitmap image'))
    # Register ICOs
    hound.add_matches(ICO_PATTERNS, BasicImageResolver('ICO', 'Windows icon'))
