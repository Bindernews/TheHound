from identifier import Result
	
MIDI_PATTERNS = [
	'4D 54 68 64'
]
	
class MidiResolver:
	def identify(self, stream):
		return Result('MIDI')
	
def load(hound):
	hound.add_matches(MIDI_PATTERNS, MidiResolver())
