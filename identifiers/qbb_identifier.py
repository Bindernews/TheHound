# Sniff for Quickbooks Backups
from identifier import Result
	
QBB_PATTERNS = [
	'45 86 00 00 06 00'
]
	
class QbbResolver:
	def identify(self, stream):
		return Result('QBB')
	
def load(hound):
	hound.add_matches(QBB_PATTERNS, QbbResolver())
