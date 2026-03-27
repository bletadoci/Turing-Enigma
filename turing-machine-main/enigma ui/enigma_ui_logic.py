ROTOR_WIRINGS = {
    "I":   "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    "II":  "AJDKSIRUXBLHWTMCQGZNPYFVOE",
    "III": "BDFHJLCPRTXVZNYEIWGAKMUSQO",
    "IV":  "ESOVPZJAYQUIRHXLNFTGKDCMWB",
    "V":   "VZBRGITYUPSDNHLXAWMJQOFECK",
}

def letter_to_num(c):
    return ord(c) - ord('A')

def num_to_letter(n):
    return chr(n % 26 + ord('A'))

def rotor_forward(wiring, letter, rotor_position, ring=0):
    shifted_input = (letter_to_num(letter) + rotor_position - ring) % 26
    wired_output = letter_to_num(wiring[shifted_input])
    real_output = wired_output - rotor_position + ring
    return num_to_letter(real_output)

def rotor_backward(wiring, letter, rotor_position, ring=0):
    shifted_input = (letter_to_num(letter) + rotor_position - ring) % 26
    wiring_as_numbers = [letter_to_num(c) for c in wiring]
    position_in_wiring = wiring_as_numbers.index(shifted_input % 26)
    real_output = position_in_wiring - rotor_position + ring
    return num_to_letter(real_output)

def step_rotors(positions):
    p1, p2, p3 = positions
    p3 += 1
    if p3 == 26:
        p3 = 0
        p2 += 1
    if p2 == 26:
        p2 = 0
        p1 += 1
    if p1 == 26:
        p1 = 0
    return [p1, p2, p3]

def enigma_step(letter, rotor_wirings, positions, rings, reflector_str, plugboard_dict):
    r1, r2, r3 = rotor_wirings
    p1, p2, p3 = positions
    ring1, ring2, ring3 = rings
    letter = plugboard_dict.get(letter, letter)
    letter = rotor_forward(r3, letter, p3, ring3)
    letter = rotor_forward(r2, letter, p2, ring2)
    letter = rotor_forward(r1, letter, p1, ring1)
    letter = reflector_str[letter_to_num(letter)]
    letter = rotor_backward(r1, letter, p1, ring1)
    letter = rotor_backward(r2, letter, p2, ring2)
    letter = rotor_backward(r3, letter, p3, ring3)
    letter = plugboard_dict.get(letter, letter)
    return letter