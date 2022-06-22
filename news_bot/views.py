import copy

def build_modal_view() -> dict:
    return {
        # このタイプは常に "modal"
        "type": "modal",
        # このモーダルに自分で付けられる ID で、次に説明する @app.view リスナーはこの文字列を指定します
        "callback_id": "search-id",
        # これは省略できないため、必ず適切なテキストを指定してください
        "title": {"type": "plain_text", "text": "ニュース検索"},
        # input ブロックを含まないモーダルの場合は view から削除することをおすすめします
        # このコード例のように input ブロックがあるときは省略できません
        "submit": {"type": "plain_text", "text": "送信"},
        # 閉じるボタンのラベルを調整することができます（必須ではありません）
        "close": {"type": "plain_text", "text": "閉じる"},
        # Block Kit の仕様に準拠したブロックを配列で指定
        # 見た目の調整は https://app.slack.com/block-kit-builder を使うと便利です
        "blocks": [
            {
                # 様々なブロックのうち input ブロックだけがデータ送信に含まれます
                # ブロックの一覧はこちら: https://api.slack.com/reference/block-kit/blocks
                "type": "input",
                # block_id / action_id を指定しない場合 Slack がランダムに指定します
                # この例のように明に指定することで、@app.view リスナー側での入力内容の取得で
                # ブロックの順序に依存しないようにすることをおすすめします
                "block_id": "question-block",
                # ブロックエレメントの一覧は https://api.slack.com/reference/block-kit/block-elements
                # Works with block types で Input がないものは input ブロックに含めることはできません
                "element": {"type": "plain_text_input", "action_id": "input-element"},
                # これはモーダル上での見た目を調整するものです
                # 同様に placeholder を指定することも可能です 
                "label": {"type": "plain_text", "text": "検索box"},
            }
        ],
    }

def add_channel_info() -> dict:
    return {
        "type": "input",
        "block_id": "channel_to_notify",
        "element": {
            "type": "conversations_select",
            "action_id": "_",
            # response_urls を発行するためには
            # このオプションを設定しておく必要があります
            "response_url_enabled": True,
            # 現在のチャンネルを初期値に設定するためのオプション
            "default_to_current_conversation": True,
        },
        "label": {
            "type": "plain_text",
            "text": "起動したチャンネル",
        },
    }

def button_block_view() -> dict:
    return {
        "type": "section",
        "block_id": "button-block",
        "text": {
            "type": "mrkdwn",
            "text": "ボタンをクリックすると検索開始します！",
        },
        "accessory": {
            "type": "button",
            "text": {"type": "plain_text", "text": "Newsbot START!"},
            "value": "clicked",
            # この action_id を @app.action リスナーで指定します
            "action_id": "open-modal-button",
        },
    }

def _say_template_view():
    blocks_template = [
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ""
            },
            "accessory": {
                "type": "image",
                "image_url": "",
                "alt_text": ""
            }
        },
    ]
    attachments= [
        {
            "color": "#f2c744",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "検索結果の *TOP5:crown:* を表示"
                    }
                },
            ]
        }
    ]
    return blocks_template, attachments

def make_say_template_view(response) -> dict:
    blocks_template, attachments = _say_template_view()
    text_template = " *<{url}|{title}>*\n{article}\n  Similarity Score: {score} "

    for res in response["hits"]["hits"]:
        _blocks = copy.deepcopy(blocks_template)
        title = res["_source"]["title"]
        article = res["_source"]["article"]
        page_url = res["_source"]["page_url"]
        img_url = res["_source"]["img_url"]
        score = res["_score"]
        _id = res["_id"]
        _blocks[1]["text"]["text"] = text_template.format(url=page_url, title=title, article=article, score=str(score))
        _blocks[1]["accessory"]["image_url"] = img_url
        _blocks[1]["accessory"]["alt_text"] = _id

        attachments[0]["blocks"] += _blocks

    return attachments