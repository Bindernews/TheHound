from identifier import Result
	
CAB_PATTERNS = [
	'4D 53 43 46'
]
	
class CabResolver:
	def identify(self, stream):
		return Result('CAB')
	
def load(hound):
	hound.add_matches(CAB_PATTERNS, CabResolver())
