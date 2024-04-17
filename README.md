## ILI9225 tft display micropython module
### This module is compatible with <a href="https://github.com/adafruit/micropython-adafruit-rgb-display">adafruit rgb module</a>.
**Note**: This module is tested with ESP8266 and the latest version of micropython(1.22.2) platform.
#### How to use:
```python
import machine
import ili9225 as tft
spi = machine.SPI(1, baudrate=40000000)
disp = tft.ILI9225(spi, cs=machine.Pin(15), dc=machine.Pin(0), rst=machine.Pin(16))
```
#### Example:
```python
import sys
import time
import machine
import ili9225 as tft
import json
import network
import random
import requests

spi = machine.SPI(1, baudrate=40000000)
disp = tft.ILI9225(spi, cs=machine.Pin(15), dc=machine.Pin(0), rst=machine.Pin(16))
wlan = network.WLAN(network.STA_IF)
api = "http://www.mycobit.ir/iexcom.php"

y = 0

def network_connect(wssid,wpass):
  wlan.active(True)
  wlan.connect(wssid,wpass)
  while not wlan.isconnected():
    print (".", end='')
    time.sleep(0.5)

def fetch_coinmap(exchange, assets):
  data = json.dumps({"ex":f"{exchange}","method":"fetch_coinmap","data":{"assets":assets}})
  res = requests.post(api, data=data)
  if res.status_code is 200:
    return json.loads(res.text)
  return {"coins":[],"message":f"code {res.status_code}"}
            
print (sys.version)
fg_color = random.getrandbits(24)
bg_color = tft.COLOR_BLACK
disp.fill(bg_color)

if not wlan.isconnected(): network_connect("****","****")
print (f"\nLocalIP: {wlan.ifconfig()[0]}")
tft.text(disp, f"LocalIP: {wlan.ifconfig()[0]}",x=0,y=y,color=fg_color,background=bg_color)

coins = ["BTC", "ETH", "SOL", "SHIB", "DOGE", "FTM"]
prices = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
fg_color = tft.color565(0xff, 0xff, 0xff)
while True:
  y=8
  i = 0
  result = fetch_coinmap('livecoinwatch',coins)
  if result['message']=="":
    for asset in result['map']:
      y+=10
      price = round(asset['price'],5)
      if price>prices[i]: fg_color = tft.color565(0x00, 0x00, 0xff)
      elif price<prices[i]: fg_color = tft.color565(0x00, 0xff, 0x00)
      else: fg_color = tft.color565(0xff, 0xff, 0xff)
      prices[i] = price
      print (f"{asset['code']}/USDT: {price}")
      tft.text(disp, f"{asset['code']}/USDT: {price}",x=0,y=y,color=fg_color,background=bg_color)
      i += 1
  else:
    print (f"Error: {result['message']}")
    y+=8
    tft.text(disp, f"Error: {result['message']}", x=0, y=y,color=fg_color,background=bg_color)
  time.sleep(5)
```

<center><img src="https://github.com/SajedHashemi/ili9225/blob/main/image.jpg" width="250" /></center>
