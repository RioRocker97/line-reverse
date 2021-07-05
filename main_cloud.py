from flask import Response
from google.cloud import storage,vision
import json,urllib3,os,time,base64
#------Support--------
HTTP = urllib3.PoolManager()
COMMON_HEADER = {
    'Authorization': 'Bearer '+ os.environ['LINE_TOKEN']
}
GCP_BUCKET = os.environ['GCP_B']
GCP_BUCKET_URL = os.environ['GCP_B_URL']
def construct_flex_msg(img_url,guess_label):
    try:
        json_file = open('./flex_1.json','r')
        flex = json.load(json_file)
        json_file.close()
        flex['body']['contents'][0]['url'] = str(img_url)
        flex['body']['contents'][2]['contents'][0]['contents'][1]['contents'][0]['text'] = str(guess_label)
        return flex
    except:
        print('ERROR loading FLEX-JSON')
def reverse_search(img_byte):
    search = vision.ImageAnnotatorClient()
    img = vision.Image(content=img_byte)
    req_param = vision.WebDetectionParams()
    context = vision.ImageContext(web_detection_params=req_param)

    response = search.web_detection(image=img, image_context=context)
    print(str(response.web_detection.best_guess_labels[0]).split('\n')[0].split('"')[1])
    return str(response.web_detection.best_guess_labels[0]).split('\n')[0].split('"')[1]
def upload_img(img_id,data):
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCP_BUCKET)
    blob = bucket.blob(str(img_id)+'.jpg')

    try:
        blob.upload_from_string(data,content_type='image/jpeg')
        print('Imaged Upload !')
        return GCP_BUCKET_URL+str(img_id)+'.jpg'
    except:
        print('ERROR uploading')
        return "ERROR"
def get_webhook_point():
    this_header = COMMON_HEADER
    this_header['Content-Type'] = 'application/json'
    rep = HTTP.request('GET','https://api.line.me/v2/bot/channel/webhook/endpoint',headers=this_header)
    if(str(rep.status) == '200'):
        return json.load(json.loads(rep.data.decode('utf-8')))['endpoint']
    else:
        raise Exception("ERROR at Get Webhook Point")
def push_reply(user,flex_body):
    this_header = COMMON_HEADER
    this_header['Content-Type'] = 'application/json'
    data = json.dumps({
        "to":user,
        "messages":[{
            "type":"flex",
            "altText": "Reverse Image search in Flex style",
            "contents": flex_body     
        }]
    })
    rep = HTTP.request('POST','https://api.line.me/v2/bot/message/push',headers=this_header,body=data)

    if str(rep.status) == '200':
        print('push reply {',user,'} OK')
    else:
        print(rep.data)
        raise Exception('push reply ERROR')
def img_reply(id,user_id):
    this_header = COMMON_HEADER
    rep = HTTP.request('GET','https://api-data.line.me/v2/bot/message/'+id+'/content',headers=this_header)

    if str(rep.status) == '200':
        print('-------IMG-----------')
        img_url = upload_img(id,rep.data)
        push_reply(user_id,construct_flex_msg(img_url,reverse_search(rep.data)))
        print('-------IMG-----------')
    else:
        raise Exception("ERROR at Get IMG")
def text_reply(reply_token,msg="Another One Webhook"):
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
    })
    rep = HTTP.request('POST','https://api.line.me/v2/bot/message/reply',
        body = data,headers=this_header)
    
    if str(rep.status) == '200':
        print('Reply OK')
    else :
        print(rep.data)
        print('Reply ERROR')
#------Support--------


def webhook(request):
    line_events = request.json['events']
    for event in line_events:
        if event['type']=='message':
            token = event['replyToken']
            address = event['source']
            payload = event['message']
            if payload['type'] == 'text':
                print("from : ",address['userId'])
                print("Text msg : ",payload['text'])
                text_reply(token)
            if payload['type'] == 'image':
                user_id = address['userId']
                img_id = payload['id']
                print("LINE image ID : ",img_id)
                text_reply(token,msg="Searching.... Please Wait")
                t0 = time.time()
                img_reply(img_id,user_id)
                print("Time used : %.2f" % (time.time()-t0))
    return Response(status=200)
