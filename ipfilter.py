from urllib import request,error
import json
ipbuf_black=[]
ipbuf_white=[]
target_region='XX'
def ipfilter(ip):
    if ip in ipbuf_white:
        return True
    if ip in ipbuf_black:
        return False
    try:
        rsp=request.urlopen('http://ip-api.com/json/%s'%ip)
        text=rsp.read(300)
        text_j=json.loads(text)
        if text_j['region'] == target_region:
            ipbuf_white.append(ip)
            return True
        else:
            ipbuf_black.append(ip)
            return False
    except error.HTTPError as e:
        print(e.reason)
        print(e.code)
        print(e.headers)
    except error.URLError as e:
        print(e.reason)
    return False