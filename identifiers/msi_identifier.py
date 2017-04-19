from identifier import Result
	
MSI_PATTERNS = [
	'D0 CF 11 E0'
]
	
class MsiResolver:
	def identify(self, stream):
		return Result('MSI')
	
def load(hound):
	hound.add_matches(MSI_PATTERNS, MsiResolver())
