import os
import sys
import json
from os.path import join, dirname
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), 'SearchEngine/'))
dotenv_path = join(dirname(__file__), 'news_bot/.env')
load_dotenv(dotenv_path)

import logging
import argparse
from slack_bolt import App, Ack, Say, BoltContext, Respond
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

from news_bot.views import build_modal_view, add_channel_info, button_block_view, make_say_template_view
from SearchEngine.engine_run import SearchEngine

# デバッグレベルのログを有効化
logging.basicConfig(level=logging.DEBUG)
# これから、この app に処理を設定していきます
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

def _get_news(query):
    return engine.search_news(query=query, topn=args.topn, index_name=args.index_name)
    #response = engine.search_news(query=query, topn=args.topn, index_name=args.index_name)
    #[print(res["_source"]["title"]) for res in response["hits"]["hits"]]

@app.message("hello")
def message_hello(message, say):
    # イベントがトリガーされたチャンネルへ say() でメッセージを送信します
    say(f"Hey there <@{message['user']}>!")

@app.view("search-id")
def handle_view_events(ack: Ack, view: dict, say: Say, logger: logging.Logger):

    inputs = view["state"]["values"]
    question = inputs.get("question-block", {}).get("input-element", {}).get("value")

    if len(question) < 3:
        ack(response_action="errors", errors={"question-block": "検索文は 3 文字以上で入力してください"})
        return

    # 正常パターン、実際のアプリではこのタイミングでデータを保存したりする
    # logger.info(f"Received question: {question}")
    

    channel_to_notify = json.loads(view.get("private_metadata", "{}")).get("channel_id")
    if channel_to_notify is None:
        channel_to_notify = (
            view["state"]["values"]
            .get("channel_to_notify")
            .get("_")
            .get("selected_conversation")
        )

    # そのチャンネルに対して chat.postMessage でメッセージを送信します
    response = _get_news(query=question)
    say(
        channel=channel_to_notify,
        attachments=make_say_template_view(response),
        text=f"query: {question}"
    )
    #say(channel=channel_to_notify, text=f"return {question}")

    # 空の応答はこのモーダルを閉じる（ここまで 3 秒以内である必要あり）
    ack()

@app.action("open-modal-button")
def handle_search_command(ack: Ack, body: dict, context: BoltContext, client: WebClient):
    # 受信した旨を 3 秒以内に Slack サーバーに伝えます
    ack()
    # views.open という API を呼び出すことでモーダルを開きます
    modal_view = build_modal_view()
    if context.channel_id is None:
        modal_view["blocks"].append(add_channel_info())
    else:
        # private_metadata に文字列として JSON を渡します
        # スラッシュコマンドやメッセージショートカットは必ずチャンネルがあるのでこれだけで OK
        state = {"channel_id": context.channel_id}
        modal_view["private_metadata"] = json.dumps(state)

    client.views_open(
        # 上記で説明した trigger_id で、これは必須項目です
        # この値は、一度のみ 3 秒以内に使うという制約があることに注意してください
        trigger_id=body["trigger_id"],
        # モーダルの内容を view オブジェクトで指定します
        view=modal_view,
    )

@app.event("app_mention")
def handle_app_mention_events(event: dict, say: Say):
    # ack() は @app.event の場合、省略可能
    # ボタンつきのメッセージを投稿、ボタンが押されたらモーダルを開く
    say(blocks=[button_block_view()])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dict_path', help='Path to tokenizer dictionary', type=str, default="/usr/local/lib/mecab/dic/mecab-ipadic-neologd")
    parser.add_argument('--index_name', help='Input ElasticSearch Index', type=str, default='test')
    parser.add_argument('--topn', help='Number of Getting resopnses', type=str, default=5)
    global args 
    args = parser.parse_args()
    global engine 
    engine = SearchEngine(dict_path=args.dict_path)
    
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()


    #test_query = "日本の政治で、日本国民の反応がよかった記事"
    #_get_news(query=test_query)
    


