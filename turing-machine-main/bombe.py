from itertools import permutations
from multiprocessing import Pool, Value
import ctypes

ROTOR_WIRINGS = {
    "I":   "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    "II":  "AJDKSIRUXBLHWTMCQGZNPYFVOE",
    "III": "BDFHJLCPRTXVZNYEIWGAKMUSQO",
    "IV":  "ESOVPZJAYQUIRHXLNFTGKDCMWB",
    "V":   "VZBRGITYUPSDNHLXAWMJQOFECK",
}

REFLECTORS = {
    "UKW-A": "EJMZALYXVBWFCRQUONTSPIKHGD",
    "UKW-B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "UKW-C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
}

def l2n(c): return ord(c) - 65
def n2l(n): return chr(n % 26 + 65)

ROTOR_WIRINGS_BACK = {}
for name, wiring in ROTOR_WIRINGS.items():
    back = [''] * 26
    for i, c in enumerate(wiring):
        back[l2n(c)] = n2l(i)
    ROTOR_WIRINGS_BACK[name] = ''.join(back)

def rotor_forward(wiring, letter, pos, ring=0):
    i = (l2n(letter) + pos - ring) % 26
    return n2l(l2n(wiring[i]) - pos + ring)

def rotor_backward(wiring, letter, pos, ring=0):
    i = (l2n(letter) + pos - ring) % 26
    return n2l(l2n(wiring[i]) - pos + ring)

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

def enigma_letter(ch, r1w, r2w, r3w, r1wb, r2wb, r3wb, p1, p2, p3, reflector):
    ch = rotor_forward(r3w,  ch, p3)
    ch = rotor_forward(r2w,  ch, p2)
    ch = rotor_forward(r1w,  ch, p1)
    ch = reflector[l2n(ch)]
    ch = rotor_backward(r1wb, ch, p1)
    ch = rotor_backward(r2wb, ch, p2)
    ch = rotor_backward(r3wb, ch, p3)
    return ch

def decrypt(ciphertext, r_names, r_start, ref_name):
    r1w, r2w, r3w    = [ROTOR_WIRINGS[n]      for n in r_names]
    r1wb, r2wb, r3wb = [ROTOR_WIRINGS_BACK[n] for n in r_names]
    ref = REFLECTORS[ref_name]
    pos = list(r_start)
    out = []
    for ch in ciphertext:
        pos = step_rotors(pos)
        p1, p2, p3 = pos
        out.append(enigma_letter(ch, r1w, r2w, r3w, r1wb, r2wb, r3wb, p1, p2, p3, ref))
    return "".join(out)

def valid_crib_offsets(ciphertext, crib):
    valid = []
    for offset in range(len(ciphertext) - len(crib) + 1):
        window = ciphertext[offset : offset + len(crib)]
        if not any(crib[i] == window[i] for i in range(len(crib))):
            valid.append(offset)
    return valid

counter = None
total_tasks = None

def init_counter(c, t):
    
    global counter, total_tasks
    counter = c
    total_tasks = t

def check_combo(args):
    r_names, ref_name, ciphertext, crib, offsets = args
    results = []
    for r1 in range(26):
        for r2 in range(26):
            for r3 in range(26):
                plain = decrypt(ciphertext, r_names, (r1, r2, r3), ref_name)
                for offset in offsets:
                    if plain[offset : offset + len(crib)] == crib:
                        results.append({
                            "rotors":    r_names,
                            "reflector": ref_name,
                            "start":     (n2l(r1), n2l(r2), n2l(r3)),
                            "offset":    offset,
                            "plaintext": plain,
                        })
                        break

    with counter.get_lock():
        counter.value += 1
        done = counter.value
        total = total_tasks.value
        pct = done / total * 100
        
        print(f"  progress: {pct:.1f}% ({done}/{total})", end="\r", flush=True)

    return results

def bombe(ciphertext, crib, counter=None, total=None):
    crib       = crib.upper().replace(" ", "")
    ciphertext = ciphertext.upper().replace(" ", "")

    offsets      = valid_crib_offsets(ciphertext, crib)
    rotor_combos = list(permutations(ROTOR_WIRINGS.keys(), 3))
    ref_list     = list(REFLECTORS.keys())

    if not offsets:
        return [], offsets

    tasks = [
        (r_names, ref_name, ciphertext, crib, offsets)
        for r_names in rotor_combos
        for ref_name in ref_list
    ]

    if total is not None:
        total.value = len(tasks)

    stops = []
    with Pool(processes=4, initializer=init_counter, initargs=(counter, total)) as pool:
        for result in pool.map(check_combo, tasks):
            stops.extend(result)

    return stops, offsets

if __name__ == "__main__":
    ciphertext = input("ciphertext: ").strip().upper()
    crib       = input("crib: ").strip().upper()

    result = bombe(ciphertext, crib)
    stops, offsets = result if isinstance(result, tuple) else (result, [])

    if not offsets:
        print("crib impossible")
    elif not stops:
        print("no stops found")
    else:
        for i, s in enumerate(stops, 1):
            r = s["rotors"]
            print(f"\nstop #{i}")
            print(f"  rotors    {r[0]}-{r[1]}-{r[2]}")
            print(f"  reflector {s['reflector']}")
            print(f"  plaintext {s['plaintext']}")