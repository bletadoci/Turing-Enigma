import tkinter as tk
from tkinter import ttk, messagebox
from enigma_ui_logic import (letter_to_num, num_to_letter,
                    rotor_forward, rotor_backward,
                    enigma_step, step_rotors)

ROTORS = {
    "I":   {"wiring": "EKMFLGDQVZNTOWYHXUSPAIBRCJ"},
    "II":  {"wiring": "AJDKSIRUXBLHWTMCQGZNPYFVOE"},
    "III": {"wiring": "BDFHJLCPRTXVZNYEIWGAKMUSQO"},
    "IV":  {"wiring": "ESOVPZJAYQUIRHXLNFTGKDCMWB"},
    "V":   {"wiring": "VZBRGITYUPSDNHLXAWMJQOFECK"},
}

REFLECTORS = {
    "UKW-A": "EJMZALYXVBWFCRQUONTSPIKHGD",
    "UKW-B": "YRUHQSLDPXNGOKMIEBFZCWVJAT",
    "UKW-C": "FVPJIAOYEDRZXWGCTKUQSBNMHL",
}


class EnigmaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Enigma Machine — Wehrmacht / Luftwaffe")
        self.configure(bg="#1a1008")
        self.resizable(False, False)

        self.plugboard = {}
        self.plugboard_pairs = []
        self.positions = [0, 0, 0]
        self.initial_positions = [0, 0, 0]

        self.font_mono  = ("Courier New", 11, "bold")
        self.font_label = ("Georgia", 9, "italic")
        self.font_key   = ("Courier New", 13, "bold")
        self.font_small = ("Courier New", 9)
        self.font_seg   = ("Courier New", 28, "bold")

        self._build_ui()
        self._refresh_rotor_display()

    def _build_ui(self):
        title_frame = tk.Frame(self, bg="#1a1008")
        title_frame.pack(fill="x", padx=16, pady=(14, 2))
        tk.Label(title_frame, text="  ENIGMA  ", font=("Georgia", 22, "bold"),
                 fg="#d4a017", bg="#1a1008").pack()
        tk.Label(title_frame, text="Wehrmacht · Luftwaffe  |  Schlüsselmaschine",
                 font=("Georgia", 9, "italic"), fg="#9a7a3a", bg="#1a1008").pack()

        tk.Frame(self, height=2, bg="#6b4f1a").pack(fill="x", padx=12, pady=4)

        content = tk.Frame(self, bg="#1a1008")
        content.pack(padx=12, pady=4)

        left = tk.Frame(content, bg="#1a1008")
        left.pack(side="left", padx=6, anchor="n")
        right = tk.Frame(content, bg="#1a1008")
        right.pack(side="left", padx=6, anchor="n")

        self._build_rotor_section(left)
        self._build_plugboard_section(left)
        self._build_lampboard(right)
        self._build_keyboard(right)
        self._build_io_section(right)

    def _build_rotor_section(self, parent):
        f = self._panel(parent, "ROTORS & REFLECTOR")
        f.pack(fill="x", pady=(0, 8))

        g = tk.Frame(f, bg="#2a1e0a")
        g.pack(fill="x")

        for col, txt in enumerate(["", "Left", "Middle", "Right"]):
            tk.Label(g, text=txt, font=("Georgia", 8, "italic"),
                     fg="#9a7a3a", bg="#2a1e0a", width=8).grid(row=0, column=col, padx=4, pady=2)

        rotor_names = list(ROTORS.keys())
        self.rotor_vars = [tk.StringVar(value="I"), tk.StringVar(value="II"), tk.StringVar(value="III")]
        tk.Label(g, text="Walze", font=self.font_label, fg="#c8a84b", bg="#2a1e0a").grid(row=1, column=0, sticky="e", padx=6)
        for i, var in enumerate(self.rotor_vars):
            cb = ttk.Combobox(g, textvariable=var, values=rotor_names,
                              width=5, state="readonly", font=self.font_mono)
            cb.grid(row=1, column=i+1, padx=4, pady=3)
            self._style_combo(cb)

        self.ring_vars = [tk.StringVar(value="A"), tk.StringVar(value="A"), tk.StringVar(value="A")]
        self.pos_vars  = [tk.StringVar(value="A"), tk.StringVar(value="A"), tk.StringVar(value="A")]

        self.ref_var = tk.StringVar(value="UKW-B")
        tk.Label(g, text="UKW", font=self.font_label, fg="#c8a84b", bg="#2a1e0a").grid(row=2, column=0, sticky="e", padx=6)
        ref_cb = ttk.Combobox(g, textvariable=self.ref_var, values=list(REFLECTORS.keys()),
                              width=7, state="readonly", font=self.font_mono)
        ref_cb.grid(row=2, column=1, padx=4, pady=3, columnspan=2, sticky="w")
        self._style_combo(ref_cb)

        pos_frame = tk.Frame(f, bg="#2a1e0a")
        pos_frame.pack(pady=(6, 2))
        tk.Label(pos_frame, text="Current:", font=self.font_label, fg="#9a7a3a", bg="#2a1e0a").pack(side="left")
        self.pos_display = tk.Label(pos_frame, text="A A A", font=self.font_seg,
                                    fg="#f5c518", bg="#2a1e0a", width=8)
        self.pos_display.pack(side="left", padx=6)

        tk.Button(f, text="↺  Reset Positions", command=self._reset_positions,
                  font=self.font_small, bg="#3d2a0a", fg="#c8a84b",
                  activebackground="#5a3d10", activeforeground="#f5c518",
                  relief="flat", bd=0, cursor="hand2", padx=8, pady=3).pack(pady=(2, 6))

    def _build_plugboard_section(self, parent):
        f = self._panel(parent, "STECKERBRETT (PLUGBOARD)")
        f.pack(fill="x", pady=(0, 8))

        inp = tk.Frame(f, bg="#2a1e0a")
        inp.pack(fill="x", padx=8, pady=4)

        tk.Label(inp, text="Pair:", font=self.font_label, fg="#c8a84b", bg="#2a1e0a").pack(side="left")
        self.plug_a = ttk.Combobox(inp, values=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                                   width=4, state="readonly", font=self.font_mono)
        self.plug_a.pack(side="left", padx=4)
        self._style_combo(self.plug_a)

        tk.Label(inp, text="↔", font=("Courier New", 14), fg="#d4a017", bg="#2a1e0a").pack(side="left")

        self.plug_b = ttk.Combobox(inp, values=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                                   width=4, state="readonly", font=self.font_mono)
        self.plug_b.pack(side="left", padx=4)
        self._style_combo(self.plug_b)

        tk.Button(inp, text="Add", command=self._add_plug,
                  font=self.font_small, bg="#3d2a0a", fg="#c8a84b",
                  activebackground="#5a3d10", relief="flat", bd=0,
                  cursor="hand2", padx=8, pady=2).pack(side="left", padx=6)
        tk.Button(inp, text="Clear All", command=self._clear_plugboard,
                  font=self.font_small, bg="#3d0a0a", fg="#e05050",
                  activebackground="#5a1010", relief="flat", bd=0,
                  cursor="hand2", padx=8, pady=2).pack(side="left", padx=2)

        self.plug_display = tk.Frame(f, bg="#2a1e0a")
        self.plug_display.pack(fill="x", padx=8, pady=4)
        self._refresh_plugboard_display()

    def _build_lampboard(self, parent):
        f = self._panel(parent, "LAMPENFELD (LAMPBOARD)")
        f.pack(fill="x", pady=(0, 6))

        self.lamps = {}
        for row_letters in ["QWERTZUIO", "ASDFGHJK", "PYXCVBNML"]:
            row_f = tk.Frame(f, bg="#2a1e0a")
            row_f.pack(pady=2)
            offset = (9 - len(row_letters)) * 14
            tk.Frame(row_f, width=offset, bg="#2a1e0a").pack(side="left")
            for letter in row_letters:
                lbl = tk.Label(row_f, text=letter, width=3, height=1,
                               font=("Courier New", 12, "bold"),
                               fg="#4a3a1a", bg="#1e160a", relief="flat", bd=1)
                lbl.pack(side="left", padx=2, pady=2)
                self.lamps[letter] = lbl

    def _light_lamp(self, letter):
        for k, lbl in self.lamps.items():
            lbl.configure(fg="#4a3a1a", bg="#1e160a")
        if letter and letter in self.lamps:
            self.lamps[letter].configure(fg="#1a1008", bg="#f5c518")

    def _build_keyboard(self, parent):
        f = self._panel(parent, "TASTATUR (KEYBOARD)")
        f.pack(fill="x", pady=(0, 6))

        for row_letters in ["QWERTZUIO", "ASDFGHJK", "PYXCVBNML"]:
            row_f = tk.Frame(f, bg="#2a1e0a")
            row_f.pack(pady=2)
            offset = (9 - len(row_letters)) * 14
            tk.Frame(row_f, width=offset, bg="#2a1e0a").pack(side="left")
            for letter in row_letters:
                tk.Button(row_f, text=letter, width=3, height=1,
                          font=self.font_key, fg="#f5e6b0", bg="#3d2f10",
                          activebackground="#c8a84b", activeforeground="#1a1008",
                          relief="raised", bd=2, cursor="hand2",
                          command=lambda l=letter: self._key_press(l)).pack(side="left", padx=2, pady=2)

        ctrl_f = tk.Frame(f, bg="#2a1e0a")
        ctrl_f.pack(pady=(4, 2))
        tk.Button(ctrl_f, text="SPACE", width=8, font=self.font_small,
                  fg="#f5e6b0", bg="#3d2f10", activebackground="#c8a84b",
                  activeforeground="#1a1008", relief="raised", bd=2, cursor="hand2",
                  command=self._type_space).pack(side="left", padx=4)
        tk.Button(ctrl_f, text="⌫ DEL", width=8, font=self.font_small,
                  fg="#e05050", bg="#3d1010", activebackground="#c05050",
                  activeforeground="#fff", relief="raised", bd=2, cursor="hand2",
                  command=self._backspace).pack(side="left", padx=4)

        self.bind("<Key>", self._on_key)
        self.focus_set()

    def _build_io_section(self, parent):
        f = self._panel(parent, "MESSAGE")
        f.pack(fill="x", pady=(0, 6))

        for label, attr in [("Input:", "input_text"), ("Output:", "output_text")]:
            row = tk.Frame(f, bg="#2a1e0a")
            row.pack(fill="x", padx=8, pady=3)
            tk.Label(row, text=label, font=self.font_label, fg="#9a7a3a",
                     bg="#2a1e0a", width=7, anchor="w").pack(side="left")
            txt = tk.Text(row, height=2, width=32, font=("Courier New", 11),
                          bg="#0f0c05", fg="#f5c518", insertbackground="#f5c518",
                          relief="flat", bd=2, wrap="word", state="disabled")
            txt.pack(side="left", fill="x", expand=True)
            setattr(self, attr, txt)
            if attr == "output_text":
                tk.Button(row, text="copy", font=self.font_small,
                          bg="#2a1e0a", fg="#9a7a3a",
                          activebackground="#3d2a0a", activeforeground="#f5c518",
                          relief="flat", bd=0, cursor="hand2",
                          command=self._copy_output).pack(side="left", padx=6)

        btn_row = tk.Frame(f, bg="#2a1e0a")
        btn_row.pack(pady=4)
        tk.Button(btn_row, text="⟳ Reset All", command=self._full_reset,
                  font=self.font_small, bg="#3d1010", fg="#e05050",
                  activebackground="#5a1010", relief="flat", bd=0,
                  cursor="hand2", padx=10, pady=3).pack(side="left", padx=4)

    def _panel(self, parent, title):
        outer = tk.Frame(parent, bg="#6b4f1a", bd=1, relief="flat")
        outer.pack(fill="x", pady=3)
        inner = tk.Frame(outer, bg="#2a1e0a", padx=8, pady=6)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        tk.Label(inner, text=title, font=("Georgia", 8, "bold italic"),
                 fg="#9a7a3a", bg="#2a1e0a").pack(anchor="w", pady=(0, 4))
        return inner

    def _style_combo(self, cb):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TCombobox",
                        fieldbackground="#f5e6b0",
                        background="#3d2f10",
                        foreground="black",
                        selectbackground="#c8a84b",
                        selectforeground="black")
        cb.configure(style="TCombobox")

    def _get_rotor_wirings(self):
        return [ROTORS[v.get()]["wiring"] for v in self.rotor_vars]

    def _get_rings(self):
        return [letter_to_num(v.get()) for v in self.ring_vars]

    def _reset_positions(self):
        self.positions = [letter_to_num(v.get()) for v in self.pos_vars]
        self.initial_positions = list(self.positions)
        self._refresh_rotor_display()

    def _refresh_rotor_display(self):
        p = self.positions
        self.pos_display.configure(
            text=f"{num_to_letter(p[0])} {num_to_letter(p[1])} {num_to_letter(p[2])}")

    def _add_plug(self):
        a = self.plug_a.get().strip().upper()
        b = self.plug_b.get().strip().upper()
        if not a or not b:
            messagebox.showwarning("Plugboard", "Select both letters.")
            return
        if a == b:
            messagebox.showwarning("Plugboard", "Cannot connect a letter to itself.")
            return
        if a in self.plugboard or b in self.plugboard:
            messagebox.showwarning("Plugboard", "One of those letters is already connected.")
            return
        if len(self.plugboard_pairs) >= 13:
            messagebox.showwarning("Plugboard", "Maximum 13 pairs reached.")
            return
        self.plugboard[a] = b
        self.plugboard[b] = a
        self.plugboard_pairs.append((a, b))
        self._refresh_plugboard_display()

    def _clear_plugboard(self):
        self.plugboard.clear()
        self.plugboard_pairs.clear()
        self._refresh_plugboard_display()

    def _refresh_plugboard_display(self):
        for w in self.plug_display.winfo_children():
            w.destroy()
        for i, (a, b) in enumerate(self.plugboard_pairs):
            pf = tk.Frame(self.plug_display, bg="#1a1008", relief="flat", bd=1)
            pf.grid(row=i // 5, column=i % 5, padx=3, pady=2)
            tk.Label(pf, text=f"{a}↔{b}", font=self.font_mono,
                     fg="#f5c518", bg="#1a1008", padx=4).pack(side="left")
            tk.Button(pf, text="✕", font=("Courier New", 8),
                      fg="#e05050", bg="#1a1008", activebackground="#3d0a0a",
                      relief="flat", bd=0, cursor="hand2",
                      command=lambda x=a, y=b: self._remove_plug(x, y)).pack(side="left")
        if not self.plugboard_pairs:
            tk.Label(self.plug_display, text="No connections", font=self.font_small,
                     fg="#5a4a2a", bg="#2a1e0a").grid(row=0, column=0)

    def _remove_plug(self, a, b):
        self.plugboard.pop(a, None)
        self.plugboard.pop(b, None)
        self.plugboard_pairs = [(x, y) for (x, y) in self.plugboard_pairs if x != a]
        self._refresh_plugboard_display()

    def _key_press(self, letter):
        self.positions = step_rotors(self.positions)
        out = enigma_step(letter, self._get_rotor_wirings(), self.positions,
                          self._get_rings(), REFLECTORS[self.ref_var.get()], self.plugboard)
        self._append_text(self.input_text, letter)
        self._append_text(self.output_text, out)
        self._light_lamp(out)
        self._refresh_rotor_display()

    def _on_key(self, event):
        ch = event.char.upper()
        if ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            self._key_press(ch)
        elif event.keysym == "space":
            self._type_space()
        elif event.keysym == "BackSpace":
            self._backspace()

    def _type_space(self):
        self._append_text(self.input_text, " ")
        self._append_text(self.output_text, " ")
        self._light_lamp(None)

    def _backspace(self):
        for txt in (self.input_text, self.output_text):
            txt.configure(state="normal")
            if txt.get("1.0", "end-1c"):
                txt.delete("end-2c", "end-1c")
            txt.configure(state="disabled")
        self._light_lamp(None)

    def _append_text(self, widget, char):
        widget.configure(state="normal")
        widget.insert("end", char)
        widget.see("end")
        widget.configure(state="disabled")

    def _copy_output(self):
        self.output_text.configure(state="normal")
        text = self.output_text.get("1.0", "end-1c")
        self.output_text.configure(state="disabled")
        self.clipboard_clear()
        self.clipboard_append(text)

    def _full_reset(self):
        for txt in (self.input_text, self.output_text):
            txt.configure(state="normal")
            txt.delete("1.0", "end")
            txt.configure(state="disabled")
        self._reset_positions()
        self._light_lamp(None)


if __name__ == "__main__":
    app = EnigmaApp()
    app.mainloop()