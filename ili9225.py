import ustruct
from rgb import DisplaySPI, color565
import framebuf

# ILI9225 screen size
ILI9225_TFTWIDTH  = 176
ILI9225_TFTHEIGHT = 220

COLOR_BLACK   = 0x0000
COLOR_BLUE    = 0x001F
COLOR_RED     = 0xF800
COLOR_GREEN   = 0x07E0
COLOR_CYAN    = 0x07FF
COLOR_MAGENTA = 0xF81F
COLOR_YELLOW  = 0xFFE0
COLOR_WHITE   = 0xFFFF

class ILI9225(DisplaySPI):
  """
  A simple driver for the ILI9225 displays.


  >>> import ili9225
  >>> from machine import Pin, SPI
  >>> spi = SPI(mosi=Pin(13), sck=Pin(14))
  >>> display = ili9225.ILI9225(spi, cs=Pin(15), dc=Pin(12), rst=Pin(16))
  >>> display.fill(ili9225.color565(0xff, 0x11, 0x22))
  >>> display.pixel(120, 160, 0)
  """
    
  _COLUMN_SET = 0x20
  _PAGE_SET = 0x21
  _RAM_WRITE = 0x22
  _RAM_READ = 0x22
  _INIT = (
    (0x10, b'\x00\x00'), # set SAP,DSTB,STB
    (0x11, b'\x00\x00'), # set APON,PON,AON,VCI1EN,VC
    (0x12, b'\x00\x00'), # set BT,DC1,DC2,DC3
    (0x13, b'\x00\x00'), # set GVDD
    (0x14, b'\x00\x00'), # set VCOMH/VCOML voltage
    (0x11, b'\x00\x18'), # set APON, PON, AON, VCI1EN, VC
    (0x12, b'\x61\x21'), # set BT, DC1, DC2, DC3
    (0x13, b'\x00\x6F'), # set GVDD   /*007F 0088 */
    (0x14, b'\x49\x5F'), # set VCOMH/VCOML voltage
    (0x10, b'\x08\x00'), # set SAP, DSTB, STB
    (0x11, b'\x10\x3B'), # set APON, PON, AON, VCI1EN, VC
    (0x01, b'\x01\x1C'), # set the display line number and display direction
    (0x02, b'\x01\x00'), # set 1 line inversion
    (0x03, b'\x10\x30'), # set GRAM write direction and BGR=1.
    (0x07, b'\x00\x00'), # Display off
    (0x08, b'\x08\x08'), # set the back porch and front porch
    (0x0B, b'\x11\x00'), # set the clocks number per line
    (0x0C, b'\x00\x00'), # CPU interface
    (0x0F, b'\x0D\x01'), # set Osc  /*0e01*/
    (0x15, b'\x00\x20'), # set VCI recycling
    (0x20, b'\x00\x00'), # RAM Address
    (0x21, b'\x00\x00'), # RAM Address
    (0x30, b'\x00\x00'),
    (0x31, b'\x00\xDB'),
    (0x32, b'\x00\x00'),
    (0x33, b'\x00\x00'),
    (0x34, b'\x00\xDB'),
    (0x35, b'\x00\x00'),
    (0x36, b'\x00\xAF'),
    (0x37, b'\x00\x00'),
    (0x38, b'\x00\xDB'),
    (0x39, b'\x00\x00'),
    (0x50, b'\x00\x00'),
    (0x51, b'\x08\x08'),
    (0x52, b'\x08\x0A'),
    (0x53, b'\x00\x0A'),
    (0x54, b'\x0A\x08'),
    (0x55, b'\x08\x08'),
    (0x56, b'\x00\x00'),
    (0x57, b'\x0A\x00'),
    (0x58, b'\x07\x10'),
    (0x59, b'\x07\x10'),
    (0x07, b'\x00\x12'),
    (0x07, b'\x10\x17')
  )
  _ENCODE_PIXEL = ">H"
  _ENCODE_POS = ">HH"
  _DECODE_PIXEL = ">BBB"

  def __init__(self, spi, dc, cs, rst=None, width=ILI9225_TFTWIDTH, height=ILI9225_TFTHEIGHT):
    super().__init__(spi, dc, cs, rst, width, height)
    self._scroll = 0
  
  def scroll(self, dy=None):
    if dy is None:
      return self._scroll
    self._scroll = (self._scroll + dy) % self.height
    self._write(0x31, ustruct.pack('>H', self._scroll))

def text(display, text, x=0, y=0, color=0xffff, background=0x0000):
  x = min(display.width - 1, max(0, x))
  y = min(display.height - 1, max(0, y))
  w = display.width - x
  h = min(display.height - y, 8)
  buffer = bytearray(display.width * h * 2)
  fb = framebuf.FrameBuffer(buffer, w, h, framebuf.RGB565)
  for line in text.split('\n'):
    fb.fill(background)
    fb.text(line, 0, 0, color)
    display.blit_buffer(buffer, x, y, w, h)
    y += 8;
    if y >= display.height:
      break
      
def show_bmp(display, filename, x=0, y=0, center=False, bg_color=0xffff):
  def lebytes_to_int(bytes):
    n = 0x00
    while len(bytes) > 0:
      n <<= 8
      n |= bytes.pop()
    return int(n)
  
  def color565(r, g, b):
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3

  with open(f"{filename}.bmp", 'rb') as f:
    img_bytes = list(bytearray(f.read(38)))  
    assert img_bytes[0:2] == [66, 77], "Not a valid BMP file"
    assert lebytes_to_int(img_bytes[30:34]) == 0, "Compression is not supported"
    assert lebytes_to_int(img_bytes[28:30]) == 24, "Only 24-bit colour depth is supported"

    start_pos = lebytes_to_int(img_bytes[10:14])
    end_pos = start_pos + lebytes_to_int(img_bytes[34:38])

    width = lebytes_to_int(img_bytes[18:22])
    height = lebytes_to_int(img_bytes[22:26])
    
    f.seek(start_pos)
    
    if center:
      x = (ILI9225_TFTWIDTH // 2) - (width // 2)
      y = (ILI9225_TFTHEIGHT // 2) - (height // 2)
    
    for col in range((height+y), y ,-1):
      img_bytes = list(bytearray(f.read(width*3)))
      for row in range((width+x), x, -1):
        color = color565(img_bytes.pop(),img_bytes.pop(),img_bytes.pop())
        if color != bg_color:
          display.pixel(row,col, color)

