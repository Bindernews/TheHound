from identifier import *
import collections 
 
CFBInfo = collections.namedtuple('CFBInfo', ['name', 'descripion', 'pattern']) 

OFFICE_PATTERNS = [
    'D0 CF 11 E0 A1 B1 1A E1'
]

FILE_PATTERNS = [
    CFBInfo('DOC', 'Microsoft Word 97-2003', bytes.fromhex('EC A5 C1 20')),
    CFBInfo('XLS', 'Microsoft Excel 97-2003', bytes.fromhex('09 08 10 20 20 06 05 20 A6 45 CD 07')),
]

class CfbResolver:
    def identify(self, stream):
        data = stream.read(128)
        for filepat in FILE_PATTERNS:
            index = data.find(filepat.pattern)
            if index != -1:
                return Result(filepat.name, filepat.description)
        return Result('CFB') 

def load(hound):
    hound.add_matches(OFFICE_PATTERNS, CfbResolver())

