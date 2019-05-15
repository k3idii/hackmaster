from requests.packages.urllib3.contrib import pyopenssl
import subprocess


def get_https_cert(host, port=443, raw=False):
    """Read subject domains in https cert from remote server"""
    if raw:
      return pyopenssl.ssl.get_server_certificate((host, port))
    # else :
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


def _safe_run(arg):
  try:
    return subprocess.check_output(arg, shell=True,)
  except subprocess.CalledProcessError as ex:
    fancy.warn("Subprocess retuned error code 0 !=" + str(ex.returncode))
  return ex.output


def openssl_new_csr(base, subj):
  _safe_run("openssl genrsa -aes256 -passout pass:123456 -out {base}.key_pass 4096".format(base=base))
  _safe_run("openssl rsa -passin pass:123456 -in {base}.key_pass -out {base}.key".format(base=base))
  _safe_run("openssl req -new -key {base}.key -out {base}.csr -subj '{subj}'".format(base=base, subj=subj))
  return dict(
    key = base + ".key",
    csr = base + ".csr",
    crt = base + ".crt",
  )

def openssl_selfsign(base=None, days=1337, openssl_args='', **kw):
  if base is not None:
    kw['csr'] = base + '.csr'
    kw['key'] = base + '.key'
    kw['crt'] = base + '.crt'
  else:
    assert 'csr' not in kw, "Must have CSR or BASE ... "
  _safe_run('openssl x509 -req -days {days} -in {csr} -signkey {key} -out {crt} {a}'.format(
    days = days,
    a = openssl_args,
    **kw
  ))

def openssl_csr_from_crt(crt, key, csr):
  _safe_run('openssl x509 -in {crt} -signkey {key} -x509toreq -out {csr}'.format(
    crt = crt,
    key = key,
    csr = csr,
  ))


def openssl_sign_ca(csr=None, ca_crt=None, ca_key=None, out_crt=None, days=1337, serial=0x31337, openssl_args=''):
  _safe_run("openssl x509 -req -days {d} -in {csr} -CA {ca_crt} -CAkey {ca_key} -out {out_crt} -set_serial {s} {a}".format(
    csr=csr,
    ca_crt = ca_crt,
    ca_key = ca_key,
    out_crt = out_crt,
    d = days,
    s = serial,
    a = openssl_args,
  ))












"""
base_ca = box.mk_path("fakeca")
ssl.openssl_new_csr(hackmaster.safe_run, base=base_ca, subj=subj_str)
ssl.openssl_selfsign(hackmaster.safe_run, base=base_ca)

base_us = box.mk_path("usercert")
ssl.openssl_new_csr(hackmaster.safe_run, base=base_us, subj=subj_str)

ssl.openssl_sign_ca(
  hackmaster.safe_run,
  csr = base_us + ".csr",
  ca_crt = base_ca + ".crt",
  ca_key = base_ca + ".key",
  out_crt = base_us + ".crt",
)

#ssl.openssl_selfsign(hackmaster.safe_run, base=base)
"""

