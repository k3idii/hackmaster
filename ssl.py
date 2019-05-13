from requests.packages.urllib3.contrib import pyopenssl

def get_https_cert(host, port):
    """Read subject domains in https cert from remote server"""
    return pyopenssl.OpenSSL.crypto.load_certificate(
        pyopenssl.OpenSSL.crypto.FILETYPE_PEM,
        pyopenssl.ssl.get_server_certificate((host, port))
    )

def get_subj_from_cert(c):
  return c.get_subject().get_components()

def get_field_from_subj(c, f):
  r = []
  for k,v in c.get_subject().get_components():
    if f=='*' or k.lower() == f.lower():
      r.append(v)
  return r


def get_sni(c):
  r = []
  n = c.get_extension_count()
  for i in range(n):
    e = c.get_extension(i)
    if e.get_short_name() == 'subjectAltName':
      return str(e)
