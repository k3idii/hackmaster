import pwn
import random
import string
import json
import yaml
import re
from bs4 import BeautifulSoup
import paramiko
import warnings
import argparse
import os
import subprocess
import sys 
import time
import shutil


STAGE_ALL = -1


warnings.filterwarnings(action='ignore',module='.*paramiko.*')
paramiko.util.log_to_file('./paramiko.log')


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

def mkdir_safe(d):
  try:
    os.mkdir(d)
  except Exception as e:
    print("Waring: " + str(e))

def path_here(p):
  return os.path.join(os.path.realpath('./'), p)

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
  cmd = 'xterm  -geometry 50x20 -e "{0}" & '.format(arg)
  print("WILL EXEC:" + cmd)
  os.system(cmd)
  
def html_parse(html):
  return BeautifulSoup(html, "html.parser")

def _dummy_func(*a):
  raise Exception('U haz br0ke IT !')

def extract_text(rex, txt, group=1):
  m = re.search(rex, txt)
  assert m is not None, "Fail to exract : "  + rex 
  return m.group(group)

def pp(**kw):
  print(yaml.safe_dump(kw, default_flow_style=False))

def input_loop(prompt, cb, *a, **kw):
  while True:
    data = raw_input(prompt).strip()
    if data == 'quit':
      break
    if len(data) > 0:
      cb(data, *a , **kw)

def waiting(n):
  sys.stdout.write("Waiting : ")
  while n > 0:
    sys.stdout.write("{0}..".format(n))
    n -= 1
    time.sleep(1)
  sys.stdout.write(' ! \n')

def simple_grep(src, pattern):
  for ln in src.split('\n'):
    if pattern in ln:
      yield ln

class Dumpster(object):
  _dirname = ''
  dont_ask = False

  def __init__(self, name='files'):
    self._dirname = path_here(name)
    mkdir_safe(self._dirname)

  def _mk_path(self, n):
    return os.path.join(self._dirname, n)

  def _continue_override(self, fp, skip=False):
    if os.path.exists(fp):
      if skip:
        return
      print("File exists: " + fp)
      return ask_yn("Override")
    else:
      return True

  def save(self, name=None, data=None, fileobj=None, skip=False):
    if name is None:
      name = random_string(10)
      print("[WARNING]=> will save under random name : " + name)
    fp = self._mk_path(name)
    if not self._continue_override(fp, skip=skip):
      return 
    with open(fp, 'w') as f:
      if data:
        f.write(data)
      if fileobj:
        shutil.copyfileobj(fileobj, f)
    return name

  def read(self, name):
    with open(self._mk_path(name), 'r') as f:
      return f.read()



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

  def fmt(self, s, *a, **kw):
    kw.update(self._d)
    return s.format(*a, **kw)


class ExploitationProcess(object):
  val = None
  args = None
  parser = None
  stage = 0

  def __init__(self):
    self.val = ObjDict(self)
    self.parser = argparse.ArgumentParser()
    self.parser.add_argument('--only_stage', type=int, default=STAGE_ALL, help="Run only selected stage")
    self.parser.add_argument('--start_stage', type=int, default=STAGE_ALL, help="Start from selected stage")
    self.parser.add_argument('--mode', type=str, default='none', help="Launch specific mode")
    self.parser.add_argument('--session', type=str, default='xsession', help="name of session")
    self.parser.add_argument('--format', type=str, default='json', help="format of session")
    self.parser.add_argument('--dont', action='store_true', default=False, help="Don't as. Assume YES for all questions.")


  def parse_args(self):
    self.args = self.parser.parse_args()

  def start(self):
    self.parse_args()
    try:
      self.restore()
    except Exception as ex:
      pwn.log.warn("Fail to restore state : {0!r}".format(ex))
    self.store()

  def next_stage(self, s):
    print(self.fmt('=== === [ STAGE:{_stage} # '+s+' ] === ===', _stage=self.stage))
    enter_stage = True
    #if self.args.start_stage > STAGE_ALL:
    enter_stage = self.args.start_stage <= self.stage
    if self.args.only_stage > STAGE_ALL:
      enter_stage = self.args.only_stage == self.stage 
    self.stage += 1
    if not enter_stage:
      print('         < SKIP > - ')
    return enter_stage

  def substage(self, s):
    print(self.fmt(' >>> '+s+' <<<'))

  def _pfmt(self, s, **kw):
    print(self.val.fmt(s, **kw))

  def win(self, s, **kw):
    self._pfmt(" ++ " + s, **kw )

  def fail(self, s, **kw):
    self._pfmt(' !! ' + s, **kw )

  def step(self, s, **kw):
    self._pfmt(' ** ' + s, **kw )

  def info(self, s, **kw):
    self._pfmt(' ii ' + s, **kw )

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
      print(" > Set: {0} = {1}".format(k, v))

  def eval_if_dont_have(self, **kw):
    self.eval(skip=True, **kw)

  def extract(self, src='', **kw):
    for k, ex in kw.items():
      v = extract_text(ex, src)
      setattr(self.val, k, v)
      print(" > Extracted: {0} = {1}".format(k, v))

  def _confirm(self, prompt):
    if self.args.dont: # explicit don't ask
      return True 
    return ask_yn(prompt)

  def run(self, s, bg=False, ask=True):
    cmd = self.val.fmt(s)
    print('---------------------------------')
    print('COMMAND: \n ' + cmd )
    print('---------------------------------')

    if bg:
      if self._confirm("EXECUTE IN BACKGOURND"):
        return run_bg(cmd)
    # else 
    if self._confirm("EXECUTE"):
      return subprocess.check_output(cmd, shell=True)
    else:
      raise Exception('Y U not exec ?')


'''

Debug::*::* "true";
Debug::RunScripts "true";


'''

