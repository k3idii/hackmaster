#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import random
import string
import json
import yaml
import re
import readline

import argparse
import os
import subprocess
import sys
import time
import shutil



from . import fancy

STAGE_ALL = -1


## UI

def _ask_user(prompt, options):
  opts = '|'.join(options)
  while True:
    print("{0} ? [{1}]".format(prompt, opts))
    tmp = raw_input().strip()
    if tmp in options:
      return tmp
    else:
      print("WTF !?")

def ask_yn(prompt):
  return 'y' == _ask_user(prompt, ['y','n'])

def query(prompt):
  return raw_input(prompt).strip()

def show_elements(collection):
  for el in collection:
    fancy.li(repr(el))

def input_loop(prompt, cb, *a, **kw):
  while True:
    data = raw_input(prompt).strip()
    if data == 'quit':
      break
    if len(data) > 0:
      cb(data, *a , **kw)

def waiting(n):
  sys.stdout.write(fancy.TXT_HGLAS + "Waiting : ")
  while n > 0:
    sys.stdout.write("{0}..".format(n))
    sys.stdout.flush()
    n -= 1
    time.sleep(1)
  sys.stdout.write(' ! \n')

# MISC

def my_ip(pattern="10\.10\.[1-9]"):
  return os.popen("ip a | grep '"+pattern+"' | head -n 1 | sed 's/.*inet //;s/... brd.*//'").read().strip()

## PATH

def mkdir_safe(d):
  d = os.path.realpath(d)
  try:
    os.mkdir(d)
  except Exception as e:
    fancy.warn("MKDIR:" + str(e))
  return d


def path_here(p):
  return os.path.join(os.path.realpath('./'), p)

## RANDOMS

def random_string(size, src=None):
  if src is None:
    src = string.ascii_uppercase + string.digits
  return ''.join(random.choice(src) for _ in xrange(size))

class RandStr(object):
  sec = ''
  def __init__(self, src):
    self.src = src 
  def __format__(self, size):
    try:
      size = int(size)
    except:
      size = 10
    return ''.join(random.choice(self.src) for _ in xrange(size))

def rand_fmt(s, src=string.ascii_lowercase, **kw):
  return s.format(r=RandStr(src), **kw)

def run_bg(arg):
  uuid = random_string(20)
  cmd = 'xterm  -geometry 50x20 -e "echo {0}; {1}; read X" & '.format(uuid, arg)
  print("WILL EXEC:" + cmd)
  r = os.system(cmd)
  return uuid

def safe_run(arg):
  try:
    return subprocess.check_output(arg, shell=True,)
  except subprocess.CalledProcessError as ex:
    fancy.warn("Subprocess retuned error code 0 !=" + str(ex.returncode))
  return ex.output


  
def extract_text(rex, txt, group=1, multiline=True):
  m = re.search(rex, txt, flags=((re.DOTALL|re.MULTILINE) if multiline else 0) )
  assert m is not None, "Fail to exract : "  + rex 
  return m.group(group)

def between(txt, mark1, mark2):
  p1 = txt.find(mark1) + len(mark1)
  p2 = txt.rfind(mark2)
  return txt[p1:p2]

def pp(**kw):
  print(yaml.safe_dump(kw, default_flow_style=False))


def gen_grep(src, regex=False, *patterns):
  if regex:
    for ln in src.split('\n'):
      for p in patterns:
        if re.search(p, ln) is not None:
          yield ln
  else:
    for ln in src.split('\n'):
      if p in patterns:
        if p in ln:
          yield ln


def simple_grep(src, pattern, do_print=False):
  r = []
  for _ln in gen_grep(src, pattern):
    r.append(_ln)
    if do_print:
      print(_ln)
  return r


## FILE STORAGE 

class Dumpster(object):
  _dirname = ''
  dont_ask = False

  def __init__(self, name='files'):
    self._dirname = path_here(name)
    mkdir_safe(self._dirname)

  def mk_path(self, n):
    return os.path.join(self._dirname, n)

  def chmod(self, n, mode):
    p = self.mk_path(n)
    os.chmod(p,mode)

  def _continue_override(self, fp, skip=False):
    if os.path.exists(fp):
      fancy.finger("File exists: " + fp)
      if self.dont_ask:
        return True
      if skip:
        return False
      return ask_yn("Override")
    else:
      return True

  def exists(self, name):
    fp = self.mk_path(name)
    return os.path.exists(fp)

  def save(self, name=None, data=None, fileobj=None, skip=False, return_full_path=False, chmod=None):
    if name is None:
      name = random_string(10)
      print("[WARNING]=> will save under random name : " + name)
    fp = self.mk_path(name)
    if not self._continue_override(fp, skip=skip):
      return 
    with open(fp, 'w') as f:
      if data:
        f.write(data)
      if fileobj:
        shutil.copyfileobj(fileobj, f)
    if chmod is not None:
      os.chmod(fp, chmod)
    if return_full_path:
      return fp
    else:
      return name

  def read(self, name):
    with open(self.mk_path(name), 'r') as f:
      return f.read()

## MAGIC
class MagicStatement(object):

  def __init__(self, obj, prop, val1, val2=None):
    self._obj = obj
    self._prop = prop
    self._val = val1
    if val2 is not None:
      self._old_val = val2 
    else:
      self._old_val = getattr(self._obj, self._prop)

  def __enter__(self):
    setattr(self._obj, self._prop, self._val)

  def __exit__(self, type, value, traceback):
    setattr(self._obj, self._prop, self._old_val)


class ObjDict(object):
  _d = {}

  def __init__(self, parent):
    self._parent = parent
    self._d = {}
  
  def __setattr__(self, k, v):
    if k.startswith('_'):
      self.__dict__[k] = v 
    else:
      self._d[k] = v
      self._parent.store()
  
  def __getattr__(self, k):
    assert k in self._d, "I have no value for " + k
    return self._d.get(k, None)

  def fmt(self, s, do_print=False, **kw):
    kw.update(self._d)
    r = s.format(**kw)
    if do_print:
      print(r)
    return r

  def save(self, k, v):
    setattr(self, k, v)



def _dummy_func(*a, **kw):
  raise Exception('U haz br0ke IT !')

def _gen_prn(f):
  def _func(self,s, **kw):
    f(self.fmt(s, **kw))
  return _func

class ExploitationProcess(object):
  val = None
  args = None
  parser = None
  stage = 0

  def __init__(self):
    self.val = ObjDict(self)
    self.parser = argparse.ArgumentParser()
    self.parser.add_argument('--only_stage', type=int, default=STAGE_ALL, help="Run only selected stage")
    self.parser.add_argument('--start', type=int, default=STAGE_ALL, dest='start_stage', help="Start from selected stage")
    self.parser.add_argument('--mode', type=str, default='none', help="Launch specific mode")
    self.parser.add_argument('--session', type=str, default='xsession', help="name of session")
    self.parser.add_argument('--format', type=str, default='json', help="format of session")
    self.parser.add_argument('--dont', action='store_true', default=False, help="Don't as. Assume YES for all questions.")
    self.parser.add_argument('--clear', default=False, action='store_true', help='CLEAR session data')

  def parse_args(self):
    self.args = self.parser.parse_args()

  def start(self):
    self.parse_args()
    if self.args.clear:
      fancy.info("CLEARING SESSION !")
    else:
      try:
        self.restore()
      except Exception as ex:
        fancy.fail("Fail to restore state : {0!r}".format(ex))
    self.store()
    if self.args.start_stage != STAGE_ALL:
      fancy.info("Will start from stage : " + str(self.args.start_stage))

  def next_stage(self, s):
    fancy.h0(self.fmt('STAGE:{_stage} # {_txt}', _stage=self.stage, _txt=s))
    enter_stage = True
    #if self.args.start_stage > STAGE_ALL:
    enter_stage = self.args.start_stage <= self.stage
    if self.args.only_stage > STAGE_ALL:
      enter_stage = self.args.only_stage == self.stage 
    self.stage += 1
    if not enter_stage:
      fancy.info("Skipping ...")
    return enter_stage

  substage = _gen_prn(fancy.h1)
  win      = _gen_prn(fancy.success)
  fail     = _gen_prn(fancy.fail)
  info     = _gen_prn(fancy.info)
  step     = _gen_prn(fancy.step)
  warn     = _gen_prn(fancy.warn)

  def _session_fn(self):
    return '{0:s}.{1:s}'.format(self.args.session, self.args.format)

  def _call_fuc(self, name, *a, **kw):
    return getattr(self, name, _dummy_func)(*a, **kw)

  def _pack_yaml(self):
    return yaml.safe_dump(self.val._d)
  
  def _pack_json(self):
    return json.dumps(self.val._d)

  def _unpack_yaml(self, d):
    self.val._d = yaml.safe_load(d)

  def _unpack_json(self, d):
    self.val._d = json.loads(d)

  def store(self):
    data = self._call_fuc('_pack_{0:s}'.format(self.args.format))
    with open(self._session_fn(), 'w') as f:
      f.write(data)    
  
  def restore(self):
    with open(self._session_fn(), 'r') as f:
      data = f.read()
    self._call_fuc('_unpack_{0:s}'.format(self.args.format), data)

  def have(self, *a):
    for k in a:
      if k not in self.val._d:
        return False
    return True
  
  def dont_have(self, *a):
    return not self.have(*a)

  def fmt(self, s, **kw):
    return self.val.fmt(s, **kw)

  def eval(self, skip=False, **kw):
    for k, fmt in kw.items():
      if skip and k in self.val._d:
        continue
      v = self.val.fmt(fmt)
      setattr(self.val, k, v)
      fancy.finger("Set: {0} = {1} ... ".format(k, repr(v)[:20]))

  def eval_if_dont_have(self, **kw):
    self.eval(skip=True, **kw)

  def extract(self, src='', silent=False, multiline=True, **kw):
    for k, ex in kw.items():
      v = extract_text(ex, src, multiline=multiline)
      setattr(self.val, k, v)
      if not silent:
        fancy.finger('Extracted: {0} = {1}'.format(k, v))

  def _confirm(self, prompt):
    if self.args.dont: # explicit don't ask
      return True 
    return ask_yn(prompt)

  def dont_ask(self, assume=True):
    return MagicStatement(self.args, 'dont', True)

  def run(self, s, bg=False, ask=True):
    cmd = self.val.fmt(s)
    fancy.h1("COMMAND: " + cmd)
    if bg:
      if self._confirm("EXECUTE IN BACKGOURND"):
        return run_bg(cmd)
      else:
        return self.warn("Not executing !")
    if self._confirm("EXECUTE"):
      return safe_run(cmd)
    else:
      return self.warn('Y U not exec ?')









