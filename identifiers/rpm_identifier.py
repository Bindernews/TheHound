from identifier import Result

RPM_PATTERNS = [
	'ED AB EE DB'
]
	
class RpmResolver:
	def identify(self, stream):
		return Result('RPM')
	
def load(hound):
	hound.add_matches(RPM_PATTERNS, RpmResolver())
