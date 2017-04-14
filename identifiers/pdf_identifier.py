
from identifier import Result

PDF_PATTERNS = [
	'25 50 44 46'
]

class PdfResolver:
	def identify(self, stream):
		return Result('PDF')

def load(hound):
	hound.add_matches(PDF_PATTERNS, PdfResolver())
