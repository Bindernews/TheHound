# Identify all ZIP files and other file types which are actually zip files

import collections
import io
from struct import unpack
import zipfile

import ioview
from identifier import *

#############
# Constants #
#############

BUFFER_SIZE = 4096
MEGABYTE = 1024 * 1024
MIMETYPE_FILE = 'mimetype'
EOCD_MAGIC = bytes.fromhex('50 4b 05 06')
CDFH_MAGIC = bytes.fromhex('50 4b 01 02')

################
# Pattern Data #
################

class IdInfo:
    def __init__(self, name, description, file_set):
        self.name = name
        self.description = description
        self.file_set = set(file_set)

MimetypeInfo = collections.namedtuple('MimetypeInfo', ['name', 'description', 'mimetype'])

ZIP_PATTERNS = [
    '50 4B 03 04 14'
]

ZIP_CONTENT_INFO = [
    IdInfo('DOCX', 'Microsoft Office Word', ['[Content_Types].xml', 'word/document.xml']),
    IdInfo('XLSX', 'Microsoft Office Excel', ['[Content_Types].xml', 'xl/workbook.xml']),
    IdInfo('PPTX', 'Microsoft Office Powerpoint', ['[Content_Types].xml', 'ppt/presentation.xml']),
    IdInfo('JAR', 'Java Archive', ['META-INF/MANIFEST.MF']),
]

MIMETYPE_INFO = dict()
def add_mimetype(name, description, mimetype):
    MIMETYPE_INFO[mimetype] = MimetypeInfo(name, description, mimetype)

add_mimetype('ODT', 'Open Document Text', b'application/vnd.oasis.opendocument.text')
add_mimetype('ODS', 'Open Document Spreadsheet', b'application/vnd.oasis.opendocument.spreadsheet')
add_mimetype('ODP', 'Open Document Presentation', b'application/vnd.oasis.opendocument.presentation')

############
# Resolver #
############

def read4U(stream):
    b = stream.read(4)
    return unpack('<I', b)[0]

def read2U(stream):
    b = stream.read(2)
    return unpack('<H', b)[0]

def stream_iterator(stream):
    """
    Creates an iterator that iterates over a stream one byte at a time.
    It also does buffering.
    """
    buff = stream.read(BUFFER_SIZE)
    buff_pos = 0
    while True:
        if buff_pos >= len(buff):
            buff = stream.read(BUFFER_SIZE)
            buff_pos = 0
        b = buff[buff_pos]
        buff_pos += 1
        yield b


class ZipResolver:
    def __init__(self, maximum=512 * MEGABYTE):
        self.maximum = maximum

    def find_pattern(self, stream, pattern, end):
        """
        Going byte-by-byte, try to find a pattern in the stream.
        Ends if we read the given end position in the stream.
        """
        pos = stream.tell()
        pat_pos = 0
        b = None
        s_iter = stream_iterator(stream)
        while pos < end and b != b'':
            b = next(s_iter)
            pos += 1
            if pattern[pat_pos] == b:
                pat_pos += 1
                if pat_pos == len(pattern):
                    return pos - len(pattern)
            else:
                pat_pos = 0
        return None

    def verify_eocd(self, stream, origin, eocd_pos):
        """
        Assuming you're currently at the start of the EOCD, verify that the EOCD isn't just
        randomly compressed data.
        :param origin: presumed start of the zip file
        """
        stream.seek(eocd_pos + 16)
        cd_offset = read4U(stream)
        stream.seek(origin + cd_offset)
        header = stream.read(4)
        return header == CDFH_MAGIC

    def find_zip_end(self, stream):
        # Determine the origin of the zip file and what our max value is before we give up
        origin = stream.tell()
        # Seek to the end of the stream so we can determine the 
        stream.seek(0, 2)
        max_size = min(origin + self.maximum, stream.tell())
        # Start back at the beginning of the zip file
        stream.seek(origin)
        # End of Central Directory position
        eocd_pos = 0
        verified = False
        # We need to find the End of Central Directory record
        while eocd_pos < max_size and not verified:
            # Find the eocd position
            eocd_pos = self.find_pattern(stream, EOCD_MAGIC, max_size)
            # Check to make sure we got a valid eocd_pos
            if not eocd_pos:
                break
            stream.seek(eocd_pos)
            # Verify it's not just compressed data
            if self.verify_eocd(stream, origin, eocd_pos):
                verified = True
            else:
                # Skip our failed eocd so we can find a new one
                stream.seek(eocd_pos + 4)
        # If we successfully verified, then return the position, otherwise return None
        if verified:
            stream.seek(eocd_pos + 20)
            comment_length = read2U(stream)
            return eocd_pos + 22 + comment_length
        else:
            return None

    def identify(self, stream):
        try:
            origin = stream.tell()
            # Well first we have to determine the length of the zip file
            zip_end = self.find_zip_end(stream)
            # If we can't find the end of the zip file, give up
            if not zip_end:
                return
            # Build a "view" intro the stream to trick the ZipFile into thinking it's working with a file stream
            stream.seek(origin)
            stream_view = ioview.ReadView(stream, origin, zip_end)
            # We actually know the length of the zip file for this!
            zip_length = zip_end - origin
            # Now that we have the info about the zip file in memory, we can 

            with zipfile.ZipFile(stream_view, mode='r') as archive:
                filename_set = set([info.filename for info in archive.infolist()])
                
                # If we have a mimetype file, identify it via that
                if MIMETYPE_FILE in filename_set:
                    with archive.open(MIMETYPE_FILE, 'r') as zf:
                        mtype_id = zf.readline()
                        mtype = MIMETYPE_INFO.get(mtype_id)
                        if mtype:
                            return Result(mtype.name, description=mtype.description, length=zip_length)

                # Identify the file type via the Zip contents
                for id_data in ZIP_CONTENT_INFO:
                    if len(id_data.file_set & filename_set) == len(id_data.file_set):
                        return Result(id_data.name, description=id_data.description, length=zip_length)

                # If we couldn't identify it as a special ZIP file, assume it's a normal zip
                return Result('ZIP', 'Zip archive', length=zip_length)
        except zipfile.BadZipFile as e:
            print('Zip {:06x} {:06x} {:d}'.format(origin, zip_end, zip_end - origin))
            print(e)

def load(hound):
    hound.add_matches(ZIP_PATTERNS, ZipResolver())


