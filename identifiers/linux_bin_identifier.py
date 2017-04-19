from identifier import Result
	
BIN_PATTERNS = [
	'7F 45 4C 46'
]
	
class BinResolver:
	def identify(self, stream):
		return Result('BIN')
	
def load(hound):
	hound.add_matches(BIN_PATTERNS, BinResolver())
