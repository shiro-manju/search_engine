from transformers import BertJapaneseTokenizer, BertModel
import torch


class SentenceBertJapanese:
    def __init__(self, device=None):
        self.tokenizer = BertJapaneseTokenizer.from_pretrained("SearchEngine/models/pretrain_model/sentence-bert-base-ja-mean-tokens-v2")
        self.model = BertModel.from_pretrained("SearchEngine/models/pretrain_model/sentence-bert-base-ja-mean-tokens-v2")
        self.model.eval()

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        self.model.to(device)

        self.batch_size=8

    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


    def encode(self, sentences):
        all_embeddings = []
        sentences = [x for x in sentences.split("。") if len(x) > 3]
        iterator = range(0, len(sentences), self.batch_size)
        for batch_idx in iterator:
            batch = sentences[batch_idx:batch_idx + self.batch_size]

            encoded_input = self.tokenizer.batch_encode_plus(batch, padding="longest", 
                                           truncation=True, return_tensors="pt").to(self.device)
            model_output = self.model(**encoded_input)
            sentence_embeddings = self._mean_pooling(model_output, encoded_input["attention_mask"]).to('cpu')

            all_embeddings.extend(sentence_embeddings)

        return torch.norm(torch.stack(all_embeddings), p=2, dim=0)

if __name__==('__main__'):
    import MeCab
    path = "/usr/local/lib/mecab/dic/mecab-ipadic-neologd"
    tokenizer = MeCab.Tagger(f"-Owakati -d {path}")
    prompt = "日本では呪術廻戦、全米では鬼滅の刃が人気だ。私もこのアニメは大好きいです。"
    prompt = tokenizer.parse(prompt)

    sbert = SentenceBertJapanese()
    sentence_embedding = sbert.encode(prompt )
    print(sentence_embedding.shape)