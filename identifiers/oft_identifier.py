from identifier import Result
	
OFT_PATTERNS = [
	'4F 46 54 32'
]
	
class OftResolver:
	def identify(self, stream):
		return Result('OFT')
	
def load(hound):
	hound.add_matches(OFT_PATTERNS, OftResolver())
