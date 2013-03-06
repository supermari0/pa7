# coding: utf-8
import re
import sys
import codecs
import string

class Translator:

    def __init__(self):
        self.spanishEnglish = {}
        self.englishSpanish = {}

    def read_data(self, fileName):
        f = codecs.open(fileName, encoding='utf-8')
        for line in f:
            m = re.match('(?P<englishWord>[^:]+): (?P<spanishWord>.+)$', line)
            self.spanishEnglish[m.group('spanishWord').encode('utf-8')] = m.group('englishWord')

    def translate(self, fileName):
        f = codecs.open(fileName, encoding='utf-8')
        print string.punctuation
        for line in f:
            tokens = line.split()
            for token in tokens:
                strippedToken = re.match(ur'([A-Za-záéíóúñ]+)', token, re.UNICODE)
                if strippedToken is not None:
                  strippedToken = strippedToken.group(0).lower()
                  print strippedToken



def main(args):
    translator = Translator()
    translator.read_data('./dictionary')
    translator.translate('./spanishText')

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
