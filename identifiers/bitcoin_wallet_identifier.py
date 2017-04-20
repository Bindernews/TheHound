from identifier import Result
	
WALLET_PATTERNS = [
	'0A 16 6F 72 67 2E 62 69 74 63 6F 69 6E 2E 70 72'
]
	
class WalletResolver:
	def identify(self, stream):
		return Result('WALLET')
	
def load(hound):
	hound.add_matches(WALLET_PATTERNS, WalletResolver())
