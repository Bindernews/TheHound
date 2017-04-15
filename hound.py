
import io
import os
import sys

import matchlib

def eprint(*args, **kwargs):
    """
    Print to stderr instead of stdout.
    """
    print(*args, file=sys.stderr, **kwargs)


class Hound:
    """
    Hound is the main state holder. All modules receive a Hound instance to which they register
    information.
    """
    def __init__(self, block_size=512):
        self._matcher = matchlib.PatternMatcher()
        self.block_size = block_size
        pass

    def add_match(self, match, resolver):
        if match is str:
            self._matcher.add_match(bytearray.fromhex(match), resolver)
        else:
            self._matcher.add_match(match, resolver)

    def add_matches(self, match_array, resolver):
        for match in match_array:
            self.add_match(match, resolver)

    def process(self, stream):
        search = HoundSearch(self, stream, self.block_size)
        search.search()
        return search.results()

    def load_identifiers(self, module_path):
        """
        Load all python modules in the given module path.
        """

        # Here's where we'll store all of our loaded modules
        results = dict()
        # Locally scoped function that updates results and handles error printing
        def loadmod(modname):
            try:
                modvalue = __import__(module_path + '.' + modname, fromlist=['*'])
                # Allow the module to load itself
                modvalue.load(self)
                # If that doesn't fail, then add it to our list of loaded modules
                results[modname] = modvalue
            except AttributeError:
                # If load() failed, then print that we couldn't load the module
                eprint('Failed to load module:', modname)

        # Now we actually process through the possible modules
        directory = os.path.join(os.path.dirname(__file__), module_path)
        file_list = os.listdir(directory)
        for fn in file_list:
            # Compute the path name
            path = os.path.join(directory, fn)
            if path.endswith('.py'):
                loadmod(fn[:-3])
            # This tests if it's a module in a directory
            elif os.path.isdir(path) and os.path.exists(os.path.join(path, '__init__.py')):
                loadmod(fn)
        # Once we're done, return the dict of loaded modules
        return results


class HoundMatch:
    def __init__(self, search, start, matcher):
        self.search = search
        self.start = start
        self.end = end
        self.matcher = matcher

class HoundSearch:
    """
    When you want to search a specific stream of data you call hound.process(stream).
    Hound creates a HoundSearch object which holds relevant information.
    """
    def __init__(self, hound, stream, block_size):
        self.hound = hound
        self.stream = stream
        self.block_size = block_size

    def search(self):
        results = []
        read_size = min(self.block_size, self.hound._matcher.depth)
        while True:
            # Read data from the stream then reset to the beginning of the block
            data = self.stream.read(read_size)
            self.stream.seek(-read_size, io.SEEK_CUR)
            # Perform match on our Hound's matcher
            matcher_list = self.hound._matcher.match(data)
            self._process_matches(matcher_list)

    def _process_matches(self, matcher_list):
        results = []
        # Loop through all possible matchers
        known_position = self.stream.tell()
        for possible_match in matches:
            for matcher in possible_match.matches:
                # Reset stream before giving it to the identifier
                self.stream.seek(known_position)
                matcher_result = matcher.identify(self.stream)
                # If we got successful results, append our results as a match
                if matcher_result:
                    results.append(HoundMatch(self, known_position, matcher_result))
        return results

def main():
    hound = Hound()
    hound.load_identifiers('identifiers')

# Our "main method"
if __name__ == '__main__':
    main()

