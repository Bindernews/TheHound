from identifier import Result
	
AU_PATTERNS = [
	'2E 72 6E 64'
]
	
class AuResolver:
	def identify(self, stream):
		return Result('AU')
	
def load(hound):
	hound.add_matches(AU_PATTERNS, AuResolver())
