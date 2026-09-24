class EnigmaRotor:

  def __init__(self, wiring, notch, ring_setting=1, position="A"):
    self.wiring = wiring
    self.notch = notch
    self.ring_setting = ring_setting - 1 if isinstance(ring_setting, int) else ord(ring_setting) - 65
    self.position = ord(position) - 65

  def step(self):
    self.position = (self.position + 1) % 26

  def is_at_notch(self):
    return chr(self.position + 65) in self.notch

  def forward(self, c_idx):
    shift = self.position - self.ring_setting
    input_idx = (c_idx + shift) % 26
    out_char = self.wiring[input_idx]
    out_idx = (ord(out_char) - 65 - shift) % 26
    return out_idx

  def backward(self, c_idx):
    shift = self.position - self.ring_setting
    input_idx = (c_idx + shift) % 26
    out_char = chr(input_idx + 65)
    target_idx = self.wiring.index(out_char)
    out_idx = (target_idx - shift) % 26
    return out_idx


class EnigmaMachine:

  def __init__(
      self,
      rotors,
      reflector,
      ring_settings,
      initial_positions,
      plugboard_pairs,
  ):
    # Definisi wiring standar Enigma I
    ROTOR_WIRINGS = {
        "I": ("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q"),
        "II": ("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E"),
        "III": ("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V"),
    }
    REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"

    # Inisialisasi rotor (dari kiri ke kanan)
    self.rotors = []
    for r_name, ring, pos in zip(
        rotors, ring_settings, initial_positions
    ):
      wiring, notch = ROTOR_WIRINGS[r_name]
      self.rotors.append(
          EnigmaRotor(
              wiring, notch, ring_setting=ring, position=pos
          )
      )

    self.reflector = REFLECTOR_B

    # Inisialisasi plugboard
    self.plugboard = {}
    for pair in plugboard_pairs:
      a, b = pair.split("-")
      self.plugboard[a] = b
      self.plugboard[b] = a

  def _step_rotors(self):
    # Urutan rotor: [0]=Kiri (II), [1]=Tengah (III), [2]=Kanan (I)
    r_left, r_middle, r_right = (
        self.rotors[0],
        self.rotors[1],
        self.rotors[2],
    )

    # Mekanisme double stepping Enigma
    middle_at_notch = r_middle.is_at_notch()
    right_at_notch = r_right.is_at_notch()

    if middle_at_notch:
      r_middle.step()
      r_left.step()
      r_right.step()
    elif right_at_notch:
      r_middle.step()
      r_right.step()
    else:
      r_right.step()

  def decrypt_char(self, char):
    if not char.isalpha():
      return char

    self._step_rotors()

    # Pass ke Plugboard
    char = self.plugboard.get(char, char)
    c_idx = ord(char) - 65

    # Forward pass melintasi rotor (Kanan ke Kiri)
    for r in reversed(self.rotors):
      c_idx = r.forward(c_idx)

    # Reflector
    ref_char = self.reflector[c_idx]
    c_idx = ord(ref_char) - 65

    # Backward pass melintasi rotor (Kiri ke Kanan)
    for r in self.rotors:
      c_idx = r.backward(c_idx)

    # Pass balik ke Plugboard
    out_char = chr(c_idx + 65)
    out_char = self.plugboard.get(out_char, out_char)

    return out_char

  def process_text(self, text):
    return "".join(self.decrypt_char(c) for c in text)


# Konfigurasi unik NIM F1D02410012:
# Urutan Rotor (Kanan ke Kiri): I, III, II -> Berarti Kiri ke Kanan: II, III, I
rotors_order = ["II", "III", "I"]
# Ring Setting (Kanan ke Kiri): I, D, Y -> Berarti Kiri ke Kanan: Y, D, I
ring_settings = [25, 4, 9]  # Y=25, D=4, I=9
# Posisi Awal (Kanan ke Kiri): E, T, U -> Berarti Kiri ke Kanan: U, T, E
initial_positions = ["U", "T", "E"]
plugboard = ["K-D", "H-P", "O-Q"]

ciphertext = "ZVFPYYHLFNDJAFHEIKVQXSKEKYNOMUFHHQBLZJJHS"

enigma = EnigmaMachine(
    rotors=rotors_order,
    reflector="B",
    ring_settings=ring_settings,
    initial_positions=initial_positions,
    plugboard_pairs=plugboard,
)

plaintext = enigma.process_text(ciphertext)
print(f"Plaintext Enigma: {plaintext}")
