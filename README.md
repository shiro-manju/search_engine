# search_engine
![EOS_image](https://github.com/shiro-manju/search_engine/blob/main/info/SEO.jpg)

Elasticsearchを用いた意味類似検索エンジン

- python ver情報の記載
- pipの記載
- modelのDL

## elasticsearchの環境構築

### JDKインストール

```
# Linux

# MacOS
brew install homebrew/cask-versions/java8 --cask
```

### elasticsearch 7.17.4 インストール

```
# Linux
$ cd install_pkg
$ wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.8.0-linux-x86_64.tar.gz
$ tar xvf elasticsearch-7.5.0-linux-x86_64.tar.gz
 

# MacOS
$ brew tap elastic/tap
$ brew install elastic/tap/elasticsearch-full
$ brew install kibana


$ cp /usr/local/etc/elasticsearch/elasticsearch.yml .
$ cp /usr/local/etc/elasticsearch/jvm.options .
$ cp /usr/local/etc/elasticsearch/log4j2.properties .

```

### elasticsearch の日本語用tokenizerを使用

```
elasticsearch --version
elasticsearch-plugin install analysis-kuromoji
elasticsearch-plugin list
```

### pre-train modelのインストール

```
# xlnet
https://huggingface.co/hajime9652/xlnet-japanese

# Sntence Bert
https://huggingface.co/sonoisa/sentence-bert-base-ja-mean-tokens-v2
```

# コンペティションの内容

## EmbeddingModelの定義

- Input: 分かち書きされたテキスト ex) "日本 で は 呪術廻戦 、 全米 で は 鬼滅の刃 が 人気 だ "
- Output: torch.size([token_num, feature_dimension])
  - token_num:対象のテキストのtoken数
  - feature_dimension: modelの特徴量の次元数

- 参考: [elasticsearchインストール](https://qiita.com/Hitoshi5858/items/02a8e231cb346e5efbf9)
- 実装参考: [bert+elasticserach](https://qiita.com/shiraitsukasa/items/53dbf792696c69a77d96)
