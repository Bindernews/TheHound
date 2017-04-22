from identifier import Result
	
PST_PATTERNS = [
	'21 42 44 4E'
]
	
class PstResolver:
	def identify(self, stream):
		return Result('PST')
	
def load(hound):
	hound.add_matches(PST_PATTERNS, PstResolver())
