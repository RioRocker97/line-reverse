import urllib3,json,certifi,os
HTTP = urllib3.PoolManager()
COMMON_HEADER = {
    'Authorization': 'Bearer '+ os.environ['LINE_TOKEN']
}

def get_webhook_point():
    this_header = COMMON_HEADER
    this_header['Content-Type'] = 'application/json'
    rep = HTTP.request('GET','https://api.line.me/v2/bot/channel/webhook/endpoint',headers=this_header)
    if(str(rep.status) == '200'):
        return json.load(json.loads(rep.data.decode('utf-8')))['endpoint']
    else:
        raise Exception("ERROR at Get Webhook Point")
def get_img(id):
    this_header = COMMON_HEADER
    rep = HTTP.request('GET','https://api-data.line.me/v2/bot/message/'+id+'/content')

    if str(rep.status) == '200':
        print(rep.data)
    else:
        raise Exception("ERROR at Get IMG")
def text_reply(reply_token,msg="This reply came from developer's Laptop"):
    this_header = COMMON_HEADER
    this_header['Content-Type'] = 'application/json'
    data = json.dumps({
        "replyToken": reply_token,
        "messages":[
            {
                "type":"text",
                "text":msg
            }
        ]
    }).encode('utf-8')
    
    rep = HTTP.request('POST','https://api.line.me/v2/bot/message/reply',
        body = data)
    
    if str(rep.status) == '200':
        print('Reply OK')
    else :
        print('Reply ERROR')

