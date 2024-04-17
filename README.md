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
import random

spi = machine.SPI(1, baudrate=40000000)
disp = tft.ILI9225(spi, cs=machine.Pin(15), dc=machine.Pin(0), rst=machine.Pin(16))

print (sys.version)
fg_color = random.getrandbits(24)
bg_color = 0xffff
disp.fill(bg_color)

tft.text(disp, "ILI9225 micropython",x=0,y=8,color=fg_color,background=0xffff)
tft.text(disp, "2024/04/18 - 01:15 AM",x=0,y=20,color=fg_color,background=0xffff)
tft.show_bmp(disp, 'bg', center=True, bg_color=bg_color)

```

<center><img src="https://github.com/SajedHashemi/ili9225/blob/main/image.jpg" width="250" /></center>
