import threading, requests
import time
from requests.structures import CaseInsensitiveDict
baseUrl="https://api.superlozzi.com/v2/"
next_file=0
total_xc=0
c=0
def App(line):
	global next_file
	global total_xc
	global c
	headers = CaseInsensitiveDict()
	headers["host"] = "z7api.superlozzi.com"
	headers["x-locale"] = "en"
	headers["content-language"] = "en"
	headers["user-agent"] = "locale=en_US|lang_code=en|country_code=AA|version_code=33|os_type=os_tp_android|version_name=3.3"
	headers["accept"] = "application/x-www-form-urlencoded"
	headers["content-type"] = "application/x-www-form-urlencoded"
	#headers["user-timezone"] = "Africa/Cairo"
	headers["accept-encoding"] = "gzip"
	acc=line.strip().split("|")
	headers["device_id"] = acc[2]
	headers["access_token"] = acc[3]
	headers["refresh_token"] = acc[3]
	headers["authorization"] = "Bearer "+acc[3]
			
	try:
		path="XC_USER_INFO"
		U_Info = requests.get(baseUrl+path, timeout=60, headers=headers)
		U_Info_J=U_Info.json()
		if U_Info.status_code == 200:
			try:
				path="XC_ISSUE_DEF"
				XC_DEF = requests.post(baseUrl+path, timeout=60, headers=headers)
				XC_DEF_J=XC_DEF.json()
				if XC_DEF.status_code == 200:
					xc_amount=0
					for box in XC_DEF_J["box_common"]:
						if box["xc_tp_cd_id"] == "XC_EVNT_0003":
							path="XC_ISSUE_BOX_COMMON_WITHOUT_AD"
							data1=f'seq_no={box["seq_no"]}&box_key={box["box_key"]}'
							ISSUE1 = requests.post(baseUrl+path, timeout=60, headers=headers, data=data1)
							ISSUE1_J=ISSUE1.json()
							xc_amount+=ISSUE1_J["xc_amount"]
						elif box["xc_tp_cd_id"] == "XC_EVNT_0004":
							path="XC_ISSUE_BOX_COMMON_WITH_AD"
							data2=f'seq_no={box["seq_no"]}&box_key={box["box_key"]}'
							ISSUE2 = requests.post(baseUrl+path, timeout=60, headers=headers, data=data2)
							ISSUE2_J=ISSUE2.json()
							xc_amount+=ISSUE2_J["xc_amount"]
						else:
							print(box["xc_tp_cd_id"])
									
					for boxG in XC_DEF_J["box_gold"]:
						path="XC_ISSUE_BOX_GOLD"
						data3=f'seq_no={boxG["seq_no"]}&box_key={boxG["box_key"]}'
						ISSUE3 = requests.post(baseUrl+path, timeout=60, headers=headers, data=data3)
						ISSUE3_J=ISSUE3.json()
						xc_amount+=ISSUE3_J["xc_amount"]
					if int(ISSUE3_J["xc_amount"]) > 1:
						ta=(int(U_Info_J["xc_amount"])+xc_amount)
						d=int(float(ta/1000000))
						print(f'{U_Info_J["user_info"]["user_nm"]} | {xc_amount} | {ta:,} | {d}')
						total_xc+=xc_amount
						c+=1
						next_file=0
					if int(ISSUE3_J["xc_amount"]) == 1:
						next_file+=1
				#else:
				#	print(XC_DEF.status_code)
			except requests.exceptions.ConnectionError:
				print("requests.exceptions.ConnectionError")
			except Exception as error:
				print(error)
				print("exp 1")
						
		else:
			print(U_Info_J)
	except requests.exceptions.ConnectionError:
		print("requests.exceptions.ConnectionError")
	except Exception as error:
		print(error)
		print("exp 2")
		
threads = []
i=7

def MainApp(_i):
	global i
	global next_file
	path=f"token{_i}.txt"
	#path=f"/storage/emulated/0/Python/SuperLozzi/GroupV2/TokenV2/token{_i}.txt"
	with open(path, 'r') as f:
		for line in f:
			t = threading.Thread(target=App, args=[line])
			threads.append(t)
			t.start()
			
		for th in threads:
			th.join()
		print(f"xc cleam : {total_xc:,}")
		print("conter : ",c)
		f.close()
		if next_file == 15:
			i-=1
			next_file=0
			print("witing 10 min")
			time.sleep(660)
			MainApp(i)
		else:
			time.sleep(30)
			MainApp(i)
		
	
MainApp(i)
