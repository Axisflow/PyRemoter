# 我們需要3個 port: (1)狀態溝通伺服器(TCP)，(2)鍵鼠、命令、檔案控制伺服器(TCP)，(3)影音傳輸伺服器(UDP)

## 1-1 (1)新客戶端在開啟時會跟伺服器要識別代碼(類似Teamviewer的)
	client send: {status:"GetID", mac:<MAC address>}  
	client rece: {status:<"GetIDSuccess"/"GetIDFail">[, id:<ID number>, pwd:<password> reason:<Why Fail?>]}

## 1-2 (1)客戶端在開啟時若有舊登入資訊，會跟伺服器要新密碼(若設定為密碼永久不變則不用回傳密碼)
	client send: {status:"Login", id:<ID number>, pwd:<old password>}  
	client rece: {status:<"LoginSuccess"/"LoginFail">[, pwd:<new password>, reason:<Why Fail?>]}

## 1-3 (1)註冊新客戶端
	client send: {status:"Register", mac:<MAC address>, id:<ID number>, pwd:<password>, permenant:<True/False>}  
	client rece: {status:<"RegisterSuccess"/"RegisterFail">[, reason:<Why Fail?>]}

## 2-1 (1)保持連接，如果想控制其他客戶端
	client send: {status:"AskConn", to:<{ID1, ID2, ...}>, password:<{"pwd1", "pwd2", ...}>} # 密碼若是空字串則代表使用詢問模式，否則使用直接連接模式  
	client rece: {status:<"AskConnSuccess"/"AskConnFail">, from:<ID number>[, reason:<Why Fail?>, UDPip:<IP address or alias name>, UDPport:<port number>, TCPip:<格式一樣>, TCPport:<格式一樣>]} # 傳回影音傳輸伺服器、鍵鼠控制伺服器位置

## 2-2 (1)保持連接，以知道是否有被控需求，如果有
	client rece: {status:"NeedConn", from:<ID number>, directly:<True/False>, UDPip:<IP address or alias name>, UDPport:<port number>, TCPip:<格式一樣>, TCPport:<格式一樣>} # directly: True 直接連接模式， False 詢問模式  
	client send: {status:<"NeedConnAccept"/"NeedConnRefuse">, to:<ID number>[, reason:<Why Refuse?>]} # 有可能被加入黑名單，或在詢問模式被拒絕了之類的

==============================================================================

# General: 傳至正確的被控端並去除 ID number (也可以不用？)

## 3-1 (2)控制端傳輸滑鼠座標
	client send: {type:"MousePoint", to:<ID number>, mx:<mouse point x>, my:<mouse point y>}

## 3-2 (2)被控端接收滑鼠座標
	client rece: {type:"MousePoint", mx:<mouse point x>, my:<mouse point y>}

## 4-1 (2)控制端傳輸滑鼠動作
	client send: {type:"MouseEvent", to:<ID number>, mtype:<mouse event>}

## 4-2 (2)被控端接收滑鼠動作
	client rece: {type:"MouseEvent", mtype:<mouse event>}

## 5-1 (2)控制端傳輸鍵盤按鍵組合
	client send: {type:"Key", to:<ID number>, key:<{key1, key2, ...}>}

## 5-2 (2)被控端接收鍵盤按鍵組合
	client rece: {type:"Key", key:<{key1, key2, ...}>}

===============================================================================

# General: 加上被控端的 ID number 再傳至控制端

## 6-1 (3)被控端傳輸螢幕畫面
	client send: screen;<screen data>

## 6-2 (3)控制端接收螢幕畫面
	client rece: <ID number>;screen;<screen data>

## 7-1 (3)被控端傳輸聲音
	client send: audio;<audio data>

## 7-2 (3)控制端接收聲音
	client rece: <ID number>;audio;<audio data>

===============================================================================

# 做個簡單類似 SNMP 的功能

## 8-1 (2)控制端請求查詢狀態
	client send: {status:"AskMonitor", to:<ID number>, question:<Anything>}  
	client rece: {status:<"AskMonitorSuccess/AskMonitorFail">, from:<ID number>, question:<Anything>[, answer:<Anything>, reason:<Why Fail?>]}

## 8-2 (2)被控端回復狀態查詢
	client rece: {status:"NeedMonitor", from:<ID number>, question:<Anything>}  
	client send: {status:<"NeedMonitorAccept/NeedMonitorRefuse">, to:<ID number>, question:<Anything>[, answer:<Anything>, reason:<Why Refuse?>]}

===============================================================================

## 9-1 (1)被控端中斷控制，被控端應
	client send: {status:"AbortNeedConn", to:<ID number>}

## 9-2 (1)被控端中斷控制，控制端應
	client rece: {status:"AbortNeedConn", from:<ID number>}

## 10-1 (1)控制端中斷控制，控制端應
	client send: {status:"AbortAskConn", to:<{ID1, ID2, ...}>}

## 10-2 (1)控制端中斷控制，被控端應
	client rece: {status:"AbortAskConn", from:<ID number>}

===============================================================================

## 11 (1)要求伺服器更改客戶端密碼
	client send: {status:"ChangePassword", password:<Password>}  
	client rece: {status:<"ChangePasswordSuccess"/"ChangePasswordFail">[, reason:<Why Fail?>]}

## 12 中斷連線
	# 內建函式可以處理

===============================================================================

# 其他設定
# General:
# 	設定(Set)
# 		client send: {status:"SetInfo", key:<key>, value:<value>}  
# 		client rece: {status:<"SetInfoSuccess"/"SetInfoFail">[, key:<key>, reason:<Why Fail?>]}
# 	查詢(Get)
# 		client send: {status:"GetInfo", key:<key>}  
# 		client rece: {status:<"GetInfoSuccess"/"GetInfoFail">[, key:<key>, value:<value>, reason:<Why Fail?>]}

## 13-1 (1)設定密碼永久性
	client send: {status:"SetInfo", key:"pwd_permenant", permenant:<True/False>}  
	client rece: {status:<"SetInfoSuccess"/"SetInfoFail">[, key:"pwd_permenant", reason:<Why Fail?>]}
