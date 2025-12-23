import tkinter as tk
from tkinter import filedialog, messagebox
import io
import contextlib

# =============================
# ATA COMPILER v1.1
# =============================
def compile_ata(code):
    lines = []
    indent = 0

    def emit(x):
        lines.append("    " * indent + x)

    for line_no, raw in enumerate(code.splitlines(), start=1):
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        # yaz
        if line.startswith("yaz "):
            emit(f"print({line[4:]})")

        # fonksiyon
        elif line.startswith("fonksiyon "):
            header = line.replace("fonksiyon ", "")
            emit(f"def {header}:")
            indent += 1

        # döndür
        elif line.startswith("döndür "):
            emit(f"return {line[7:]}")

        # eğer
        elif line.startswith("eğer "):
            cond = line[5:].replace(" ise", "")
            emit(f"if {cond}:")
            indent += 1

        # değilse
        elif line == "değilse":
            indent -= 1
            if indent < 0:
                raise Exception(f"Satır {line_no}: 'değilse' hatalı")
            emit("else:")
            indent += 1

        # iken
        elif line.startswith("iken "):
            emit(f"while {line[5:]}:")
            indent += 1

        # tekrar
        elif line.startswith("tekrar "):
            count = line.split()[1]
            emit(f"for _ in range({count}):")
            indent += 1

        # bitti
        elif line == "bitti":
            indent -= 1
            if indent < 0:
                raise Exception(f"Satır {line_no}: Fazla 'bitti'")

        # normal satır
        else:
            emit(line)

    if indent != 0:
        raise Exception("Eksik 'bitti' tespit edildi")

    return "\n".join(lines)

# =============================
# ÇALIŞTIR
# =============================
def run_code():
    output_box.delete("1.0", tk.END)
    try:
        ata_code = editor.get("1.0", tk.END)
        python_code = compile_ata(ata_code)

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            exec(python_code, {})

        output_box.insert(tk.END, buffer.getvalue())

    except Exception as e:
        messagebox.showerror("ATA Hatası", str(e))

# =============================
# DOSYA
# =============================
def open_file():
    file = filedialog.askopenfilename(filetypes=[("ATA Dosyaları", "*.ata")])
    if file:
        editor.delete("1.0", tk.END)
        with open(file, "r", encoding="utf-8") as f:
            editor.insert(tk.END, f.read())

def save_file():
    file = filedialog.asksaveasfilename(defaultextension=".ata",
                                        filetypes=[("ATA Dosyaları", "*.ata")])
    if file:
        with open(file, "w", encoding="utf-8") as f:
            f.write(editor.get("1.0", tk.END))

def clear_output():
    output_box.delete("1.0", tk.END)

# =============================
# SATIR NUMARASI
# =============================
def update_lines(event=None):
    count = editor.get("1.0", tk.END).count("\n")
    line_box.config(state="normal")
    line_box.delete("1.0", tk.END)
    for i in range(1, count + 1):
        line_box.insert(tk.END, f"{i}\n")
    line_box.config(state="disabled")

# =============================
# GUI
# =============================
root = tk.Tk()
root.title("ATA Language – Desktop IDE v1.1")
root.geometry("1000x650")
root.configure(bg="#1e1e1e")

menu = tk.Menu(root)
root.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label="Aç", command=open_file)
file_menu.add_command(label="Kaydet", command=save_file)
menu.add_cascade(label="Dosya", menu=file_menu)

run_menu = tk.Menu(menu, tearoff=0)
run_menu.add_command(label="Çalıştır", command=run_code)
run_menu.add_command(label="Çıktıyı Temizle", command=clear_output)
menu.add_cascade(label="Çalıştır", menu=run_menu)

frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

line_box = tk.Text(frame, width=4, bg="#2b2b2b", fg="#888", state="disabled")
line_box.pack(side="left", fill="y")

editor = tk.Text(frame, bg="#1e1e1e", fg="white",
                 insertbackground="white",
                 font=("Consolas", 12))
editor.pack(side="left", fill="both", expand=True)
editor.bind("<KeyRelease>", update_lines)

tk.Label(root, text="Çıktı", bg="#1e1e1e", fg="white").pack()
output_box = tk.Text(root, height=10, bg="#000", fg="#00ff88",
                     font=("Consolas", 11))
output_box.pack(fill="both")

update_lines()
root.mainloop()
