import hashlib

def md5load_dictionary(filename):
    with open(filename, "rb") as f:
      passwords = f.readlines()
      return passwords

def md5brute_force(hash, dictionary):
    for word in dictionary:
        if hashlib.md5(word.strip()).hexdigest() == hash:
            return word
    return None
