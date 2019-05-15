


def no_warnings(r):
  r.urllib3.disable_warnings(r.urllib3.exceptions.InsecureRequestWarning)


def _strcmp(a, b):
  return a == b

def like(a, b):
  return a.find(b) >= 0

def ends(a, b):
  return a.endswith(b)


def dns_config_entry(host, target, port=None, target_port=None, match=_strcmp):
  return dict(
    match = match,
    host = host,
    port = port,
    target = target,
    target_port = target_port,
  )


def dirty_static_dns_hook(r,conf=[]):
  print("Making dirty patch ...")

  def _wrp(_f):
    def _prox(self,*a, **kw):
      print("Hammer Time !")
      print(self.host,self.port)
      for pos in conf:
        if not pos['match'](self.host, pos['host']):
          continue ## SKIP 1
        if pos['port'] is not None:
          if pos['port'] != self.port:
            continue ## SKIP 2 
        self.host = pos['target']
        if pos['target_port'] is not None:
          self.port = pos['target_port']
        print("REPLACED !")
        break
      print(self.host,self.port)
      return _f(self, *a, **kw)
    return _prox

  r.urllib3.connection.HTTPConnection._new_conn = _wrp(r.urllib3.connection.HTTPConnection._new_conn)
