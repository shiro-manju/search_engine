from sudachipy import tokenizer 
from sudachipy import dictionary
import MeCab
import os

class MecabTokenizer():
    def __init__(self, path=False):
        if not path:
            path = os.path.abspath('SearchEngine/tokenizer/dic/ipadic')
        self.tagger = MeCab.Tagger (f'-Owakati -d {path}')
    
    def tokenizer(self, text):
        return self.tagger.parse(text)

class  SudachiTokenizer():
    def __init__(self):
        self.tokenizer_obj = dictionary.Dictionary().create()
        self.mode = tokenizer.Tokenizer.SplitMode.C

    def tokenizer(self, text):
        return " ".join([m.surface() for m in self.tokenizer_obj.tokenize(text, self.mode)])


if __name__==('__main__'):
    text = "日本では呪術廻戦、全米では鬼滅の刃が人気だ"
    Tokenizer = MecabTokenizer()
    print(Tokenizer.tokenizer(text))

    TokenizerNeologd = MecabTokenizer(path="/usr/local/lib/mecab/dic/mecab-ipadic-neologd")
    print(TokenizerNeologd.tokenizer(text))

    TokenizerSudachi = SudachiTokenizer()
    print(TokenizerSudachi.tokenizer(text))