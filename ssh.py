import paramiko
import warnings
import time
import subprocess


warnings.filterwarnings(action='ignore',module='.*paramiko.*')
paramiko.util.log_to_file('./paramiko.log')


def transport_by_pass(target, u, p):
  conn = paramiko.Transport(target)
  conn.connect(username=u, password=p)
  return conn

def transport_by_key(target, user, keyfile):
  conn = paramiko.Transport(target)
  k = paramiko.RSAKey.from_private_key_file(keyfile)
  conn.connect(username=user, pkey=k)
  return conn

def do_sftp(conn):
  return paramiko.SFTPClient.from_transport(conn)


def interactive(target, user, keyfile=None, password=None):
  client = paramiko.SSHClient()
  client.set_missing_host_key_policy(paramiko.WarningPolicy)
  if keyfile is not None:
    k = paramiko.RSAKey.from_private_key_file(keyfile)
    client.connect(target[0], port=target[1], username=user, pkey=k)
    return client
  else:
    client.connect(target[0], port=target[1], username=user, password=password)
    return client

def just_exec(con, cmd):
  _, stdout, _ = con.exec_command(cmd)
  return stdout.read()

def chan_read_untill(chan, wait_for='$'):
  b = ''
  while True:
    tmp = chan.recv(1024)
    b += tmp
    if wait_for in tmp:
      break
  return b

class SSHShell(object):

  def __init__(self, connection, prompt):
    self.sleep_time = 0.3
    self.prompt = prompt
    self._chan = connection.invoke_shell()
    time.sleep(self.sleep_time*3)
    self.banner = chan_read_untill(self._chan, self.prompt)

  def run(self, cmd, stdin=None, parse=True, only_result=False):
    if not cmd.endswith("\n"):
      cmd = cmd + '\n'
    self._chan.send(cmd)
    time.sleep(self.sleep_time)
    if stdin:
      self._chan.send(stdin)
    time.sleep(self.sleep_time)
    r = chan_read_untill(self._chan, self.prompt)
    if not parse:
      return r
    ln1 = r.find("\n")
    ln2 = r.rfind("\n")
    retval = (r[:ln1].strip(), r[ln1:ln2].strip(), r[ln2:].strip())
    if only_result:
      return retval[1]
    else:
      return retval


  def su(self, password, new_prompt):
    if not password.endswith("\n"):
      password = password + '\n'
    self.prompt = new_prompt
    r = self.run(
      cmd = "su",
      stdin = password,
    )
    return r






def ssh_genkey(outfile,passphrase=''):
  cmd = 'ssh-keygen -f {_f} -P "{_p}"'.format(
    _f=outfile,
    _p=passphrase,
  )
  print(cmd)
  subprocess.check_output(cmd, shell=1)






