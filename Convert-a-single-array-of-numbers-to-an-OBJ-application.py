import os
import tkinter as tk
from tkinter import filedialog, messagebox

def parse_unified_file(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        tokens = f.read().strip().split()
    if len(tokens) < 2:
        raise ValueError("Файл слишком короткий: нет первых двух чисел (длин массивов).")

    vertex_count = int(tokens[0])
    face_count = int(tokens[1])

    rest = tokens[2:]
    if len(rest) < vertex_count + face_count:
        raise ValueError(f"В файле недостаточно чисел: указаны lengths {vertex_count}, {face_count}, а данных {len(rest)}.")

    # Парсим числа
    vertex_tokens = rest[:vertex_count]
    face_tokens = rest[vertex_count:vertex_count + face_count]

    vertex_numbers = [float(x) for x in vertex_tokens]
    face_numbers = [int(float(x)) for x in face_tokens]  # на случай, если индексы записаны как числа с .0

    return vertex_numbers, face_numbers, vertex_count, face_count

def build_obj(vertex_numbers, face_numbers, vertices_per_face=3, zero_based_input=False):
    # Проверки
    if len(vertex_numbers) % 3 != 0:
        raise ValueError("Количество чисел вершин не делится на 3 — невозможно разбить на вершины (x,y,z).")
    if vertices_per_face <= 1:
        raise ValueError("vertices_per_face должен быть >= 2.")

    num_vertices = len(vertex_numbers) // 3
    if len(face_numbers) % vertices_per_face != 0:
        raise ValueError("Количество чисел в faces не кратно указанному vertices_per_face.")

    # Сформировать списки
    vertices = []
    for i in range(num_vertices):
        x, y, z = vertex_numbers[3*i:3*i+3]
        vertices.append((x, y, z))

    faces = []
    num_faces = len(face_numbers) // vertices_per_face
    for i in range(num_faces):
        inds = face_numbers[vertices_per_face*i : vertices_per_face*i + vertices_per_face]
        if zero_based_input:
            inds = [idx + 1 for idx in inds]
        faces.append(inds)

    # Сформировать текст OBJ
    lines = []
    for v in vertices:
        lines.append("v {:.6f} {:.6f} {:.6f}".format(v[0], v[1], v[2]))
    for f in faces:
        # безопасно форматируем индексы целыми
        lines.append("f " + " ".join(str(int(idx)) for idx in f))

    return "\n".join(lines) + "\n"

def save_obj_to_desktop(text, filename="output.obj"):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    out_path = os.path.join(desktop, filename)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
    return out_path

# GUI
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Unified → OBJ")
        self.geometry("420x200")
        self.resizable(False, False)

        tk.Label(self, text="Выберите файл с единым массивом чисел (первые два числа — lengths):", wraplength=400, justify="left").pack(padx=10, pady=(12,6))

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Выбрать файл", command=self.select_file, width=18).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Выход", command=self.destroy, width=10).pack(side="left", padx=6)

        options_frame = tk.Frame(self)
        options_frame.pack(pady=6, fill="x", padx=12)

        tk.Label(options_frame, text="Кол-во вершин в грани (vertices per face):").grid(row=0, column=0, sticky="w")
        self.vertices_per_face_var = tk.IntVar(value=3)
        tk.Entry(options_frame, textvariable=self.vertices_per_face_var, width=6).grid(row=0, column=1, sticky="w", padx=6)

        self.zero_based_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Входные индексы 0-based (добавить +1 при записи)", variable=self.zero_based_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6,0))

        tk.Label(self, text="(Если faces был сохранён как тройки индексов — оставьте 3.)", fg="gray").pack(pady=(6,0))

    def select_file(self):
        path = filedialog.askopenfilename(title="Выберите файл", filetypes=[("Text files","*.txt *.dat *.out *.objdata"),("All files","*.*")])
        if not path:
            return
        try:
            vertex_numbers, face_numbers, vlen, flen = parse_unified_file(path)
            vpf = int(self.vertices_per_face_var.get())
            obj_text = build_obj(vertex_numbers, face_numbers, vertices_per_face=vpf, zero_based_input=self.zero_based_var.get())
            out_path = save_obj_to_desktop(obj_text)
            messagebox.showinfo("Готово", f"OBJ сохранён:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    App().mainloop()
