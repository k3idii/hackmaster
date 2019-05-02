""" Extra IO Objects wrapper. Usefull for binary-level parsing/building """

import struct
import os
import binascii
import StringIO

NULLBYTE = '\x00'

DO_SAVE_POS = 1
NO_SAVE_POS = 2

def unpack_ex(fmt, data, into=None):
  size = struct.calcsize(fmt)
  if len(data) < size:
    raise Exception("unpack_ex: too few bytes to unpack !")
  parts = struct.unpack(fmt, data)
  if not parts:
    return None
  if not into:
    return parts
  if len(parts) > len(into):
    raise Exception("unpack_ex: too many values unpacked !")
  return dict((into[i], parts[i]) for i in range(len(parts)))

def debug_reads(obj):
  def _dbg_read(self, n):
    print("Try to read {0} bytes ...".format(n))
    result = self._real_io.read(n)
    print(" ... and got {0} bytes : [{1}] ".format(n,repr(result)))
    return result
  obj.read = _dbg_read

def debug_writes(obj):
  def _dbg_write(self, data):
    print("Try to write {0} bytes [{1}]".format(len(data), repr(data)))
    return self._real_io.write(data)
  obj.read = _dbg_write

class ExIO(object):
  _jump_stack = None
  _real_io = None
  endian = "<"

  def __init__(self, real_io=None, from_string=None):
    self._jump_stack = list()
    if from_string is not None:
      real_io = StringIO.StringIO(from_string)
    self._real_io = real_io

  def __getattr__(self, name):
    return getattr(self._real_io, name)


  def _pack(self, fmt, *a, **kw):
    return struct.pack(self.endian + fmt , *a , **kw)

  def _unpack(self, fmt, *a, **kw):
    return struct.unpack(self.endian + fmt, *a, **kw)

  def w8(self, v):
    return self.write(self._pack("B", v))

  def w16(self, v):
    return self.write(self._pack("H", v))
  
  def w32(self, v):
    return self.write(self._pack("I", v))
    
  def w64(self, v):
    return self.write(self._pack("Q", v))

  def write_len_str(self, s):
    self.w8(len(s))
    self.write(s)

  def read(self, n):
    return self._real_io.read(n)
  
  def tell(self):
    return self._real_io.tell()
    
  def write(self, s):
    return self._real_io.write(s)

  def g_read_till(self, b):
    while True:
      c = self.read(1)
      if c == b:
        return
      yield c

  def read_till(self, b, include=False):
    s = []
    for c in self.g_read_till(b):
      s.append(c)
    if include:
      s.append(b)
    return ''.join(s)

  def read_n(self, n, context=''):
    d = self.read(n)
    #assert len(d) == n
    if not d or len(d) < n:
      raise Exception("Read error : need %d bytes, got %d (%s)" % (n, len(d), context))
    return d

  def read_fmt(self, fmt="", into=None):
    sz = struct.calcsize(fmt)
    d = self.read_n(sz)
    return unpack_ex(fmt, d, into)

  def read_one_fmt(self, fmt):
    sz = struct.calcsize(fmt)
    d = self.read_n(sz)
    if len(d) != sz:
      raise Exception("To few bytes to read {0}".format(fmt))
    val = struct.unpack(fmt, d)
    if val:
      return val[0]
    else:
      return None

  def read_the_rest(self):
    n = self.available_bytes()
    return self.read_n(n)

  def append(self, data): #
    p = self.tell()
    self.seek(0, os.SEEK_END)
    self.write(data)
    self.seek(p)

  def append_fmt(self, fmt, *a):
    return self.append(struct.pack(fmt, *a))

  def write_fmt(self, fmt, *a):
    return self.write(struct.pack(fmt, *a))

  def fprintf(self, fmt, *a, **kw):
    self.write(fmt.format(*a, **kw))

  def read_all(self):
    p = self.tell()
    self.seek(0)
    v = self.read(0xffff)
    self.seek(p)
    return v

  def dump(self):
    return self.getvalue()

  def available_bytes(self):
    org = self.tell()
    self.seek(0, os.SEEK_END)
    end = self.tell()
    self.seek(org)
    return end - org

  def get_pos(self):
    return self.tell()

  def push_pos(self):
    self._jump_stack.append(self.tell())

  def pop_pos(self, restore_position=False):
    if restore_position:
      self.seek(self._jump_stack.pop(), os.SEEK_SET)
    else:
      self._jump_stack.pop()

  def goto(self, pos, save=DO_SAVE_POS):  ## x.goto(10, DO_SAVE_POS)
    if save == DO_SAVE_POS:
      self.push_pos()
    self.seek(pos, os.SEEK_SET)

  def g_chunk(self, chunk_size=8, yield_pos=True, number_of_chunks=-1):
    while number_of_chunks == -1 or number_of_chunks > 0:
      pos = self.tell()
      chunk = self.read(chunk_size)
      if yield_pos:
        yield pos, chunk
      else:
        yield chunk
      if len(chunk) != chunk_size:
        return
      if number_of_chunks >0:
        number_of_chunks -= 1
  
  def g_hexdump(self, row_size=16, max_bytes=0, row_printer=None, offset_fmt=None, hex_sep=' ', asc_sep='', non_ascii_char='.'):
    n_chunks = -1
    spare_bytes = 0
    if max_bytes > 0:
      n_chunks = max_bytes / row_size
      spare_bytes = max_bytes % row_size
    def _def_r_p(a,b,c):
      return " | ".join(a,b,c)

    def _def_o_f(a):
      return str(a)

    if row_printer is None:
      row_printer = _def_r_pw

    if offset_fmt is None:
      offset_fmt = _def_o_f

    for pos, chunk in self.g_chunk(row_size, yield_pos=True, number_of_chunks=n_chunks):
      hex_chunk = hex_sep.join([binascii.hexlify(i) for i in chunk])
      asc_chunk = asc_sep.join([i if 32 <= ord(i) < 128 else non_ascii_char for i in chunk])
      yield row_printer(offset_fmt(pos), asc_chunk, hex_chunk)
    if spare_bytes:
      pos = self.tell()
      chunk =  self.read(spare_bytes)
      hex_chunk = hex_sep.join([binascii.hexlify(i) for i in chunk])
      asc_chunk = asc_sep.join([i if 32 <= ord(i) < 128 else non_ascii_char for i in chunk])
      yield row_printer(offset_fmt(pos), asc_chunk, hex_chunk)

  def hexdump(self, row_size=16, max_bytes=0, title=None, head=True, rewind=False, non_ascii_char='.', col_sep="|", return_array=False, hex_sep=' ', asc_sep='', offset_bits=32):
    rows = []
    num_chunks = -1
    if rewind:
      self.goto(0, DO_SAVE_POS)
    asc_el_size = 1 + len(asc_sep)
    hex_el_size = 2 + len(hex_sep)
    offset_bits = 2 * offset_bits / 8

    def print1(off_str, asc_str, hex_str):
      return ("{cs} {0: ^"+str(2+offset_bits)+"} {cs} {1: <" + str(asc_el_size * row_size) + "} {cs} {2: <" + str(hex_el_size * row_size) + "}").format(off_str,asc_str,hex_str, cs=col_sep)
    
    def format1(off):
      return ("0x{0:0>"+str(offset_bits)+"X}").format(off)
 
    if head:
      if title:
        rows.append(" .--[ {0} ]-----".format(title))
      rows.append(print1("OFFSET","ASCII","HEX"))
    for hex_chunk in self.g_hexdump(row_size=row_size, max_bytes=max_bytes, row_printer=print1, offset_fmt=format1, hex_sep=hex_sep, asc_sep=asc_sep, non_ascii_char=non_ascii_char):
      rows.append(hex_chunk)
    rows.append("{cs} {0} {cs} <EOF>".format(format1(self.tell()), cs=col_sep))
    if rewind:
      self.pop_pos(restore_position=True)
    if return_array:
      return rows
    return '\n'.join(rows)

if __name__ == '__main__':
  import sys
  print ExIO(open(sys.argv[0],'r')).hexdump(max_bytes=42)



