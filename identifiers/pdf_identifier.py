
from identifier import *
import io

THREE_NULLS = bytes([0, 0, 0])
ONE_NULL = bytes([0])
JUMP_SIZE = 32
MAXIMUM_SEARCH = MEBIBYTE * 16
PDF_EOF = b'%%EOF'
NAME = 'PDF'
DESC = 'Adobe PDF file'

PDF_PATTERNS = [
    '25 50 44 46'
]




class PdfResolver:

    def jump_find(self, stream, data, maximum_seek):
        data_len = len(data)
        while stream.tell() < maximum_seek:
            b = stream.read(data_len)
            if len(b) != data_len:
                print(b)
                return False
            if b == data:
                return True
            stream.seek(JUMP_SIZE - data_len, io.SEEK_CUR)
        return False

    def identify(self, stream):
        origin = stream.tell()
        maximum_seek = origin + MAXIMUM_SEARCH
        # We're going to cheat and guess the file size by looking for nulls in the stream
        if not self.jump_find(stream, THREE_NULLS, maximum_seek):
            return Result(NAME, DESC)

        # Now we look backwards and try to find %%EOF
        stream.seek(-JUMP_SIZE * 2, io.SEEK_CUR)
        # Where is the beginning of data in our stream
        data_origin = stream.tell()
        data = stream.read(JUMP_SIZE * 2)
        # Get the index of EOF
        index = data.rfind(PDF_EOF)
        # If EOF wasn't found, give up, too much effort
        if index < 0:
            return Result(NAME, DESC)
        # If EOF was found, search forward until we find a null and we'll assume that's probably the end
        # Yes I realize this is janky, but too bad.
        index_end = data.find(ONE_NULL) - 1
        return Result(NAME, DESC, length=data_origin + index_end - origin)

def load(hound):
	hound.add_matches(PDF_PATTERNS, PdfResolver())
