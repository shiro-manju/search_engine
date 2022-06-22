from transformers import XLNetTokenizer, XLNetModel
import torch

class XLNet():
    def __init__(self):
        self.model_tokenizer = XLNetTokenizer.from_pretrained("SearchEngine/models/pretrain_model/xlnet-japanese")
        self.model = XLNetModel.from_pretrained("SearchEngine/models/pretrain_model/xlnet-japanese")
         
    def embdding(self, prompt: str):
        inputs = self.model_tokenizer(prompt, add_special_tokens=False, return_tensors="pt")
        outputs = self.model(**inputs)
        last_hidden_states = outputs.last_hidden_state
        return torch.norm(last_hidden_states[0], p=2, dim=0)

if __name__==('__main__'):
    import MeCab
    path = "/usr/local/lib/mecab/dic/mecab-ipadic-neologd"
    tokenizer = MeCab.Tagger(f"-Owakati -d {path}")
    prompt = "日本では呪術廻戦、全米では鬼滅の刃が人気だ"
    prompt = tokenizer.parse(prompt)
    xlnet = XLNet()
    vector = xlnet.embdding(prompt)
    print(vector.shape)