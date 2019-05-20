

def log(s):
  print("(╯°□°) ︻╦╤─   -{IMPLANT : " + s)

class Implantator(object):

  source_dir = None
  remote_dir = None

  def __init__(self, src, dst):
    self.source_dir = src
    self.remote_dir = dst


  def _generate_pairs(self):
    pass

  def via_sftp(host, port, user, password=None, key=None):
    from . import ssh
    con = None
    if key is None:
      if password is None:
        raise Exception("R U from the past ?!")
      else:
        log("sftp pssword login")
        con = ssh.transport_by_pass((host, port), user, password)
    else:
      log("sftp key login")
      con = ssh.transport_by_key((host,port), user, key)
    sftp = ssh.do_sftp(con)




