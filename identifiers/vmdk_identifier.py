from identifier import Result
	
VMDK_PATTERNS = [
	'23 20 44 69 73 6B 20 44 65 73 63 72 69 70 74 6F'
]
	
class VmdkResolver:
	def identify(self, stream):
		return Result('VMDK')
	
def load(hound):
	hound.add_matches(VMDK_PATTERNS, VmdkResolver())
