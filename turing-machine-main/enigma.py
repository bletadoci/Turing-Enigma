plugboard = {
    'A': 'M', 'M': 'A',
    'B': 'Z', 'Z': 'B',
    'C': 'R', 'R': 'C',
    'D': 'T', 'T': 'D',
    'E': 'K', 'K': 'E',
    'F': 'L', 'L': 'F',
    'G': 'X', 'X': 'G',
    'H': 'W', 'W': 'H',
    'I': 'U', 'U': 'I',
    'J': 'N', 'N': 'J',
    'O': 'P', 'P': 'O',
    'Q': 'S', 'S': 'Q',
    'Y': 'V', 'V': 'Y',
}

rotor_I   = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
rotor_II  = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
rotor_III = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
reflector = "YRUHQSLDPXNGOKMIEBFZCWVJAT"

def letter_to_num(c):
    return ord(c) - ord('A')

def num_to_letter(n):
    return chr(n % 26 + ord('A'))

def rotor_forward(wiring, letter, rotor_position):
    shifted_input = (letter_to_num(letter) + rotor_position) % 26
    wired_output = letter_to_num(wiring[shifted_input])
    real_output = wired_output - rotor_position
    return num_to_letter(real_output)

def rotor_backward(wiring, letter, rotor_position):
    shifted_input = (letter_to_num(letter) + rotor_position) % 26
    wiring_as_numbers = []
    for c in wiring:
        wiring_as_numbers.append(letter_to_num(c))
    position_in_wiring = wiring_as_numbers.index(shifted_input)
    real_output = position_in_wiring - rotor_position
    return num_to_letter(real_output)

def enigma(letter, r1_pos, r2_pos, r3_pos):
    letter = plugboard.get(letter, letter)
    letter = rotor_forward(rotor_III, letter, r3_pos)
    letter = rotor_forward(rotor_II,  letter, r2_pos)
    letter = rotor_forward(rotor_I,   letter, r1_pos)
    letter = reflector[letter_to_num(letter)]
    letter = rotor_backward(rotor_I,   letter, r1_pos)
    letter = rotor_backward(rotor_II,  letter, r2_pos)
    letter = rotor_backward(rotor_III, letter, r3_pos)
    letter = plugboard.get(letter, letter)
    return letter

def encode_message(message):
    encoded = ""
    r1_pos = 0
    r2_pos = 0
    r3_pos = 0
    for letter in message:
        encoded += enigma(letter, r1_pos, r2_pos, r3_pos)
        r3_pos += 1
        if r3_pos == 26:
            r3_pos = 0
            r2_pos += 1
        if r2_pos == 26:
            r2_pos = 0
            r1_pos += 1
    return encoded

message = input("Enter message: ").upper()
print(encode_message(message))