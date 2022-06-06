import time
import datetime
import argparse
import re
import unicodedata
import math
import string
import requests
from bs4 import BeautifulSoup
import pandas as pd
from progressbar import progressbar



# 記号文字は分析をするにあたって邪魔になるため、記号を取り除く関数を定義します。
# 下のYahooNews関数で使用します。
def symbol_removal(soup):
    soup = unicodedata.normalize("NFKC", soup)
    exclusion = "「」『』【】《》≪≫、。・◇◆" + "\n" + "\r" + "\u3000" # 除去する記号文字を指定
    soup = soup.translate(str.maketrans("", "", string.punctuation  + exclusion))
    return soup

def get_requests(url):
    res = requests.get(url)
    time.sleep(0.1)
    return res

def html_parser(html_text, parser_type="html.parser"):
    soup = BeautifulSoup(html_text, parser_type)
    return soup

# Yahooニュースをスクレイピングする関数です。
# 引数で指定した数の記事をとってきてデータフレームを返します。
def YahooNews(n=30, page=2):
    url = "https://news.yahoo.co.jp/topics/top-picks"
    URL = "https://news.yahoo.co.jp/"
    res = get_requests(url)
    soup = html_parser(res.text, "html.parser")
    all_page_links = []
    all_page_links.append(url)
    all_links = []

    page_index = 0
    while True:
        try:
            if page_index >= page-1:
                break
            next = soup.find("li", class_="pagination_item-next").find("a")["href"]
            next_link = URL + next
            all_page_links.append(next_link)
            next_res = get_requests(next_link)
            soup = html_parser(next_res.text, "html.parser")
            page_index += 1
            
        except:
            break

    title_list = []
    category_list = []
    text_list = []
    for url in all_page_links: # all_page_links: 全てのニュースのリスト
            res = get_requests(url) # url: 25個分のニュースのリスト
            soup = html_parser(res.text, "html.parser")
            page_soup = soup.find_all("a", class_="newsFeed_item_link")
            for href in page_soup:
                link = href["href"] # link: 一つのニュースのリンク(本文は一部のみ)
                all_links.append(link)

    if len(all_links) <= n:
        n = len(all_links)

    i = 0
    for link in progressbar(all_links):
        link_res = get_requests(link)
        href_soup = html_parser(link_res.text, "html.parser")
        try:
            title = href_soup.find("h1", class_=re.compile("^sc")).string
            category = href_soup.find("li", class_="sc-ckVGcZ jTRJbz").string
            title_link = href_soup.find("a", class_="sc-kREsUy fOkZWA")["href"] # title_link: 本文
            res = get_requests(title_link)
            soup = html_parser(res.text, "html.parser")
            text = soup.find("p", class_="sc-iqzUVk LDceb yjSlinkDirectlink highLightSearchTarget").text
            text = symbol_removal(text)
        except:
            continue
        

        i += 1

        text_list.append(text)
        title_list.append(title)
        category_list.append(category)

        if i >= n:
            print("取得記事の設定上限に達したため、処理を中断")
            break

        '''
        try:
            category = category[1].string
        except:
            continue
        else:
            for tag in soup.find_all(["a"]):
                tag.decompose()
            try:
                soup = soup.find("div", class_="article_body").get_text()
                soup = symbol_removal(soup)

                text_list.append(soup)
                title_list.append(title)
                category_list.append(category)
                i += 1 # 本文が正常に保存できたことをトリガーにしてカウントを一つ増やすことにします。
                # 進捗バーを表示させます。
                pro_bar = ('=' * math.ceil(i / (n / 20))) + (' ' * int((n / (n / 20)) - math.ceil(i / (n / 20))))
                print('\r[{0}] {1}記事'.format(pro_bar, i), end='')
                if i >= n:
                    df = pd.DataFrame({'title': title_list, 'category': category_list, 'text': text_list})
                    return df
            except:
                continue
        '''
    df = pd.DataFrame({'title': title_list, 'category': category_list, 'text': text_list})
    return df

def main(args):
    df = YahooNews(n=args.num_articles, page=args.num_pages)
    today = datetime.datetime.now().strftime('%Y%m%d')
    df.to_csv(args.output_path+today+".csv", index=False)

if __name__ == ('__main__'):
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_articles', help='Number of getting articles', type=int, default=20)
    parser.add_argument('--num_pages', help='Number of search pages (25 articles / page)', type=int, default=1)
    parser.add_argument('--output_path', help='output directory', type=str, default="./ScrapingData/")
    args = parser.parse_args()
    main(args)