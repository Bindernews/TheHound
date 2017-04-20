from identifier import Result

PSD_PATTERNS = [
	'38 42 50 53'
]
	
class PsdResolver:
	def identify(self, stream):
		return Result('PSD')
	
def load(hound):
	hound.add_matches(PSD_PATTERNS, PsdResolver())
