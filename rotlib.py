import string

alphabet = string.ascii_lowercase
def encode(rot, text):
    result = ""
    for char in text:
        lchar = char.lower()
        if lchar in alphabet:
            if char.isupper():
                result += alphabet[((ord(lchar)-97)+rot) % 26].upper()
                continue
            result += alphabet[((ord(lchar)-97) + rot) % 26]
        else:
            result += char
    return result

