#!/usr/bin/python -tt
# -*- coding: utf-8 -*-


try:
  import colorama
except:
  colorama = None

TXT_WAVE=u'·´¯`·.¸¸.'
TXT_BRA    = u' 【'
TXT_KET    = u'】 '
TXT_SMILE  =          u' \(ツ)/'
TXT_INFO  = TXT_BRA + u'🔎' + TXT_KET
TXT_STEP   = TXT_BRA + u'👣' + TXT_KET
TXT_SAD    = TXT_BRA + u'סּ︵סּ' + TXT_KET
TXT_FLAG   = TXT_BRA + u'⚑' + TXT_KET
TXT_HGLAS  = TXT_BRA + u'⌛'+ TXT_KET
TXT_WARN   = u' (╯°□°）'

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

def box(s,title=None):
  _l = len(s)
  f = '─' * MAX_LINE_LEN


  if title is None:
    print('  ╭─' + f + '─╮')
  else:
    lt = len(title)
    if lt + 5 > MAX_LINE_LEN:
      title = title[MAX_LINE_LEN - 5] + '...'
    title = '┤  ' + title + '  ├'
    title = title + ('─' * (MAX_LINE_LEN - len(title) + 4 ) )
    print('  ╭─' + title + '─╮')
  for i in range(0,_l,MAX_LINE_LEN):
    print('  │ ' + s[i:i+MAX_LINE_LEN].ljust(MAX_LINE_LEN, ' ') + ' │') 
  print('  ╰─' + f + '─╯')


def h2(s):
  print('├────╼ ' + s + ' ╾')

def li(s):
  print('  ' + TXT_B_ARR_R + ' ' + s)

def finger(s):
  print('   ' + TXT_FINGER + '  ' + s)

def fail(s):
  print(TXT_SAD + s)

def success(s):
  print(TXT_SMILE + '  ' + s)

def delay(s):
  print(TXT_HGLAS + s)

def step(s):
  print(TXT_STEP + s)

def info(s):
  print(TXT_INFO + s)

def flag(s):
  print(TXT_FLAG + s)

def warn(s):
  print(TXT_WARN + s)


