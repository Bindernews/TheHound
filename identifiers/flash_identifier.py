from identifier import Result
	
FLV_PATTERNS = [
	'46 4C 5C 01'
]
	
class FlvResolver:
	def identify(self, stream):
		return Result('FLV')
	
def load(hound):
	hound.add_matches(FLV_PATTERNS, FlvResolver())
