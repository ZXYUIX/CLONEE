import base64
import re
import requests

from lxml import etree
from urllib.parse import urlparse, parse_qs

from bot import UNIFIED_EMAIL, UNIFIED_PASS, GDTOT_CRYPT, HUBDRIVE_CRYPT, KATDRIVE_CRYPT, DRIVEFIRE_CRYPT
from bot.helper.ext_utils.exceptions import DDLException

account = {
    'email': UNIFIED_EMAIL, 
    'passwd': UNIFIED_PASS
}

def account_login(client, url, email, password):
    data = {
        'email': email,
        'password': password
    }
    client.post(f'https://{urlparse(url).netloc}/login', data=data)

def gen_payload(data, boundary=f'{"-"*6}_'):
    data_string = ''
    for item in data:
        data_string += f'{boundary}\r\n'
        data_string += f'Content-Disposition: form-data; name="{item}"\r\n\r\n{data[item]}\r\n'
    data_string += f'{boundary}--\r\n'
    return data_string

def unified(url: str) -> str:
    if (UNIFIED_EMAIL or UNIFIED_PASS) is None:
        raise DDLException("APPDRIVE_EMAIL and APPDRIVE_PASS env vars not provided")
    client = requests.Session()
    client.headers.update({
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
    })
    account_login(client, url, account['email'], account['passwd'])
    res = client.get(url)
    try:
        key = re.findall(r'"key",\s+"(.*?)"', res.text)[0]
    except IndexError:
        raise DDLException("Invalid link")
    ddl_btn = etree.HTML(res.content).xpath("//button[@id='drc']")
    info = {}
    info['error'] = False
    info['link_type'] = 'login' # direct/login
    headers = {
        "Content-Type": f"multipart/form-data; boundary={'-'*4}_",
    }
    data = {
        'type': 1,
        'key': key,
        'action': 'original'
    }
    if len(ddl_btn):
        info['link_type'] = 'direct'
        data['action'] = 'direct'
        
    while data['type'] <= 3:
        try:
            response = client.post(url, data=gen_payload(data), headers=headers).json()
            break
        except:
            data['type'] += 1
            
    if 'url' in response:
        info['gdrive_link'] = response['url']
        
    elif 'error' in response and response['error']:
        info['error'] = True
        info['message'] = response['message']
        
    if urlparse(url).netloc == 'driveapp.in' and not info['error']:
        res = client.get(info['gdrive_link'])
        drive_link = etree.HTML(res.content).xpath("//a[contains(@class,'btn')]/@href")[0]
        info['gdrive_link'] = drive_link
        
    if urlparse(url).netloc == 'drivesharer.in' and not info['error']:
        res = client.get(info['gdrive_link'])
        drive_link = etree.HTML(res.content).xpath("//a[contains(@class,'btn btn-primary')]/@href")[0]
        info['gdrive_link'] = drive_link

    if urlparse(url).netloc == 'drivebit.in' and not info['error']:
        res = client.get(info['gdrive_link'])
        drive_link = etree.HTML(res.content).xpath("//a[contains(@class,'btn btn-primary')]/@href")[0]
        info['gdrive_link'] = drive_link


    info['src_url'] = url
    
    return info['gdrive_link']

def appdrive(url: str) -> str:
    if (UNIFIED_EMAIL or UNIFIED_PASS) is None:
        raise ExceptionHandler("APPDRIVE_EMAIL and APPDRIVE_PASS env vars not provided")
    client = requests.Session()
    client.headers.update({
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
    })
    account_login(client, url, account['email'], account['passwd'])
    res = client.get(url)
    try:
        key = re.findall(r'"key",\s+"(.*?)"', res.text)[0]
    except IndexError:
        raise ExceptionHandler("Invalid link")
    ddl_btn = etree.HTML(res.content).xpath("//button[@id='drc']")
    info = {}
    info['error'] = False
    info['link_type'] = 'login'  # direct/login
    headers = {
        "Content-Type": f"multipart/form-data; boundary={'-'*4}_",
    }
    data = {
        'type': 1,
        'key': key,
        'action': 'original'
    }
    if len(ddl_btn):
        info['link_type'] = 'direct'
        data['action'] = 'direct'
    while data['type'] <= 3:
        try:
            response = client.post(url, data=gen_payload(data), headers=headers).json()
            break
        except:
            data['type'] += 1
    if 'url' in response:
        info['gdrive_link'] = response['url']
    elif 'error' in response and response['error']:
        info['error'] = True
        info['message'] = response['message']
    if not info['error']:
        return info
    else:
        raise ExceptionHandler(f"{info['message']}")

def parse_info(res):
    info_parsed = {}
    title = re.findall('>(.*?)<\/h4>', res.text)[0]
    info_chunks = re.findall('>(.*?)<\/td>', res.text)
    info_parsed['title'] = title
    for i in range(0, len(info_chunks), 2):
        info_parsed[info_chunks[i]] = info_chunks[i+1]
    return info_parsed

def udrive(url: str) -> str:
    client = requests.Session()
    if 'hubdrive' in url:
        client.cookies.update({'crypt': HUBDRIVE_CRYPT})
    if ('katdrive' or 'kolop') in url:
        client.cookies.update({'crypt': KATDRIVE_CRYPT})
    if 'drivefire' in url:
        client.cookies.update({'crypt': DRIVEFIRE_CRYPT})
    res = client.get(url)
    info_parsed = parse_info(res)
    info_parsed['error'] = False
    
    up = urlparse(url)
    req_url = f"{up.scheme}://{up.netloc}/ajax.php?ajax=download"
    
    file_id = url.split('/')[-1]
    
    data = { 'id': file_id }
    
    headers = {
        'x-requested-with': 'XMLHttpRequest'
    }
    
    try:
        res = client.post(req_url, headers=headers, data=data).json()['file']
    except: return {'error': True, 'src_url': url}
    
    if 'drivefire.co' in url:
      return res
    else:
      gd_id = re.findall('gd=(.*)', res, re.DOTALL)[0]
    
    info_parsed['gdrive_url'] = f"https://drive.google.com/open?id={gd_id}"
    info_parsed['src_url'] = url

    return info_parsed['gdrive_url']        
        
def gdtot(url: str) -> str:
    if GDTOT_CRYPT is None:
        raise DDLException("GDTOT_CRYPT env var not provided")
    client = requests.Session()
    client.cookies.update({'crypt': GDTOT_CRYPT})
    res = client.get(url)
    res = client.get(f"https://new.gdtot.nl/dld?id={url.split('/')[-1]}")
    url = re.findall(r'URL=(.*?)"', res.text)[0]
    info = {}
    info['error'] = False
    params = parse_qs(urlparse(url).query)
    if 'gd' not in params or not params['gd'] or params['gd'][0] == 'false':
        info['error'] = True
        if 'msgx' in params:
            info['message'] = params['msgx'][0]
        else:
            info['message'] = 'Invalid link'
    else:
        decoded_id = base64.b64decode(str(params['gd'][0])).decode('utf-8')
        drive_link = f'https://drive.google.com/open?id={decoded_id}'
        info['gdrive_link'] = drive_link
    if not info['error']:
        return info['gdrive_link']
    else:
        raise DDLException(f"{info['message']}")
