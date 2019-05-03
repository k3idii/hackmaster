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


def h0(s):
  f = '═' * len(s)
  print('│  ╔═' + f + '═╗')
  print('├──╢ ' + s + ' ╟')
  print('│  ╚═' + f + '═╝')

def h1(s):
  f = '─' * len(s)
  print('│    ╭─' + f + '─╮')
  print('├────┤ ' + s + ' ├')
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


