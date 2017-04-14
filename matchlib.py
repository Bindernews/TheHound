import string

# The wildchar "byte" that matches any byte.
C_FSLASH = ord('/')
C_QUESTION = ord('?')
C_WILDCHAR = 0xff00

MATCH_ESCAPE_LOOKUP = {
    C_FSLASH: C_FSLASH,
    C_QUESTION: C_WILDCHAR,
}

class SearchStruct:
    def __init__(self, parent, byte):
        self.parent = parent
        self.byte = byte
        self.children = dict()
        self.matches = set()
        self._pattern = None  # Cache for the pattern. It's only calculated on demand

        # Add child to parent in constructor
        if parent and byte:
            parent.children[byte] = self

    def find(self, byte):
        """
        Returns a list containing "child" objects which match the given byte.
        Currently the list may contain 0 - 2 objects.
        """
        results = []
        if byte in self.children:
            results.append(self.children[byte])
        if C_WILDCHAR in self.children:
            results.append(self.children[C_WILDCHAR])
        return results

    def calc_wildchar_parents(self):
        """
        Return the number of parents (including this SearchStruct) with a C_WILDCHAR byte.
        """
        cur_struct = self
        count = 0
        while cur_struct:
            if cur_struct.byte == C_WILDCHAR:
                count += 1
            cur_struct = cur_struct.parent
        return count

    def get_pattern(self):
        """
        Build a pattern string which would match this SearchStruct.
        Note that this string is in ASCII and does not account for UTF-8.
        """
        if not self._pattern:
            s = ''
            cur_struct = self._sstruct
            while cur_struct:
                b = cur_struct.byte
                if chr(b) in string.printable:
                    s = chr(b) + s
                else:
                    s = '\\x{:02x}'.format(b) + s
                cur_struct = cur_struct.parent
            self._pattern = s
        return self._pattern


def match_byte_iter(match):
    """
    Iterate through a bytearray and yield sucessive "bytes". Accounts for wildchars.
    """
    idx = 0
    length = len(match)
    while idx < length:
        if match[idx] == C_FSLASH:
            bnext = MATCH_ESCAPE_LOOKUP.get(match[idx + 1])
            if bnext:
                yield bnext
                idx += 2
            else:
                raise ValueError
        else:
            yield match[idx]
            idx += 1


class MatchResult:
    def __init__(self, sstruct, confidence):
        self._sstruct = sstruct
        self._pattern = None
        self.results = sstruct.matches
        self.confidence = confidence

    def __str__(self):
        # Format is "pattern confidence [result1, result2, resultN]"
        # ex: "\xCA\xFE\xBA\xBE 0.750 [.class]"
        s = self._sstruct.get_pattern() + ' {:.3f} ['.format(self.confidence)
        for match in self.results:
            if hasattr(match, 'name'):
                s += match.name
            else:
                s += str(match)
            s += ', '
        s = s[:-2] + ']'
        return s


class PatternMatcher:
    def __init__(self):
        self.root = SearchStruct(None, None)
        self.depth = 0

    def add_match(self, match, result):
        """
        Add a file header match to the matcher.
        :param match: a byte array specifying the file match
        """
        cur_struct = self.root
        depth = 0
        # Recurse through the match tree until we hit the leaf
        for mbyte in match_byte_iter(match):
            if mbyte in cur_struct.children:
                cur_struct = cur_struct.children[mbyte]
            else:
                cur_struct = SearchStruct(cur_struct, mbyte)
            depth += 1
        # Add our result to the leaf
        cur_struct.matches.add(result)
        self.depth = max(self.depth, depth)

    def match(self, match):
        """
        Returns a list of MatchResult objects with the properties 'result' containing the relevant
        result object and 'confidence' which is a measure of the confidence of the result.
        The list is sorted by confidence (most confident first).
        """
        results = []
        length = min(self.depth, len(match))

        def add_result(sstruct, i):
            confidence = (i - (0.5 * sstruct.calc_wildchar_parents())) / length
            results.append( MatchResult(sstruct, confidence) )

        cur_structs = [self.root]
        for i in range(length):
            mbyte = match[i]
            # This will hold new structs at the next level
            new_structs = []
            for sstruct in cur_structs:
                # Find all possible children in the tree
                children = sstruct.find(mbyte)
                # If there are no children, this is a leaf match, so add to results
                if len(children) == 0:
                    add_result(sstruct, i)
                else:
                    new_structs.extend(children)
            # If we've reached the end the tree, stop
            if len(new_structs) == 0:
                break
            cur_structs = new_structs


        # Now each SearchStruct remaining is a leaf node. Confidence for these will be high.
        for sstruct in cur_structs:
            add_result(sstruct, len(match))

        # Sort by confidence
        results.sort(key=lambda m: m.confidence)

        return results


