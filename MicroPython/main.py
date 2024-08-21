import _thread
import utime
from machine import Pin, ADC
import dht, neopixel
from umqtt.simple import MQTTClient
import ujson

# MQTT設置
mq_server = "broker.mqttgo.io"
mq_id = "mqpub_abcdef"
mq_topic_pub = "ntub/jacobian/status"
mq_topic_sub = "ntub/jacobian/command"
mq_user = "my_name"
mq_pwd = "my_password"

# DHT 空氣溫溼度
gpio_dht = 10   
dht_sensor = dht.DHT11(Pin(gpio_dht)) 

# 土壤濕度感測器設定
gpio_soil_moisture = 34  
adc = ADC(Pin(gpio_soil_moisture))
adc.atten(ADC.ATTN_11DB)  # 配置 ADC 的衰減

max_dry = 4095
min_wet = 0

# 水位感測器設定 
gpio_water_level = 35  
adc_water = ADC(Pin(gpio_water_level))
adc_water.atten(ADC.ATTN_11DB)  

# 水位感測器的最大和最小讀數
max_water_level_reading = 4095  # 水位感測器的最大讀數
min_water_level_reading = 0     # 水位感測器的最小讀數
max_water_level_cm = 3.5  # 最大水位高度

# 計算轉換因子
conversion_factor = max_water_level_cm / max_water_level_reading

# 光源感測器設定
gpio_light_sensor = 33
adc_light = ADC(Pin(gpio_light_sensor))
adc_light.atten(ADC.ATTN_11DB) 

max_light_reading = 4095  # 最暗的讀數
min_light_reading = 0     # 最亮的讀數


# 雨滴感測器設定
gpio_rain_drop = 32
adc_rain_drop = ADC(Pin(gpio_rain_drop))
adc_rain_drop.atten(ADC.ATTN_11DB)  


# 紅綠燈設定腳位
red_led = Pin(17, Pin.OUT)  
yellow_led = Pin(3, Pin.OUT)  
green_led = Pin(21, Pin.OUT)


# 初始化LED
pin = Pin(15, Pin.OUT)
num_leds = 8 
np = neopixel.NeoPixel(pin, num_leds)


# 水泵腳位
pump_pin = Pin(5)

# mqClient
mqClient = MQTTClient(mq_id, mq_server, user=mq_user, password=mq_pwd)


# MQTT 消息處理函數
def on_message(topic, msg):
    print("Received message:", topic, msg)
    try:
        data = ujson.loads(msg)
        if data['pump'] == 'on':
            pump_pin.init(Pin.OUT)#開啟馬達
        elif data['pump'] == 'off':
            pump_pin.init(Pin.IN) #關閉馬達
    except Exception as e:
        print("Error:", e)
       
       
# 處理MQTT訊息的線程
def mqtt_thread():
    global mqClient
    mqClient.set_callback(on_message)
    
    while True:
        try:
            mqClient.connect()
            mqClient.subscribe(mq_topic_sub)
            print("Connected to MQTT and subscribed to topic: {}".format(mq_topic_sub))
            break
        except Exception as e:
            print("Failed to connect to MQTT server:", e)
            utime.sleep(3)

    while True:
        mqClient.check_msg()
        utime.sleep(0.5)
        

# 處理傳感器數據的線程
def sensor_thread():
    while True:
        try:
            global mqClient
            
            # 讀取 DHT 感測器
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            hum = dht_sensor.humidity()

            # 讀取土壤濕度感測器
            soil_moisture = adc.read()
            soil_moisture = 100 * (max_dry - soil_moisture) / (max_dry - min_wet)
            
            # 讀取水位感測器
            water_level_raw = adc_water.read()
            water_level_cm = water_level_raw * conversion_factor

            # 計算水位百分比
            water_level_percentage = 100 * (water_level_raw - min_water_level_reading) / (max_water_level_reading - min_water_level_reading)
            
            # 讀取光源感測器
            light_intensity = adc_light.read()
             # 計算光照強度百分比
            light_percentage = 100 * (max_light_reading - light_intensity) / (max_light_reading - min_light_reading)
            
            # 讀取雨滴感測器
            rain_drop_reading = adc_rain_drop.read()
            
            # 紅綠燈控制
            if soil_moisture > 50:
                green_led.on()
                red_led.off()
                yellow_led.off()
            elif soil_moisture >= 25:
                yellow_led.on()
                green_led.off()
                red_led.off()
            else:
                red_led.on()
                green_led.off()
                yellow_led.off()
                
            # 點亮的LED
            num_active_leds = min(int(water_level_cm / max_water_level_cm * num_leds), num_leds)

            for i in range(num_active_leds):
                np[i] = (135, 206, 235)

            for i in range(num_active_leds, num_leds):
                np[i] = (0, 0, 0)

            np.write()
            
            # 整合所有數據
            data = ujson.dumps({
                "temperature": temp,
                "humidity": hum,
                "soil_moisture": int(soil_moisture),
                "water_level_cm": round(water_level_cm, 1),
                "water_level_percentage": int(water_level_percentage),
                "light_percentage": int(light_percentage),
                "rain_drop": rain_drop_reading
            })
            mqClient.publish(mq_topic_pub, data)
            print("Sent data:", data)
        except OSError as e:
            print("Failed to read sensors.", e)
            
        utime.sleep(0.5)  # 暫停 0.5 秒

# 啟動MQTT處理線程
_thread.start_new_thread(mqtt_thread, ())

# 啟動傳感器數據處理線程
_thread.start_new_thread(sensor_thread, ())

# 主線程可以進行其他任務或保持空閒
while True:
    utime.sleep(5)
