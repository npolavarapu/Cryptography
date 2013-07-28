import urllib2
import sys

TARGET = 'http://crypto-class.appspot.com/po?er='
BLOCK_SIZE = 16
CIPHER = "f20bdba6ff29eed7b046d1df9fb7000058b1ffb4210a580f748b4ac714c001bd4a61044426fb515dad3f21f18aa577c0bdf302936266926ff37dbf7035d5eeb4".decode("hex")
assert len(CIPHER) % BLOCK_SIZE == 0
BLOCKS = [CIPHER[i * BLOCK_SIZE : (i + 1) * BLOCK_SIZE] for i in xrange(len(CIPHER) / BLOCK_SIZE)]
HEX = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "0A", "0B", "0C", "0D", "0E", "0F", "10"]
ZERO_BLOCK = (HEX[0] * BLOCK_SIZE).decode("hex")
PAD_BLOCKS = [(HEX[0] * (BLOCK_SIZE - pad) + HEX[pad] * pad).decode("hex") for pad in xrange(BLOCK_SIZE + 1)]
GUESSES = [chr(i) for i in xrange(256)]
PRINTABLES_INDICES = set([i for i in range(ord("a"), ord("z") + 1) + range(ord("A"), ord("Z") + 1)])
FIRST_GUESSES_INDICES = set(list(PRINTABLES_INDICES) + [ord(" ")] + range(1, 17))
SKIP_GUESSES = set([GUESSES[i] for i in xrange(2)])

def try_guess(cipher):
  target = TARGET + urllib2.quote(cipher.encode("hex"))
  req = urllib2.Request(target)
  try:
    urllib2.urlopen(req)
    assert False # Just to make sure we always get an exception
  except urllib2.HTTPError, e:
    assert (e.code == 404 or e.code == 403)
    return e.code == 404

def strxor(a, b, c = None):
  if c:
    return strxor(strxor(a, b), c)
  assert len(a) == len(b)
  return "".join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a, b)])

def replace_char(string, index, new_char):
  return string[:index] + new_char + string[index + 1:]

def strip_pad(plaintext):
  return plaintext[:-ord(plaintext[-1])]

def guesses():
  for i in FIRST_GUESSES_INDICES:
    yield GUESSES[i]
  for i in xrange(len(GUESSES)):
    if not i in FIRST_GUESSES_INDICES:
      yield GUESSES[i]

def attack_byte(pad, previous_cipher_block, cipher_block, belief):
  byte_index = BLOCK_SIZE - pad
  pad_block = PAD_BLOCKS[pad]
  for guess in guesses():
    if guess in SKIP_GUESSES:
      continue
    new_guess = replace_char(belief, byte_index, guess)
    print "Guess: %s Pad: %s\r" % (new_guess.encode("hex"), pad_block.encode("hex")),
    sys.stdout.flush()
    if try_guess(strxor(new_guess, pad_block, previous_cipher_block) + cipher_block):
      print "\nNew byte detected", guess if ord(guess) in PRINTABLES_INDICES else hex(ord(guess))
      return guess

def attack_block(previous_cipher_block, cipher_block):
  belief = ZERO_BLOCK
  for pad in xrange(1, BLOCK_SIZE + 1):
    res = attack_byte(pad, previous_cipher_block, cipher_block, belief)
    belief = replace_char(belief, BLOCK_SIZE - pad, res)
  return belief

plaintext = ""
for i in reversed(xrange(1, len(BLOCKS))):
  plaintext = attack_block(BLOCKS[i - 1], BLOCKS[i]) + plaintext
  print "Detected:", plaintext
print strip_pad(plaintext)