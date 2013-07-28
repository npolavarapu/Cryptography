import os
from Crypto.Hash import SHA256

BLOCK_SIZE = 1024
FILE_NAME = "hw3.mp4"

def blocks(f):
  f.seek(0, os.SEEK_END)
  next_block_size = f.tell() % BLOCK_SIZE
  while f.tell() > 0:
    f.seek(-next_block_size, os.SEEK_CUR)
    yield f.read(next_block_size)
    f.seek(-next_block_size, os.SEEK_CUR)
    next_block_size = BLOCK_SIZE

def h0(f):
  last_sha = ""
  for b in blocks(f):
    last_sha = SHA256.new(b + last_sha).hexdigest().decode("hex")
  return last_sha
  
with open(FILE_NAME, "rb") as f:
  print h0(f).encode("hex")