#!/usr/bin/python -tt
# -*- coding: utf-8 -*-




try:
  import colorama
except:
  colorama = None

TXT_WAVE=u'·´¯`·.¸¸.'
TXT_BRA    = u' 【'
TXT_KET    = u'】 '
TXT_SMILE  = TXT_BRA + u'ツ' + TXT_KET
TXT_INFO  = TXT_BRA + u'🔎' + TXT_KET
TXT_STEP   = TXT_BRA + u'👣' + TXT_KET
TXT_SAD    = TXT_BRA + u'סּ︵סּ' + TXT_KET
TXT_FLAG   = TXT_BRA + u'⚑' + TXT_KET
TXT_HGLAS  = TXT_BRA + u'⌛'+ TXT_KET

TXT_FINGER  = u'👉'
TXT_B_ARR_R = u'⮕'

log_level = 0

MAX_LINE_LEN = 100

def h0(s):
  _l = len(s)
  f = '═' * _l
  print('│  ╔═' + f + '═╗')
  if _l < MAX_LINE_LEN:
    print('├──╢ ' + s + ' ╟')
  else:
    print('├──╢ ' + s[:MAX_LINE_LEN] + ' ╟')
    for i in range(MAX_LINE_LEN,_l,MAX_LINE_LEN):
      print('│  ║ ' + s[i:i+MAX_LINE_LEN].ljust(' ',MAX_LINE_LEN) + ' ║')
  print('│  ╚═' + f + '═╝')

def h1(s):
  _l = len(s)
  f = '─' * (_l if _l < MAX_LINE_LEN else MAX_LINE_LEN)
  print('│    ╭─' + f + '─╮')
  if _l < MAX_LINE_LEN:
    print('├────┤ ' + s + ' ├')
  else:
    print('├────┤ ' + s[:MAX_LINE_LEN] + ' ├')
    for i in range(MAX_LINE_LEN,_l,MAX_LINE_LEN):
      print('│    │ ' + s[i:i+MAX_LINE_LEN].ljust(MAX_LINE_LEN, ' ') + ' │') 
  print('│    ╰─' + f + '─╯')

def h2(s):
  print('├────╼ ' + s + ' ╾')

def li(s):
  print('  ' + TXT_B_ARR_R + ' ' + s)

def finger(s):
  print('   ' + TXT_FINGER + ' ' + s)

def fail(s):
  print(TXT_SAD + s)

def success(s):
  print(TXT_SMILE + s)

def delay(s):
  print(TXT_HGLAS + s)

def step(s):
  print(TXT_STEP + s)

def info(s):
  print(TXT_INFO + s)

def flag(s):
  print(TXT_FLAG + s)


