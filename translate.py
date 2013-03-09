# coding: utf-8
import re
import sys
import codecs
from stanford import StanfordTagger
from collections import namedtuple


class Translator:

    def __init__(self):
        self.spanishEnglish = {}
        self.englishSpanish = {}
        self.text = []
        self.WordTag = namedtuple('WordTag', 'word tag')
        self.tagger = StanfordTagger('./postag/models/english-bidirectional-distsim.tagger',
                                     './postag/stanford-postagger-3.1.4.jar')
        self.patterns = [(["NN", "RB", "VBD"], ["NN", "VBD", "RB"]),    # Adverbs at end
                         (["VBD", "DT", "NNS"], ["DT", "NNS", "VBD"]),  # Subject before verb
                         (["VBN", "DT", "NN"], ["DT", "NN", "VBN"]),    # Subject before verb
                         # Prep. after possesive
                         # of close his beauty -> his beauty of close
                         (["IN", "JJ", "PRP\$", "NN"], ["PRP\$", "NN", "IN", "JJ"]),
                         # Prep before noun
                         # water sweet -> water salt
                         (["NN", "JJ"], ["JJ", "NN"]),
                         (["VBN", "PRP"], ["PRP", "VBN"]),
                         (["DT", "PRP", "VB*"], ["PRP", "VB*", "DT"])]
        self.replacements = [("all the days", "always"), ("him same", "himself")]

    def read_data(self, fileName):
        f = codecs.open(fileName, encoding='utf-8')
        for line in f:
            m = re.match('(?P<englishWord>[^:]+): (?P<spanishWord>.+)$', line)
            self.spanishEnglish[m.group('spanishWord').encode('utf-8')] = m.group('englishWord')

    def tokenTranslate(self, fileName):
        f = codecs.open(fileName, encoding='utf-8')
        for line in f:
            tokens = line.split()
            for token in tokens:
                match = re.match(u'\W*(?P<word>\w+)(?P<punctuation>\W*)', token, re.UNICODE)
                if match:
                    strippedToken = match.group('word').lower()
                    if strippedToken.encode('utf-8') in self.spanishEnglish:
                        yield self.spanishEnglish[strippedToken.encode('utf-8')]
                    if match.group('punctuation'):
                        yield match.group('punctuation')
                else:
                    yield token

    def patternsMatch(self, text, pattern):
        """
        Check if the tags in text match the tags in pattern.
        text is a list of WordTag tuples (word, tag)
        pattern is a list of patterns.
        patternsMatch([WordTag("a", "NN"), WordTag("b", "VB")], ["NN", "VB"]) -> True
        patternsMatch([WordTag("a", "NN"), WordTag("b", "VB")], ["NN", "V*"]) -> True
        patternsMatch([WordTag("a", "NN"), WordTag("b", "VB")], ["NN", "PP"]) -> False
        """
        return all([re.match(pair[1], pair[0].tag) for pair in zip(text, pattern)])

    def reorderPatterns(self, pattern, sub, text):
        """
        Look for pattern in text and reorder according to the rules in sub.
        pattern is a list of strings (eg. ["VB", "NN", "IT])
        sub is a way to reorder (permutation of) pattern (eg. ["IT", "NN", "VB])
        text is a list of (word, tag) that should be reordered.
        For instance, reorderPatterns(["VB", "NN"], ["NN", "VB"], ["IT", "VB", "NN"])
        changes text to ["IT", "NN", "VB"]
        """
        patternLen = len(pattern)
        for i, wordTag in enumerate(text[:-patternLen]):
            if wordTag.tag == pattern[0] and self.patternsMatch(text[i:i + patternLen], pattern):
                # Create a pattern -> wordTag in text mapping
                mapping = {pattern[j]: text[i + j] for j in range(patternLen)}
                # Replace the existing sub-list with the reordered list
                text[i:i + patternLen] = [mapping[p] for p in sub]

    def translate(self, fileName):
        self.text = [word for word in self.tokenTranslate(fileName)]
        self.tagged = self.tagger.tag(self.text)
        # Convert to named tuples so we can access w.word, w.tag
        self.tagged = [self.WordTag(w[0], w[1]) for w in self.tagged]

        for pattern in self.patterns:
            self.reorderPatterns(pattern[0], pattern[1], self.tagged)
            # if tag == 'NNS' and self.tagged[index - 1][1] == 'DT':
            #     print word
        print self.tagged


def main(args):
    translator = Translator()
    translator.read_data('./dictionary')
    translator.translate('./spanishText')

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
