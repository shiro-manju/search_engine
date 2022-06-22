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
import cv2
import tempfile
import os

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

def get_image(url, news_id):
    # 画像をリクエストする
    res = requests.get(url)
    img = None
    # Tempfileを作成して即読み込む
    fp = tempfile.NamedTemporaryFile(dir='./', delete=False)
    fp.write(res.content)
    fp.close()
    img = cv2.imread(fp.name)
    os.remove(fp.name)
    save_path = f'MakeDataset/ScrapingData/png_data/{news_id}.png'
    cv2.imwrite(save_path, img)
    return save_path
    

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

    news_id_list = []
    img_path_list = []
    page_url_list = []
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
            news_id = link.split("/")[-1]
            img_url = href_soup.find("source", type="image/jpeg")["srcset"]
            
            # img_path = get_image(url=img_url, news_id=news_id)
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

        news_id_list.append(news_id)
        img_path_list.append(img_url)
        page_url_list.append(link)
        text_list.append(text)
        title_list.append(title)
        category_list.append(category)

        if i >= n:
            print("取得記事の設定上限に達したため、処理を中断")
            break

    df = pd.DataFrame({'news_id': news_id_list, 'title': title_list, 'category': category_list, 'article': text_list, 'img_url': img_path_list, 'page_url': page_url_list})
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