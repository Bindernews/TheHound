from identifier import Result

MP3_DESC = 'MP3 Audio'

AU_PATTERNS = [
    '2E 72 6E 64',
]

MP3_PATTERNS = set([
    bytes.fromhex('FF FB'),
    bytes.fromhex('FF FA'),
])

AIFF_PATTERNS = [
    '46 4F 52 4D 00'
]

class BadMp3Error(BaseException):
    def __init__(*args, **kwargs):
        super().__init__(*args, **kwargs)

class Mp3Resolver:
    def read_frame(self, stream):
        header = stream.read(4)
        if not header[0:2] in MP3_PATTERNS:
            return False
        has_crc = (header[1] & 8) == 0
        bitrate_index = header[2] & 0x0F

    def identify(self, stream):
        return Result('MP3', MP3_DESC)
        # if not self.read_frame(stream):
        #     return Result('MP3', MP3_DESC)
    
class AuResolver:
    def identify(self, stream):
        return Result('AU')

class AiffResolver:
    def identify(self, stream):
        return Result('AIFF')
    
def load(hound):
    hound.add_matches(AU_PATTERNS, AuResolver())
    hound.add_matches(AIFF_PATTERNS, AiffResolver())
