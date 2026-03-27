import tkinter as tk
from tkinter import ttk
import threading
import ctypes
from multiprocessing import Value
import bombe

class BombeUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Bombe Machine")
        self.geometry("720x520")
        self.configure(bg="#1a1008")
        self.resizable(False, False)

        self.font_title = ("Georgia", 20, "bold")
        self.font_label = ("Georgia", 9, "italic")
        self.font_text  = ("Courier New", 11)
        self.font_btn   = ("Courier New", 10, "bold")

        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="  BOMBE  ",
                 font=self.font_title,
                 fg="#d4a017", bg="#1a1008").pack(pady=(12, 2))

        tk.Frame(self, height=2, bg="#6b4f1a").pack(fill="x", padx=12, pady=6)

        panel = self._panel("INPUT")
        panel.pack(fill="x", padx=12, pady=6)

        tk.Label(panel, text="Ciphertext",
                 font=self.font_label,
                 fg="#c8a84b", bg="#2a1e0a").pack(anchor="w")

        self.cipher_entry = tk.Entry(panel,
                                     font=self.font_text,
                                     bg="#0f0c05", fg="#f5c518",
                                     insertbackground="#f5c518",
                                     relief="flat")
        self.cipher_entry.pack(fill="x", pady=4)

        tk.Label(panel, text="Crib",
                 font=self.font_label,
                 fg="#c8a84b", bg="#2a1e0a").pack(anchor="w")

        self.crib_entry = tk.Entry(panel,
                                   font=self.font_text,
                                   bg="#0f0c05", fg="#f5c518",
                                   insertbackground="#f5c518",
                                   relief="flat")
        self.crib_entry.pack(fill="x", pady=4)

        self.pct_label = tk.Label(panel, text="0.0%",
                                  font=("Courier New", 9),
                                  fg="#c8a84b", bg="#2a1e0a")
        self.pct_label.pack(anchor="w")
        self.progress = ttk.Progressbar(panel, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=4)

        self.run_btn = tk.Button(panel, text="RUN BOMBE",
                  command=self.run_bombe,
                  font=self.font_btn,
                  bg="#3d2a0a", fg="#f5c518",
                  activebackground="#5a3d10",
                  activeforeground="#1a1008",
                  relief="flat", bd=0,
                  cursor="hand2",
                  padx=10, pady=4)
        self.run_btn.pack(pady=6)

        out_panel = self._panel("OUTPUT")
        out_panel.pack(fill="both", expand=True, padx=12, pady=6)

        self.output = tk.Text(out_panel,
                              font=self.font_text,
                              bg="#0f0c05", fg="#f5c518",
                              insertbackground="#f5c518",
                              relief="flat", bd=2,
                              wrap="word")
        self.output.pack(fill="both", expand=True)

    def _panel(self, title):
        outer = tk.Frame(self, bg="#6b4f1a")
        outer.pack(fill="x")

        inner = tk.Frame(outer, bg="#2a1e0a", padx=10, pady=8)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Label(inner, text=title,
                 font=("Georgia", 8, "bold italic"),
                 fg="#9a7a3a", bg="#2a1e0a").pack(anchor="w", pady=(0, 4))

        return inner

    def run_bombe(self):
        ciphertext = self.cipher_entry.get().strip().upper()
        crib = self.crib_entry.get().strip().upper()

        self.output.delete("1.0", "end")
        self.output.insert("end", "Running...\n")

        self.progress["value"] = 0
        self.pct_label.config(text="0.0%")

        self.run_btn.config(state="disabled")

        t = threading.Thread(target=self._run_in_background,
                             args=(ciphertext, crib),
                             daemon=True)
        t.start()
        self._poll_progress()

    def _run_in_background(self, ciphertext, crib):
        self._counter   = Value(ctypes.c_int, 0)
        self._total     = Value(ctypes.c_int, 1) 

        result = bombe.bombe(ciphertext, crib,
                             counter=self._counter,
                             total=self._total)
        stops, offsets = result if isinstance(result, tuple) else (result, [])
        self.after(0, self._show_results, stops, offsets)

    def _poll_progress(self):
        try:
            done  = self._counter.value
            total = self._total.value
            if total > 0:
                pct = done / total * 100
                self.progress["value"] = pct
                self.pct_label.config(text=f"{pct:.1f}%  ({done}/{total} combos)")
        except AttributeError:
            pass  

        if self.run_btn["state"] == "disabled":
            self.after(200, self._poll_progress)

    def _show_results(self, stops, offsets):
        self.progress["value"] = 100
        self.pct_label.config(text="100.0%  done!")
        self.run_btn.config(state="normal")

        self.output.delete("1.0", "end")

        if not offsets:
            self.output.insert("end", "crib impossible\n")
            return

        if not stops:
            self.output.insert("end", "no stops found\n")
            return

        for i, s in enumerate(stops, 1):
            r = s["rotors"]
            self.output.insert("end", f"\nstop #{i}\n")
            self.output.insert("end", f"  rotors    {r[0]}-{r[1]}-{r[2]}\n")
            self.output.insert("end", f"  reflector {s['reflector']}\n")
            self.output.insert("end", f"  plaintext {s['plaintext']}\n")

if __name__ == "__main__":
    app = BombeUI()
    app.mainloop()