import csv
import os
import sys
from tqdm import tqdm
from elasticsearch7 import Elasticsearch, helpers
import yaml

class CreateIndex:
    def __init__(self):
        self.es = Elasticsearch("http://localhost:9200")
        self.es_config_path = 'SearchEngine/engine/elasticsearch/setting/elasticsearch.yml'
    
    def _deleate_index(self, index_name):
        self.es.indices.delete(index=index_name, ignore=[404])
    
    def _new_index(self, index_name):
        self.es.indices.create(index=index_name, body=self.setting)
        self.es.indices.flush()

    def _add_record(self, input_df, index_name, tokenizer, embdding_module):
        #input_df = input_df.head(5)
        attrs = input_df.columns.values
        data = {
            '_op_type': 'index',
            '_index': index_name,
        }

        for idx, (news_id, title, category, article, img_url, page_url) in tqdm(enumerate(
            zip(
                input_df["news_id"].values,
                input_df["title"].values,
                input_df["category"].values,
                input_df["article"].values,
                input_df["img_url"].values,
                input_df["page_url"].values
            )
        ), total=len(input_df)):

            for col_idx, value in enumerate([news_id, title, category, article, img_url, page_url]):
                if attrs[col_idx] in self.properties:
                    data[attrs[col_idx]] = value
                if attrs[col_idx] == 'article':
                    token_text = tokenizer.tokenizer(value)
                    vector = embdding_module.embdding(token_text)
                    data['article_vector'] = vector.tolist()
            yield data


    def create_index(self, input_df, index_name, tokenizer, embdding_module, new_index=True, deleate_index=True):
        if deleate_index:
            self._deleate_index(index_name)
        
        self.setting = yaml.load(open(self.es_config_path), Loader=yaml.SafeLoader)
        self.properties = self.setting['mappings']['properties']
        print(self.setting)

        if new_index:
            self._new_index(index_name)                    

        helpers.bulk(self.es, self._add_record(input_df, index_name, tokenizer, embdding_module), request_timeout=5000)
        self.es.close()
    
    def session_close(self):
        self.es.close()


if __name__==('__main__'):
    index_name = 'test'
    create_index = CreateIndex()
    create_index.setting = yaml.load(open(create_index.es_config_path), Loader=yaml.SafeLoader)
    create_index._deleate_index(index_name)
    create_index._new_index(index_name)

    create_index.session_close()
