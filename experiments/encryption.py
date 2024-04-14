def encrypt(text: str, code: int):
    code = str(code * code.bit_length())
    new_text = ""
    for num, i in enumerate(text):
        new_text += chr((ord(i) ^ int(code[num % len(code)])))
    return new_text


def decrypt(text: str, code: int):
    code = str(code * code.bit_length())
    new_text = ""
    for num, i in enumerate(text):
        new_text += chr((ord(i) ^ int(code[num % len(code)])))
    return new_text

def main():
    code = 231312
    msg = "Hello word"
    a = encrypt(msg, code)
    print(a)
    print(solve(a))

def solve(encrypted_text: str):
    # Find repeating patterns in the encrypted text
    patterns = []
    max_pattern_length = len(encrypted_text) // 2
    for i in range(1, max_pattern_length):
        if encrypted_text[:i] == encrypted_text[i:2*i]:
            patterns.append(encrypted_text[:i])

    # If no repeating patterns found, return empty string (decryption failed)
    if not patterns:
        return ""

    # Deduce the length of the code
    code_length = len(patterns[0])

    # Divide the encrypted text into blocks based on the code length
    blocks = [encrypted_text[i:i+code_length] for i in range(0, len(encrypted_text), code_length)]

    # Find the common XOR character for each block
    code = ""
    for block in blocks:
        common_xor = chr(ord(block[0]) ^ ord(block[1]))
        code += common_xor

    # Decrypt the text using the deduced code
    decrypted_text = ""
    for i, char in enumerate(encrypted_text):
        decrypted_text += chr(ord(char) ^ ord(code[i % code_length]))

    return decrypted_text


if __name__ == '__main__':
    main()

