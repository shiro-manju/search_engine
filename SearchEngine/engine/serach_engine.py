from elasticsearch7 import Elasticsearch
import sys

class ElasticSearchEngine:
    def __init__(self):
        self.es = Elasticsearch("http://localhost:9200")
    
    
    def search_documents(self, query, topn, index_name, tokenizer, embdding_module):
        query_token = tokenizer.tokenizer(query)
        query_vector = embdding_module.embdding(query_token).tolist()
        print(len(query_vector))

        query_script = {
            "script_score": {
                "query": {
                    "match_all": {}
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'article_vector') + 1.0",
                "params": {"query_vector": query_vector}
                }
            }
        }
        
        response = self.es.search(
            index=index_name,
            body={
                "size": topn,
                "query": query_script,
                "_source": {"includes": ["news_id", "title", "category", "article", "img_url", "page_url"]}
            }
        )
        
        # response = self.es.search(index="test", query={"match_all": {}}, size=2)
        return response

if __name__==('__main__'):
    es_search = ElasticSearchEngine()