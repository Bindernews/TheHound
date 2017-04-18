
import argparse
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
        if not isinstance(match, bytearray):
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
    def __init__(self, search, start, confidence, result):
        self.search = search
        self.start = start
        self.confidence = confidence
        self.result = result
        # Copy values from result
        self.name = result.name
        self.description = result.description
        self.length = result.length
        self.data = result.data

    def __str__(self):
        s = self.name + ' 0x{:04x} c={:.2f}'.format(self.start, self.confidence)
        if self.description:
            s += ' ' + self.description
        if self.data:
            s += ' ' + str(self.data)
        return s

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
            # Make sure we're not at the end of the stream
            if len(data) == 0:
                break
            self.stream.seek(-read_size, io.SEEK_CUR)
            # Perform match on our Hound's matcher
            matcher_list = self.hound._matcher.match(data)
            # Add the data to our list of results
            results += self._process_matches(matcher_list)
            # Jump to the next block
            self.stream.seek(self.block_size, io.SEEK_CUR)
        return results

    def _process_matches(self, matcher_list):
        results = []
        # Loop through all possible matchers
        known_position = self.stream.tell()
        for possible_match in matcher_list:
            for matcher in possible_match.matches:
                # Reset stream before giving it to the identifier
                self.stream.seek(known_position)
                matcher_result = matcher.identify(self.stream)
                # If we got successful results, append our results as a match
                if matcher_result:
                    results.append(HoundMatch(self, known_position, possible_match.confidence, matcher_result))
        return results


def build_argparser():
    parser = argparse.ArgumentParser(description='Search a dd file for files of various types')
    parser.add_argument('file', type=argparse.FileType('rb'), help='dd file for the Hound to scan')
    parser.add_argument('--block-size', type=int, default=512, help='Hound will search for a file at each multiple of block-size in the dd file')
    return parser

def main():
    parser = build_argparser()
    args = parser.parse_args()

    hound = Hound()
    hound.load_identifiers('identifiers')

    print('Processing file...')
    results = HoundSearch(hound, args.file, args.block_size).search()
    print('Results...')
    for res in results:
        print(res)

# Our "main method"
if __name__ == '__main__':
    main()

