
# Identifier for Java CLASS files.
import io
import identifier

CLASS_PATTERN = 'CA FE BA BE'

VERSION_LOOKUP = {
    0x30 = 'JDK 1.4',
    0x31 = 'Java SE 5.0',
    0x32 = 'Java SE 6.0',
    0x33 = 'Java SE 7',
    0x34 = 'Java SE 8',
    0x35 = 'Java SE 9',
}

class JavaClassIdentifier:
    def identify(self, stream):
        stream.seek(7, io.SEEK_CUR)
        version_name = VERSION_LOOKUP[stream.read(1)]
        return identifier.Result(version_name)

def load(hound):
    hound.add_match(CLASS_PATTERN, JavaClassIdentifier())

