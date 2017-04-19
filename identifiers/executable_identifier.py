from identifier import *

EXE_PATTERNS = [
  '4D 5A 50 00',
  '4D 5A 90 00',
]

BIN_PATTERNS = [
    '7F 45 4C 46'
]

MSI_PATTERNS = [
    'D0 CF 11 E0'
]

class BinResolver:
    def identify(self, stream):
        return Result('BIN', 'Linux executable')
    
class ExeResolver:
    def identify(self, stream):
        return Result('EXE', 'Windows Executable')

class MsiResolver:
    def identify(self, stream):
        return Result('MSI', 'Microsoft Installer')


def load(hound):
    hound.add_matches(EXE_PATTERNS, ExeResolver())
    hound.add_matches(BIN_PATTERNS, BinResolver())
    hound.add_matches(MSI_PATTERNS, MsiResolver())
