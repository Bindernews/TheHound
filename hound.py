
import io
import os
import sys

import matchlib

class Hound:
    """
    Hound is the main state holder. All modules receive a Hound instance to which they register
    information.
    """
    def __init__(self, block_size=2048):
        self._matcher = matchlib.PatternMatcher()
        self.block_size = block_size
        pass

    def add_match(self, match, resolver):
        self._matcher.add_match(match, resolver)

    def process(self, stream):
        search = HoundSearch(self, stream, self.block_size)
        search.search()
        return search.results()

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



