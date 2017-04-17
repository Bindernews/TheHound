from identifier import Result
	
AU_PATTERNS = [
	'2E 72 6E 64',
	
]

AIFF_PATTERNS = [
	'46 4F 52 4D 00'
]
	
class AuResolver:
	def identify(self, stream):
		return Result('AU')

class AiffResolver:
	def identify(self, stream):
		return Result('AIFF')
	
def load(hound):
	hound.add_matches(AU_PATTERNS, AuResolver())
	hound.add_matches(AIFF_PATTERNS, AiffResolver())
