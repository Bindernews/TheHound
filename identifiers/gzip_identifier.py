from identifier import Result
	
GZ_PATTERNS = [
	'1F 8B 08 08'
]
	
class GzResolver:
	def identify(self, stream):
		return Result('GZ')
	
def load(hound):
	hound.add_matches(GZ_PATTERNS, GzResolver())
