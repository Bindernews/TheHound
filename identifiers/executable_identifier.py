from identifier import

EXE_PATTERNS = [
  '4D 5A 50 00',
  '4D 5A 90 00',
]

class ExeResolver
  def identify(self, stream):
    return Result('exe')

def load(hound):
  hound.add_matches(EXE_PATTERNS, ExeResolver())