from identifier import Result
	
ELF_PATTERNS = [
	'7F 45 4C 46'
]
	
class ElfResolver:
	def identify(self, stream):
		return Result('ELF')
	
def load(hound):
	hound.add_matches(ELF_PATTERNS, ElfResolver())
