import network
import utime

wifi_ssid = "..."
wifi_password = "..."

wifi = network.WLAN(network.STA_IF)

try:
    wifi.active(False)
    wifi.active(True)
    wifi.connect(wifi_ssid, wifi_password) 
    print("開始連接WiFi")
    for i in range(20):
        print("嘗試於{}秒內連接WiFi".format(i))
        utime.sleep(1)
        if wifi.isconnected():
            break
    if wifi.isconnected():
        print("WiFi連接成功！")
        print("網路配置=", wifi.ifconfig())
    else:
        print("WiFi連接錯誤")
except Exception as e:
    print(e)