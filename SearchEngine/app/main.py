import os, sys
import argparse

# モジュール検索パスの追加
module_paths = [
    os.path.join(os.path.dirname(__file__), "tokenizer"),
]
for module_path in module_paths:
    if module_path not in sys.path: sys.path.append(module_path)

 
from utils.data_loader import DataLoader   
from tokenizer.tokenizer import MecabTokenizer
from models.xlnet.xlnet import XLNet
from engine.create_index_engine import CreateIndex
from engine.serach_engine import ElasticSearchEngine

from config import cfg


def main(args):
    index_name = args.index_name
    tokenizer = MecabTokenizer(path=args.dict_path)
    xlnet = XLNet()

    if args.engine_type == "create_index":
        data_loader = DataLoader(data_folder_path=args.dataset_path)
        create_index = CreateIndex()
        input_df = data_loader.load_dataset()
        create_index.create_index(input_df, index_name=index_name, tokenizer=tokenizer, embdding_module=xlnet)
    
    elif args.engine_type == "search_engine":
        test_query = "日本の政治で、日本国民の反応がよかった記事"
        es_search = ElasticSearchEngine()
        response = es_search.search_documents(query=test_query, topn=args.topn, index_name=index_name, tokenizer=tokenizer, embdding_module=xlnet)
        [print(res["_source"]["title"]) for res in response["hits"]["hits"]]
    

if __name__==('__main__'):
    parser = argparse.ArgumentParser()

    parser.add_argument('--dict_path', help='Path to tokenizer dictionary', type=str, default=cfg.CONF.MECAB_DICT_PATH)
    parser.add_argument('--dataset_path', help='Path to Dataset', type=str, default=cfg.CONF.DATASET_PATH)
    parser.add_argument('--engine_type', help='Select engine-type, "create_index" or "search_engine"', type=str, default=cfg.CONF.ENGINE_TYPE)
    parser.add_argument('--index_name', help='Input ElasticSearch Index', type=str, default="test")
    parser.add_argument('--topn', help='Number of Getting resopnses', type=str, default=cfg.SEARCH.TOPN)
   
    args = parser.parse_args() 
    main(args)