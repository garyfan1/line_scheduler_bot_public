import os
from chalice import Chalice, Response
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, PostbackEvent, FlexSendMessage
)
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import requests
import json
from dateutil import parser

from chalicelib.dt_parser import dt_convert
from dateutil.relativedelta import relativedelta

app = Chalice(app_name='functionB')

line_bot_api = LineBotApi(os.getenv("LINE_BOT_API_KEY"))
handler = WebhookHandler(os.getenv("WEBHOOK_HANDLER"))

SCHEDULER_URL = os.getenv("SCHEDULER_URL")
MY_URL = os.getenv("MY_URL")
WRITE_KEY=os.getenv("WRITE_KEY")


jwt_token = requests.request("GET", headers={"write_key": WRITE_KEY},
                             url=SCHEDULER_URL+"jwt").json()["jwt_token"]


def update_jwt():
    global jwt_token
    jwt_token = requests.request("GET", headers={"write_key": WRITE_KEY},
                                 url=SCHEDULER_URL+"jwt").json()["jwt_token"]


@app.route('/')
def index():
    return {'hello': 'world'}


@app.route("/callback", methods=['POST'])
def callback():
    request = app.current_request
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.raw_body.decode('utf-8')
    # app.logger.info("Request body: " + body)
    print(body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        # return ChaliceViewError('error')

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("received message!!!")
    user_id = event.source.user_id
    # text = event.message.text.split('\n', 1)
    # date_time = text[0]
    # message = text[1]

    text = event.message.text
    print("before entering dt_convert")
    date_time = dt_convert(text)
    message = text

    scheduler_url = SCHEDULER_URL
    payload = json.dumps({
        "target_info": {
            "date_time": date_time,
            "callback": MY_URL+"line_push",
            "method": "POST"
        },
        "data": {
            "user_id": user_id,
            "message": message
        }
    })
    headers = {
        'Content-Type': 'application/json',
        "jwt_token": jwt_token
    }
    print("send request to scheduler for scheduling")
    response = requests.request("POST", scheduler_url, headers=headers, data=payload)
    if response.status_code == 200:
        response = response.json()
    elif response.status_code == 403:
        update_jwt()
        headers = {
            'Content-Type': 'application/json',
            "jwt_token": jwt_token
        }
        response = requests.request("POST", scheduler_url, headers=headers, data=payload).json()
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response.text))
        return

    date_time = parser.parse(date_time) + relativedelta(hours=8)
    date_time = date_time.strftime("%Y年%m月%d號%H時%M分")

    # reply_text = "I'll send you a reminder for\n" + message + "\non\n" + date_time

    event_name = response["rule_name"]
    flex_content = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "Event Scheduled!",
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "Message",
                                    "color": "#aaaaaa",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": message,
                                    "wrap": True,
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 5
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "When?",
                                    "color": "#aaaaaa",
                                    "size": "sm",
                                    "flex": 1
                                },
                                {
                                    "type": "text",
                                    "text": date_time,
                                    "wrap": True,
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 5
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": "Cancel Event",
                        "data": event_name
                    }
                }
            ],
            "flex": 0
        }
    }
    flex_message = FlexSendMessage(alt_text="cancel event", contents=flex_content)

    line_bot_api.reply_message(event.reply_token, flex_message)

    print("flex message sent")


@handler.add(PostbackEvent)
def cancel_event(event):
    data = event.postback.data
    reply_token = event.reply_token

    headers = {
        'Content-Type': 'application/json',
        "jwt_token": jwt_token
    }

    scheduler_url = SCHEDULER_URL + "events/" + data

    response = requests.request(method="DELETE", headers=headers, url=scheduler_url)

    if response.status_code == 403:
        update_jwt()
        headers = {
            'Content-Type': 'application/json',
            "jwt_token": jwt_token
        }
        response = requests.request(method="DELETE", headers=headers, url=scheduler_url)

    if response.status_code == 200:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=data + " deleted"))
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="something went wrong"))



@app.route('/line_push', methods=["POST"])
def line_push_message():
    data = app.current_request.json_body

    user_id = data["user_id"]
    message = data["message"]

    line_bot_api.push_message(user_id, TextSendMessage(text=message))
