# 我們需要3個 port: (1)狀態溝通伺服器(TCP，JSON)，(2)鍵鼠命令控制伺服器(TCP，JSON)，(3)影音傳輸伺服器(TCP，分號分隔值字串)
# 傳送的資料前面都須加上 4 bytes 的長度資訊，以確保資料完整性

## 1-1 (1)新客戶端在開啟時會跟伺服器要識別代碼(類似Teamviewer的)
	client send: {status:"GetID", mac:<MAC address>}  
	client rece: {status:<"GetIDSuccess"/"GetIDFail">[, id:<ID number>, pwd:<password> reason:<Why Fail?>]}

## 1-2 (1)客戶端在開啟時若有舊登入資訊，會跟伺服器要新密碼(若設定為密碼永久不變則不用回傳密碼)
	client send: {status:"Login", mac:<MAC address>, id:<ID number>, pwd:<old password>}  
	client rece: {status:<"LoginSuccess"/"LoginFail">[, pwd:<new password>, reason:<Why Fail?>]}

## 1-3 (1)註冊新客戶端
	client send: {status:"Register", mac:<MAC address>, id:<ID number>, pwd:<password>, permenant:<True/False>}  
	client rece: {status:<"RegisterSuccess"/"RegisterFail">[, reason:<Why Fail?>]}

## 2-1 (1)保持連接，如果想控制其他客戶端
	client send: {status:"AskConn", to:<{ID1, ID2, ...}>, pwd:<{"pwd1", "pwd2", ...}>} # 密碼若是空字串則代表使用詢問模式，否則使用直接連接模式  
	client rece: {status:<"AskConnSuccess"/"AskConnFail">, from:<ID number>[, reason:<Why Fail?>, UDPip:<IP address or alias name>, UDPport:<port number>, TCPip:<格式一樣>, TCPport:<格式一樣>]} # 傳回影音傳輸伺服器、鍵鼠控制伺服器位置

## 2-2 (1)保持連接，以知道是否有被控需求，如果有
	client rece: {status:"NeedConn", from:<ID number>, directly:<True/False>, UDPip:<IP address or alias name>, UDPport:<port number>, TCPip:<格式一樣>, TCPport:<格式一樣>} # directly: True 直接連接模式， False 詢問模式  
	client send: {status:<"NeedConnAccept"/"NeedConnRefuse">, to:<ID number>[, reason:<Why Refuse?>]} # 有可能被加入黑名單，或在詢問模式被拒絕了之類的

## 3 (2)第一次連接鍵鼠、命令、檔案控制伺服器時，應傳送登入資訊，以確認是否為合法客戶端
	client send: {type:"Login", from:<ID number>, pwd:<password>}  
	client rece: {type:<"LoginSuccess"/"LoginFail">[, reason:<Why Fail?>]}

## 4 (3)第一次連接影音傳輸伺服器時，應傳送登入資訊，以確認是否為合法客戶端
	client send: <ID number>;Login;<password>
	client rece: <ID number>;<LoginSuccess/LoginFail>[;<Why Fail?>]

==============================================================================

## 5-1 (2)控制端傳輸使用者動作
	client send: {type:"ScreenEvent", to:<ID number>, event:<event type>[, <data key>:<data value>]}

## 5-2 (2)被控端接收使用者動作
	client rece: {type:"ScreenEvent", from:<ID number>, event:<event type>[, <data key>:<data value>]}

## 6-1 (3)控制端請求更新狀態
	client send: {type:"AskUpdate", to:<ID number>, key:<Anything>, value:<Anything>}

## 6-2 (3)被控端接收狀態更新
	client rece: {type:"NeedUpdate", from:<ID number>, key:<Anything>, value:<Anything>}

## 7-1 (3)被控端請求更新狀態
	client send: {type:"AskInform", to:<ID number>, key:<Anything>, value:<Anything>}

## 7-2 (3)控制端接收狀態更新
	client rece: {type:"NeedInform", from:<ID number>, key:<Anything>, value:<Anything>}

===============================================================================

## 8-1 (3)被控端傳輸螢幕畫面
	client send: <ID number>;screen;<screen data>

## 8-2 (3)控制端接收螢幕畫面
	client rece: <ID number>;screen;<screen data>

## 9-1 (3)被控端傳輸聲音
	client send: <ID number>;audio;<audio data>

## 9-2 (3)控制端接收聲音
	client rece: <ID number>;audio;<audio data>

===============================================================================

# 做個簡單類似 SNMP 的功能

## 10-1 (2)控制端請求查詢狀態
	client send: {status:"AskMonitor", to:<ID number>, question:<Anything>}  
	client rece: {status:<"AskMonitorSuccess/AskMonitorFail">, from:<ID number>, question:<Anything>[, answer:<Anything>, reason:<Why Fail?>]}

## 10-2 (2)被控端回復狀態查詢
	client rece: {status:"NeedMonitor", from:<ID number>, question:<Anything>}  
	client send: {status:<"NeedMonitorAccept/NeedMonitorRefuse">, to:<ID number>, question:<Anything>[, answer:<Anything>, reason:<Why Refuse?>]}

===============================================================================

## 11-1 (1)被控端中斷控制，被控端應
	client send: {status:"AbortNeedConn", to:<ID number>}

## 11-2 (1)被控端中斷控制，控制端應
	client rece: {status:"AbortNeedConn", from:<ID number>}

## 12-1 (1)控制端中斷控制，控制端應
	client send: {status:"AbortAskConn", to:<ID number>}

## 12-2 (1)控制端中斷控制，被控端應
	client rece: {status:"AbortAskConn", from:<ID number>}

===============================================================================

## 12 (1)要求伺服器更改客戶端密碼
	client send: {status:"ChangePassword", password:<Password>}  
	client rece: {status:<"ChangePasswordSuccess"/"ChangePasswordFail">[, reason:<Why Fail?>]}

## 13 中斷連線
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

## 14-1 (1)設定密碼永久性
	client send: {status:"SetInfo", key:"pwd_permenant", permenant:<True/False>}  
	client rece: {status:<"SetInfoSuccess"/"SetInfoFail">[, key:"pwd_permenant", reason:<Why Fail?>]}
