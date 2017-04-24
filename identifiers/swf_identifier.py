from identifier import Result
	
SWF_PATTERNS = [
	'46 57 53'
]
	
class SwfResolver:
	def identify(self, stream):
		return Result('SWF')
	
def load(hound):
	hound.add_matches(SWF_PATTERNS, SwfResolver())
