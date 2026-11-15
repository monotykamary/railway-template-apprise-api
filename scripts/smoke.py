#!/usr/bin/env python3
"""Repeatable product checks; credentials remain process-local and never printed."""
import os,json,time,uuid,hashlib,tempfile,base64,urllib.request,urllib.error,urllib.parse
from pathlib import Path
base=os.environ['BASE_URL'].rstrip('/')
phase=os.environ.get('SMOKE_PHASE','boot')
state=Path(tempfile.gettempdir())/('railway-smoke-'+hashlib.sha256(base.encode()).hexdigest()[:16]+'.json')
def req(path,method='GET',data=None,auth=None,headers=None):
 h=dict(headers or {})
 if auth:
  h['Authorization']='Basic '+base64.b64encode((':'.join(auth)).encode()).decode() if isinstance(auth,tuple) else 'Bearer '+auth
 if isinstance(data,dict):h['Content-Type']='application/json';data=json.dumps(data).encode()
 if isinstance(data,str):data=data.encode()
 r=urllib.request.Request(base+path,data=data,headers=h,method=method)
 try:
  with urllib.request.urlopen(r,timeout=45) as x:return x.status,x.read().decode()
 except urllib.error.HTTPError as e:return e.code,e.read().decode()
def good(result,codes=(200,)):
 assert result[0] in codes, 'unexpected HTTP status '+str(result[0])
 return result[1]
def asjson(result,codes=(200,)):return json.loads(good(result,codes))

auth=(os.environ['AUTH_USER'],os.environ['AUTH_PASSWORD'])
assert good(req('/status')).strip()=='OK'
assert req('/')[0]==401
assert req('/',auth=(auth[0],'incorrect-password'))[0]==401
assert 'Apprise' in good(req('/',auth=auth))
import socket,threading
from http.server import BaseHTTPRequestHandler,HTTPServer
received=[]
class Sink(BaseHTTPRequestHandler):
 def do_POST(self):
  received.append(self.rfile.read(int(self.headers.get('Content-Length','0'))).decode())
  self.send_response(200);self.end_headers();self.wfile.write(b'OK')
 def log_message(self,*args):pass
if phase=='boot':
 key='railway-'+uuid.uuid4().hex
 route=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);route.connect(('1.1.1.1',53));host=route.getsockname()[0];route.close()
 sink=HTTPServer(('0.0.0.0',int(os.environ.get('CALLBACK_PORT','0'))),Sink)
 target=os.environ.get('CALLBACK_PUBLIC_URL') or ('json://'+host+':'+str(sink.server_port))
 body=urllib.parse.urlencode({'urls':target}).encode()
 good(req('/add/'+key,method='POST',data=body,auth=auth,headers={'Content-Type':'application/x-www-form-urlencoded'}),(200,201))
 state.write_text(json.dumps({'key':key,'target':target,'port':sink.server_port}))
saved=json.loads(state.read_text())
config=good(req('/get/'+saved['key'],method='POST',data=b'',auth=auth))
assert urllib.parse.urlsplit(saved['target']).hostname in config, 'stored notification configuration missing'
if phase!='boot':sink=HTTPServer(('0.0.0.0',saved['port']),Sink)
thread=threading.Thread(target=sink.serve_forever,daemon=True);thread.start()
try:
 good(req('/notify/'+saved['key'],method='POST',data={'title':'Railway validation','body':'persisted configuration delivery probe'},auth=auth),(200,202))
 assert received and 'persisted configuration delivery probe' in received[0], 'notification not delivered to controlled receiver'
finally:
 sink.shutdown();sink.server_close()
assert req('/railway-missing-resource',auth=auth)[0]==404
print(json.dumps({'phase':phase,'product':'apprise','auth':True,'persistent_configuration':True,'controlled_webhook_delivery':True}))
