#! /usr/bin/python3
#
# (C) 2019 juergen@fabmail.org
#
# This is an upload tool for e.g.
# https://www.sertronics-shop.de/computer/pc-peripheriegeraete/usb-gadgets/led-name-tag-11x44-pixel-usb
# The font_11x44[] data was downloaded from such a device.
#
# Requires:
#  sudo apt-get install python3-usb
#
# Optional for image support:
#  sudo apt-get install python3-pil
#
# v0.1, 2019-03-05, jw  initial draught. HID code is much simpler than expected.
# v0.2, 2019-03-07, jw  support for loading bitmaps added.
# v0.3              jw  option -p to preload graphics for inline use in text.
# v0.4, 2019-03-08, jw  Warning about unused images added. Examples added to the README.
# v0.5,             jw  Deprecated -p and CTRL-characters. We now use embedding within colons(:)
#                       Added builtin icons and -l to list them.
# v0.6, 2019-03-14, jw  Added --mode-help with hints and example for making animations.
#                       Options -b --blink, -a --ants added. Removed -p from usage.

import sys, os, re, time, argparse
from array import array
if sys.platform == "darwin":
  import pyhidapi
else:
  import usb.core

__version = "0.6"

font_11x44 = (
  # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  0x00, 0x38, 0x6c, 0xc6, 0xc6, 0xfe, 0xc6, 0xc6, 0xc6, 0xc6, 0x00,
  0x00, 0xfc, 0x66, 0x66, 0x66, 0x7c, 0x66, 0x66, 0x66, 0xfc, 0x00,
  0x00, 0x7c, 0xc6, 0xc6, 0xc0, 0xc0, 0xc0, 0xc6, 0xc6, 0x7c, 0x00,
  0x00, 0xfc, 0x66, 0x66, 0x66, 0x66, 0x66, 0x66, 0x66, 0xfc, 0x00,
  0x00, 0xfe, 0x66, 0x62, 0x68, 0x78, 0x68, 0x62, 0x66, 0xfe, 0x00,
  0x00, 0xfe, 0x66, 0x62, 0x68, 0x78, 0x68, 0x60, 0x60, 0xf0, 0x00,
  0x00, 0x7c, 0xc6, 0xc6, 0xc0, 0xc0, 0xce, 0xc6, 0xc6, 0x7e, 0x00,
  0x00, 0xc6, 0xc6, 0xc6, 0xc6, 0xfe, 0xc6, 0xc6, 0xc6, 0xc6, 0x00,
  0x00, 0x3c, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3c, 0x00,
  0x00, 0x1e, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0xcc, 0xcc, 0x78, 0x00,
  0x00, 0xe6, 0x66, 0x6c, 0x6c, 0x78, 0x6c, 0x6c, 0x66, 0xe6, 0x00,
  0x00, 0xf0, 0x60, 0x60, 0x60, 0x60, 0x60, 0x62, 0x66, 0xfe, 0x00,
  0x00, 0x82, 0xc6, 0xee, 0xfe, 0xd6, 0xc6, 0xc6, 0xc6, 0xc6, 0x00,
  0x00, 0x86, 0xc6, 0xe6, 0xf6, 0xde, 0xce, 0xc6, 0xc6, 0xc6, 0x00,
  0x00, 0x7c, 0xc6, 0xc6, 0xc6, 0xc6, 0xc6, 0xc6, 0xc6, 0x7c, 0x00,
  0x00, 0xfc, 0x66, 0x66, 0x66, 0x7c, 0x60, 0x60, 0x60, 0xf0, 0x00,
  0x00, 0x7c, 0xc6, 0xc6, 0xc6, 0xc6, 0xc6, 0xd6, 0xde, 0x7c, 0x06,
  0x00, 0xfc, 0x66, 0x66, 0x66, 0x7c, 0x6c, 0x66, 0x66, 0xe6, 0x00,
  0x00, 0x7c, 0xc6, 0xc6, 0x60, 0x38, 0x0c, 0xc6, 0xc6, 0x7c, 0x00,
  0x00, 0x7e, 0x7e, 0x5a, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3c, 0x00,
  0x00, 0xc6, 0xc6, 0xc6, 0xc6, 0xc6, 0xc6, 0xc6, 0xc6, 0x7c, 0x00,
  0x00, 0xc6, 0xc6, 0xc6, 0xc6, 0xc6, 0xc6, 0x6c, 0x38, 0x10, 0x00,
  0x00, 0xc6, 0xc6, 0xc6, 0xc6, 0xd6, 0xfe, 0xee, 0xc6, 0x82, 0x00,
  0x00, 0xc6, 0xc6, 0x6c, 0x7c, 0x38, 0x7c, 0x6c, 0xc6, 0xc6, 0x00,
  0x00, 0x66, 0x66, 0x66, 0x66, 0x3c, 0x18, 0x18, 0x18, 0x3c, 0x00,
  0x00, 0xfe, 0xc6, 0x86, 0x0c, 0x18, 0x30, 0x62, 0xc6, 0xfe, 0x00,

  # 'abcdefghijklmnopqrstuvwxyz'
  0x00, 0x00, 0x00, 0x00, 0x78, 0x0c, 0x7c, 0xcc, 0xcc, 0x76, 0x00,
  0x00, 0xe0, 0x60, 0x60, 0x7c, 0x66, 0x66, 0x66, 0x66, 0x7c, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x7c, 0xc6, 0xc0, 0xc0, 0xc6, 0x7c, 0x00,
  0x00, 0x1c, 0x0c, 0x0c, 0x7c, 0xcc, 0xcc, 0xcc, 0xcc, 0x76, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x7c, 0xc6, 0xfe, 0xc0, 0xc6, 0x7c, 0x00,
  0x00, 0x1c, 0x36, 0x30, 0x78, 0x30, 0x30, 0x30, 0x30, 0x78, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x76, 0xcc, 0xcc, 0x7c, 0x0c, 0xcc, 0x78,
  0x00, 0xe0, 0x60, 0x60, 0x6c, 0x76, 0x66, 0x66, 0x66, 0xe6, 0x00,
  0x00, 0x18, 0x18, 0x00, 0x38, 0x18, 0x18, 0x18, 0x18, 0x3c, 0x00,
  0x0c, 0x0c, 0x00, 0x1c, 0x0c, 0x0c, 0x0c, 0x0c, 0xcc, 0xcc, 0x78,
  0x00, 0xe0, 0x60, 0x60, 0x66, 0x6c, 0x78, 0x78, 0x6c, 0xe6, 0x00,
  0x00, 0x38, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3c, 0x00,
  0x00, 0x00, 0x00, 0x00, 0xec, 0xfe, 0xd6, 0xd6, 0xd6, 0xc6, 0x00,
  0x00, 0x00, 0x00, 0x00, 0xdc, 0x66, 0x66, 0x66, 0x66, 0x66, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x7c, 0xc6, 0xc6, 0xc6, 0xc6, 0x7c, 0x00,
  0x00, 0x00, 0x00, 0x00, 0xdc, 0x66, 0x66, 0x7c, 0x60, 0x60, 0xf0,
  0x00, 0x00, 0x00, 0x00, 0x7c, 0xcc, 0xcc, 0x7c, 0x0c, 0x0c, 0x1e,
  0x00, 0x00, 0x00, 0x00, 0xde, 0x76, 0x60, 0x60, 0x60, 0xf0, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x7c, 0xc6, 0x70, 0x1c, 0xc6, 0x7c, 0x00,
  0x00, 0x10, 0x30, 0x30, 0xfc, 0x30, 0x30, 0x30, 0x34, 0x18, 0x00,
  0x00, 0x00, 0x00, 0x00, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0x76, 0x00,
  0x00, 0x00, 0x00, 0x00, 0xc6, 0xc6, 0xc6, 0x6c, 0x38, 0x10, 0x00,
  0x00, 0x00, 0x00, 0x00, 0xc6, 0xd6, 0xd6, 0xd6, 0xfe, 0x6c, 0x00,
  0x00, 0x00, 0x00, 0x00, 0xc6, 0x6c, 0x38, 0x38, 0x6c, 0xc6, 0x00,
  0x00, 0x00, 0x00, 0x00, 0xc6, 0xc6, 0xc6, 0x7e, 0x06, 0x0c, 0xf8,
  0x00, 0x00, 0x00, 0x00, 0xfe, 0x8c, 0x18, 0x30, 0x62, 0xfe, 0x00,

  # '0987654321^ !"\0$%&/()=?` °\\}][{' + "@ ~ |<>,;.:-_#'+* "
  0x00, 0x7c, 0xc6, 0xce, 0xde, 0xf6, 0xe6, 0xc6, 0xc6, 0x7c, 0x00,
  0x00, 0x7c, 0xc6, 0xc6, 0xc6, 0x7e, 0x06, 0x06, 0xc6, 0x7c, 0x00,
  0x00, 0x7c, 0xc6, 0xc6, 0xc6, 0x7c, 0xc6, 0xc6, 0xc6, 0x7c, 0x00,
  0x00, 0xfe, 0xc6, 0x06, 0x0c, 0x18, 0x30, 0x30, 0x30, 0x30, 0x00,
  0x00, 0x7c, 0xc6, 0xc0, 0xc0, 0xfc, 0xc6, 0xc6, 0xc6, 0x7c, 0x00,
  0x00, 0xfe, 0xc0, 0xc0, 0xfc, 0x06, 0x06, 0x06, 0xc6, 0x7c, 0x00,
  0x00, 0x0c, 0x1c, 0x3c, 0x6c, 0xcc, 0xfe, 0x0c, 0x0c, 0x1e, 0x00,
  0x00, 0x7c, 0xc6, 0x06, 0x06, 0x3c, 0x06, 0x06, 0xc6, 0x7c, 0x00,
  0x00, 0x7c, 0xc6, 0x06, 0x0c, 0x18, 0x30, 0x60, 0xc6, 0xfe, 0x00,
  0x00, 0x18, 0x38, 0x78, 0x18, 0x18, 0x18, 0x18, 0x18, 0x7e, 0x00,
  0x38, 0x6c, 0xc6, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x3c, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x18, 0x3c, 0x3c, 0x3c, 0x18, 0x18, 0x00, 0x18, 0x18, 0x00,
  0x66, 0x66, 0x22, 0x22, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x7c, 0x04, 0x14, 0x18, 0x10, 0x10, 0x20,
  0x10, 0x7c, 0xd6, 0xd6, 0x70, 0x1c, 0xd6, 0xd6, 0x7c, 0x10, 0x10,
  0x00, 0x60, 0x92, 0x96, 0x6c, 0x10, 0x6c, 0xd2, 0x92, 0x0c, 0x00,
  0x00, 0x38, 0x6c, 0x6c, 0x38, 0x76, 0xdc, 0xcc, 0xcc, 0x76, 0x00,
  0x00, 0x00, 0x02, 0x06, 0x0c, 0x18, 0x30, 0x60, 0xc0, 0x80, 0x00,
  0x00, 0x0c, 0x18, 0x30, 0x30, 0x30, 0x30, 0x30, 0x18, 0x0c, 0x00,
  0x00, 0x30, 0x18, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0x18, 0x30, 0x00,
  0x00, 0x00, 0x00, 0x7e, 0x00, 0x00, 0x7e, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x7c, 0xc6, 0xc6, 0x0c, 0x18, 0x18, 0x00, 0x18, 0x18, 0x00,
  0x18, 0x18, 0x10, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x7c, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x7c,
  0x00, 0x10, 0x28, 0x28, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x80, 0xc0, 0x60, 0x30, 0x18, 0x0c, 0x06, 0x02, 0x00, 0x00,
  0x00, 0x70, 0x18, 0x18, 0x18, 0x0e, 0x18, 0x18, 0x18, 0x70, 0x00,
  0x00, 0x3c, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0x0c, 0x3c, 0x00,
  0x00, 0x3c, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x3c, 0x00,
  0x00, 0x0e, 0x18, 0x18, 0x18, 0x70, 0x18, 0x18, 0x18, 0x0e, 0x00,

  # "@ ~ |<>,;.:-_#'+* "
  0x00, 0x00, 0x3c, 0x42, 0x9d, 0xa5, 0xad, 0xb6, 0x40, 0x3c, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xc0, 0xc0, 0x00, 0x00, 0x00,
  0x00, 0x76, 0xdc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x08, 0x08, 0x7c, 0x08, 0x08, 0x18, 0x18, 0x28, 0x28, 0x48, 0x18,
  0x00, 0x18, 0x18, 0x18, 0x18, 0x00, 0x18, 0x18, 0x18, 0x18, 0x00,
  0x00, 0x06, 0x0c, 0x18, 0x30, 0x60, 0x30, 0x18, 0x0c, 0x06, 0x00,
  0x00, 0x60, 0x30, 0x18, 0x0c, 0x06, 0x0c, 0x18, 0x30, 0x60, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x30, 0x30, 0x10, 0x20,
  0x00, 0x00, 0x00, 0x18, 0x18, 0x00, 0x00, 0x18, 0x18, 0x08, 0x10,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x30, 0x30, 0x00,
  0x00, 0x00, 0x00, 0x18, 0x18, 0x00, 0x00, 0x18, 0x18, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0xfe, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff,
  0x00, 0x6c, 0x6c, 0xfe, 0x6c, 0x6c, 0xfe, 0x6c, 0x6c, 0x00, 0x00,
  0x18, 0x18, 0x08, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x18, 0x18, 0x7e, 0x18, 0x18, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x66, 0x3c, 0xff, 0x3c, 0x66, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,

  # "äöüÄÖÜß"
  0x00, 0xcc, 0xcc, 0x00, 0x78, 0x0c, 0x7c, 0xcc, 0xcc, 0x76, 0x00,
  0x00, 0xc6, 0xc6, 0x00, 0x7c, 0xc6, 0xc6, 0xc6, 0xc6, 0x7c, 0x00,
  0x00, 0xcc, 0xcc, 0x00, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0x76, 0x00,
  0xc6, 0xc6, 0x38, 0x6c, 0xc6, 0xfe, 0xc6, 0xc6, 0xc6, 0xc6, 0x00,
  0xc6, 0xc6, 0x00, 0x7c, 0xc6, 0xc6, 0xc6, 0xc6, 0xc6, 0x7c, 0x00,
  0xc6, 0xc6, 0x00, 0xc6, 0xc6, 0xc6, 0xc6, 0xc6, 0xc6, 0x7c, 0x00,
  0x00, 0x3c, 0x66, 0x66, 0x66, 0x7c, 0x66, 0x66, 0x66, 0x6c, 0x60,
)

charmap = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
          'abcdefghijklmnopqrstuvwxyz' + \
          '0987654321^ !"\0$%&/()=?` °\\}][{' + \
          "@ ~ |<>,;.:-_#'+* " + "äöüÄÖÜß"

char_offset = {}
for i in range(len(charmap)):
  char_offset[charmap[i]] = 11 * i

bitmap_preloaded = [ ([],0) ]
bitmaps_preloaded_unused = False

bitmap_named = {
  'ball':    (array('B', (
    0b00000000,
    0b00000000,
    0b00000000,
    0b00000000,
    0b00111100,
    0b11111111,
    0b11111111,
    0b00111100,
    0b00000000,
    0b00000000,
    0b00000000,
    0b00000000
    )), 1, '\x1e'),
  'happy':    (array('B', (0x00, 0x00, 0x3c, 0x42, 0xa5, 0x81, 0xa5, 0x99, 0x42, 0x3c, 0x00)), 1, '\x1d'),
  'happy2':   (array('B', (0x00, 0x08, 0x14, 0x08, 0x01, 0x00, 0x00, 0x61, 0x30, 0x1c, 0x07,
                           0x00, 0x20, 0x50, 0x20, 0x00, 0x80, 0x80, 0x86, 0x0c, 0x38, 0xe0)), 2, '\x1c'),
  'heart':    (array('B', (0x00, 0x00, 0x6c, 0x92, 0x82, 0x82, 0x44, 0x28, 0x10, 0x00, 0x00)), 1, '\x1b'),
  'HEART':    (array('B', (0x00, 0x00, 0x6c, 0xfe, 0xfe, 0xfe, 0x7c, 0x38, 0x10, 0x00, 0x00)), 1, '\x1a'),
  'heart2':   (array('B', (0x00, 0x0c, 0x12, 0x21, 0x20, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01,
                           0x00, 0x60, 0x90, 0x08, 0x08, 0x08, 0x10, 0x20, 0x40, 0x80, 0x00)), 2, '\x19'),
  'HEART2':   (array('B', (0x00, 0x0c, 0x1e, 0x3f, 0x3f, 0x3f, 0x1f, 0x0f, 0x07, 0x03, 0x01,
                           0x00, 0x60, 0xf0, 0xf8, 0xf8, 0xf8, 0xf0, 0xe0, 0xc0, 0x80, 0x00)), 2, '\x18'),
  'fablab':   (array('B', (0x07, 0x0e, 0x1b, 0x03, 0x21, 0x2c, 0x2e, 0x26, 0x14, 0x1c, 0x06,
                           0x80, 0x60, 0x30, 0x80, 0x88, 0x38, 0xe8, 0xc8, 0x10, 0x30, 0xc0)), 2, '\x17'),
  'bicycle':  (array('B', (0x01, 0x02, 0x00, 0x01, 0x07, 0x09, 0x12, 0x12, 0x10, 0x08, 0x07,
                           0x00, 0x87, 0x81, 0x5f, 0x22, 0x94, 0x49, 0x5f, 0x49, 0x80, 0x00,
                           0x00, 0x80, 0x00, 0x80, 0x70, 0xc8, 0x24, 0xe4, 0x04, 0x88, 0x70)), 3, '\x16'),
  'bicycle_r':(array('B', (0x00, 0x00, 0x00, 0x00, 0x07, 0x09, 0x12, 0x13, 0x10, 0x08, 0x07,
                           0x00, 0xf0, 0x40, 0xfd, 0x22, 0x94, 0x49, 0xfd, 0x49, 0x80, 0x00,
                           0x40, 0xa0, 0x80, 0x40, 0x70, 0xc8, 0x24, 0x24, 0x04, 0x88, 0x70)), 3, '\x15'),
  'owncloud': (array('B', (0x00, 0x01, 0x02, 0x03, 0x06, 0x0c, 0x1a, 0x13, 0x11, 0x19, 0x0f,
                           0x78, 0xcc, 0x87, 0xfc, 0x42, 0x81, 0x81, 0x81, 0x81, 0x43, 0xbd,
                           0x00, 0x00, 0x00, 0x80, 0x80, 0xe0, 0x30, 0x10, 0x28, 0x28, 0xd0)), 3, '\x14'),
}
bitmap_builtin = {}
for i in bitmap_named:
  bitmap_builtin[bitmap_named[i][2]] = bitmap_named[i]

def bitmap_char(ch):
  """ Returns a tuple of 11 bytes,
      ch = '_' returns (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255)
      The bits in each byte are horizontal, highest bit is left.
  """
  if ord(ch) < 32:
    if ch in bitmap_builtin:
      return bitmap_builtin[ch][:2]

    global bitmaps_preloaded_unused
    bitmaps_preloaded_unused = False
    return bitmap_preloaded[ord(ch)]

  o = char_offset[ch]
  return (font_11x44[o:o+11],1)


def bitmap_text(text):
  """ returns a tuple of (buffer, length_in_byte_columns_aka_chars)
      We preprocess the text string for substitution patterns
      "::" is replaced with a single ":"
      ":1: is replaced with CTRL-A referencing the first preloaded or loaded image.
      ":happy:" is replaced with a reference to a builtin smiley glyph
      ":heart:" is replaced with a reference to a builtin heart glyph
      ":gfx/logo.png:" preloads the file gfx/logo.png and is replaced the corresponding control char.
  """
  def colonrepl(m):
    name = m.group(1)
    if name == '':
       return ':'
    if name.isdecimal():
      return chr(int(name))
    if '.' in name:
      bitmap_preloaded.append(bitmap_img(name))
      return chr(len(bitmap_preloaded)-1)
    b = bitmap_named[name]
    return b[2]

  text = re.sub(r':([^:]*):', colonrepl, text)
  buf = array('B')
  cols = 0
  for c in text:
    (b,n) = bitmap_char(c)
    buf.extend(b)
    cols += n
  return (buf, cols)


def bitmap_img(file):
  """ returns a tuple of (buffer, length_in_byte_columns)
  """
  from PIL import Image

  im = Image.open(file)
  print("fetching bitmap from file %s -> (%d x %d)" % (file, im.width, im.height))
  if im.height != 11:
    sys.exit("%s: image height must be 11px. Seen %d" % (file, im.height))
  buf = array('B')
  cols = int((im.width+7)/8)
  for col in range(cols):
    for row in range(11):
      byte_val = 0
      for bit in range(8):
        bit_val = 0
        x = 8*col+bit
        if x < im.width and sum(im.getpixel( (x, row) )) > 384:
          bit_val = 1 << (7-bit)
        byte_val += bit_val
      buf.append(byte_val)
  im.close()
  return (buf, cols)


def bitmap(arg):
  """ if arg is a valid and existing path name, we load it as an image.
      Otherwise we take it as a string.
  """
  if os.path.exists(arg):
    return bitmap_img(arg)
  return bitmap_text(arg)


proto_header = (
  0x77, 0x61, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
)

def header(lengths, speeds, modes, blink, ants):
  """ lengths[0] is the number of chars of the first text

      Speeds come in as 1..8, but are needed 0..7 here.
  """
  a = [int(x) for x in re.split(r'[\s,]+', ants)]
  a = a + [a[-1]]*(8-len(a))    # repeat last element

  b = [int(x) for x in re.split(r'[\s,]+', blink)]
  b = b + [b[-1]]*(8-len(b))    # repeat last element

  s = [int(x)-1 for x in re.split(r'[\s,]+', speeds)]
  s = s + [s[-1]]*(8-len(s))    # repeat last element

  m = [int(x) for x in re.split(r'[\s,]+', modes)]
  m = m + [m[-1]]*(8-len(m))    # repeat last element

  h = list(proto_header)
  for i in range(8):
    h[6] += b[i]<<i
    h[7] += a[i]<<i

  for i in range(8):
    h[8+i] = 16*s[i] + m[i]

  for i in range(len(lengths)):
    h[17+2*i] = lengths[i]

  return h


parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='Upload messages or graphics to a 44x11 led badge via USB HID.\nVersion %s from https://github.com/jnweiger/led-badge-44x11\n -- see there for more examples and for updates.' % __version, epilog='Example combining image and text:\n sudo %s "I:HEART2:you"' % sys.argv[0])
parser.add_argument('-s', '--speed', default='4', help="Scroll speed (Range 1..8). Up to 8 comma-seperated values")
parser.add_argument('-m', '--mode',  default='0', help="Up to 8 mode values: Scroll-left(0) -right(1) -up(2) -down(3); still-centered(4); animation(5); drop-down(6); curtain(7); laser(8); See '--mode-help' for more details.")
parser.add_argument('-b', '--blink', default='0', help="1: blinking, 0: normal. Up to 8 comma-seperated values")
parser.add_argument('-a', '--ants',  default='0', help="1: animated border, 0: normal. Up to 8 comma-seperated values")
parser.add_argument('-p', '--preload',  metavar='FILE', action='append', help=argparse.SUPPRESS)       # "Load bitmap images. Use ^A, ^B, ^C, ... in text messages to make them visible. Deprecated, embed within ':' instead")
parser.add_argument('-l', '--list-names', action='version', help="list named icons to be embedded in messages and exit", version=':'+':  :'.join(bitmap_named.keys())+':  ::  or e.g. :path/to/some_icon.png:')
parser.add_argument('message', metavar='MESSAGE', nargs='+', help="Up to 8 message texts with embedded builtin icons or loaded images within colons(:) -- See -l for a list of builtins")
parser.add_argument('--mode-help', action='version', help=argparse.SUPPRESS, version="""

-m 5 "Animation"

 Animation frames are 6 character (or 48px) wide. Upload an animation of
 N frames as one image N*48 pixels wide, 11 pixels high.
 Frames run from left to right and repeat endless.
 Speed [1..8] result in ca. [1.2 1.3 2.0 2.4 2.8 4.5 7.5 15] fps.

 Example of a slowly beating heart:
  sudo %s -s1 -m5 "  :heart2:    :HEART2:"

-m 9 "Smoth"
-m 10 "Rotate"

 These modes are mentioned in the BMP Badge software.
 Text is shown static, or sometimes (longer texts?) not shown at all.
 One significant difference is: The text of the fist message stays visible after
 upload, even if the USB cable remains connected.
 (No "rotation" or "smothering"(?) effect can be expected, though)
""" % sys.argv[0])
args = parser.parse_args()
if sys.platform == "darwin":
  pyhidapi.hid_init()
  devinfo = pyhidapi.hid_enumerate(0x0416, 0x5020)
  #dev = pyhidapi.hid_open(0x0416, 0x5020)
else:
  dev = usb.core.find(idVendor=0x0416, idProduct=0x5020)

if sys.platform == "darwin":
  if devinfo:
    dev = pyhidapi.hid_open_path(devinfo[0].path)
    print("using [%s %s] int=%d page=%s via HIDAPI" % (devinfo[0].manufacturer_string, devinfo[0].product_string, devinfo[0].interface_number, devinfo[0].usage_page))
  else:
    print("No led tag with vendorID 0x0416 and productID 0x5020 found.")
    print("Connect the led tag and run this tool as root.")
    sys.exit(1)
else:
  if dev is None:
    print("No led tag with vendorID 0x0416 and productID 0x5020 found.")
    print("Connect the led tag and run this tool as root.")
    sys.exit(1)
  if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)
  dev.set_configuration()
  print("using [%s %s] bus=%d dev=%d" % (dev.manufacturer, dev.product, dev.bus, dev.address))

if args.preload:
  for file in args.preload:
    bitmap_preloaded.append(bitmap_img(file))
    bitmaps_preloaded_unused = True

msgs = []
for arg in args.message:
  msgs.append(bitmap(arg))

if bitmaps_preloaded_unused == True:
  print("\nWARNING:\n Your preloaded images are not used.\n Try without '-p' or embed the control character '^A' in your message.\n")

buf = array('B')
buf.extend(header(list(map(lambda x: x[1], msgs)), args.speed, args.mode, args.blink, args.ants))

for msg in msgs:
  buf.extend(msg[0])

needpadding = len(buf)%64
if needpadding:
  buf.extend( (0,) * (64-needpadding) )

# print(buf)
for i in range(int(len(buf)/64)):
  time.sleep(0.1)
  if sys.platform == "darwin":
    pyhidapi.hid_write(dev, buf[i*64:i*64+64])
  else:
    dev.write(1, buf[i*64:i*64+64])

if sys.platform == "darwin":
  pyhidapi.hid_close(dev)
