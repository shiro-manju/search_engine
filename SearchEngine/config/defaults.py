from yacs.config import CfgNode as CN
_C = CN()


# -----------------------------------------------------------------------------
# config
# -----------------------------------------------------------------------------
_C.CONF = CN()
_C.CONF.DATASET_PATH = "./MakeDataset/ScrapingData/"
_C.CONF.MECAB_DICT_PATH = "/usr/local/lib/mecab/dic/mecab-ipadic-neologd"

_C.CONF.ENGINE_TYPE = "create_index" # or search_engine
#_C.CONF.ENGINE_TYPE = "search_engine"


# Use embedding model
_C.CONF.SELECT_MODEL = "xlnet"

# -----------------------------------------------------------------------------
# train model
# -----------------------------------------------------------------------------
_C.TRAIN = CN()
_C.TRAIN.XLNET = True


# -----------------------------------------------------------------------------
# search engine
# -----------------------------------------------------------------------------
_C.SEARCH = CN()
_C.SEARCH.INDEFX_NAME = "test"
_C.SEARCH.TOPN = 10
