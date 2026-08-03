#!/usr/bin/env python3
import os,requests,uuid
base=os.environ['BASE_URL'].rstrip('/');auth=(os.environ['AUTH_USER'],os.environ['AUTH_PASSWORD'])
status=requests.get(base+'/status',timeout=30);assert status.status_code==200 and status.text.strip()=='OK'
locked=requests.get(base+'/',timeout=30);assert locked.status_code==401
home=requests.get(base+'/',auth=auth,timeout=30);assert home.status_code==200 and 'Apprise' in home.text
missing=requests.get(base+'/railway-missing-resource',auth=auth,timeout=30);assert missing.status_code==404
print('Apprise API smoke checks passed')
