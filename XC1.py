import requests, threading
from datetime import datetime
from requests.structures import CaseInsensitiveDict
baseUrl="https://z7api.superlozzi.com/"
total_xc=0
def setHeader(d,t):
	headers = CaseInsensitiveDict()
	headers["host"] = "z7api.superlozzi.com"
	headers["x-locale"] = "en"
	headers["content-language"] = "en"
	headers["user-agent"] = "locale=en_US|lang_code=en|country_code=AA|version_code=33|os_type=os_tp_android|version_name=3.3"
	headers["accept"] = "application/json"
	headers["content-type"] = "application/x-www-form-urlencoded"
	headers["accept-encoding"] = "gzip"
	headers["device_id"] = d
	headers["access_token"] = t
	return headers
		
def App(d,t):
	global total_xc
	try:
		path="v2/XC_ISSUE_DEF"
		XC_DEF = requests.post(baseUrl+path, headers=setHeader(d,t))
		XC_DEF_J=XC_DEF.json()
		if XC_DEF.status_code == 200:
			#print("ok")
			for box in XC_DEF_J["box_common"]:
				if box["xc_tp_cd_id"] == "XC_EVNT_0003":
					WITHOUT_AD(box,d,t)
				elif box["xc_tp_cd_id"] == "XC_EVNT_0004":
					WITH_AD(box,d,t)
				else:
					print(box["xc_tp_cd_id"])
						
			for boxG in XC_DEF_J["box_gold"]:
				BOX_GOLD(boxG,d,t)
				
			total_xc+=XC_DEF_J["xc_amount"]
			#print("Total_XC:", total_xc)
		else:
			print(XC_DEF_J)
	except requests.exceptions.ConnectionError:
		App(d,t)
	except Exception as error:
		print("")
		
def WITHOUT_AD(box,d,t):
	global total_xc
	try:
		path="v2/XC_ISSUE_BOX_COMMON_WITHOUT_AD"
		data1=f'seq_no={box["seq_no"]}&box_key={box["box_key"]}'
		ISSUE1 = requests.post(baseUrl+path, headers=setHeader(d,t), data=data1)
		if ISSUE1.status_code == 200:
			ISSUE1_J=ISSUE1.json()
			total_xc+=ISSUE1_J["xc_amount"]
			#print(ISSUE1_J["xc_amount"])
	except requests.exceptions.ConnectionError:
		WITHOUT_AD(box,d,t)
	except Exception as error:
		print("")

def WITH_AD(box,d,t):
	global total_xc
	try:
		path="v2/XC_ISSUE_BOX_COMMON_WITH_AD"
		data2=f'seq_no={box["seq_no"]}&box_key={box["box_key"]}'
		ISSUE2 = requests.post(baseUrl+path, headers=setHeader(d,t), data=data2)
		if ISSUE2.status_code == 200:
			ISSUE2_J=ISSUE2.json()
			total_xc+=ISSUE2_J["xc_amount"]
			#print(ISSUE2_J["xc_amount"])
	except requests.exceptions.ConnectionError:
		WITH_AD(box,d,t)
	except Exception as error:
		print("")
				
def BOX_GOLD(boxG,d,t):
	global total_xc
	try:
		path="v2/XC_ISSUE_BOX_GOLD"
		data3=f'xc_cd_id_r=XC_RATE_0000&seq_no={boxG["seq_no"]}&box_key={int(boxG["box_key"])}'
		ISSUE3 = requests.post(baseUrl+path, headers=setHeader(d,t), data=data3)
		if ISSUE3.status_code == 200:
			ISSUE3_J=ISSUE3.json()
			total_xc+=ISSUE3_J["xc_amount"]
			#print(ISSUE3_J["xc_amount"])
		else:
			print(ISSUE3.json())
	except requests.exceptions.ConnectionError:
		BOX_GOLD(boxG,d,t)
	except Exception as error:
		print("")

def USER_INFO(d,t):
    path = "v2/XC_USER_INFO"
    try:
    	U_Info = requests.get(baseUrl+path, headers=setHeader(d,t))
    	U_Info_J=U_Info.json()
    	nits=datetime.fromtimestamp(int(U_Info_J["etc_info"]["next_issue_timestamp"]))
    	etnd=datetime.fromtimestamp(int(U_Info_J["exchange_to_next_dt"]))
    	if datetime.now() >= nits:
    		App(d,t)
    		print(f'{int(U_Info_J["xc_amount"]):,}')
    except requests.exceptions.ConnectionError:
    	USER_INFO(d,t)
    except Exception as error:
    	print("")

def Go(d,t):
	while True:
		USER_INFO(d,t)
		
list_th = []
def getContent():
	try:
		url="https://raw.githubusercontent.com/Htrick98/Lozzi/main/maillist1.txt"
		response = requests.get(url)
		for line in response.iter_lines():
			acc=line.decode("utf-8").strip()
			d = acc.split('|')[1]
			t = acc.split('|')[3]
			list_th.append(threading.Thread(target=Go, args=(d,t)))
	except requests.exceptions.ConnectionError:
		getContent()
		
getContent()
for th in list_th:
	th.start()
	
	