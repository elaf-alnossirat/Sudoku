import tkinter as tk
from tkinter import ttk, messagebox
import time
from sudoku import Sudoku
import os

class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")
        self.root.geometry("800x700")
        self.root.configure(bg="#1e1e1e")

        # Variables
        self.sudoku = None
        self.solving = False
        self.selected_method = tk.StringVar(value="1")

        # Styles
        self.style = ttk.Style()
        self.setup_style()

        # UI Setup
        self.main_frame = ttk.Frame(root, padding="10", style="DarkFrame.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()

    def setup_style(self):
        self.style.theme_use('clam')
        self.style.configure("DarkFrame.TFrame", background="#1e1e1e")
        self.style.configure("TButton", padding=6, relief="flat", background="#3a3a3a", foreground="white",
                             font=("Helvetica", 12), borderwidth=1)
        self.style.map("TButton",
                      background=[("active", "#575757"), ("pressed", "#444444")])

        self.style.configure("Title.TLabel", font=("Helvetica", 18, "bold"), background="#1e1e1e", foreground="white")
        self.style.configure("Method.TRadiobutton", background="#1e1e1e", foreground="white", font=("Helvetica", 12))

    def create_widgets(self):
        # Title
        ttk.Label(self.main_frame, text="Sudoku Solver", style="Title.TLabel").pack(pady=10)

        # Example Buttons
        example_frame = ttk.Frame(self.main_frame, style="DarkFrame.TFrame")
        example_frame.pack(fill=tk.X, pady=5)

        for i in range(1, 6):
            ttk.Button(example_frame, text=f"Example {i}", command=lambda n=i: self.load_example(n)).pack(side=tk.LEFT, padx=5)
        ttk.Button(example_frame, text="Clear Grid", command=self.clear_grid).pack(side=tk.LEFT, padx=5)

        # Sudoku Grid
        self.grid_frame = ttk.Frame(self.main_frame, style="DarkFrame.TFrame")
        self.grid_frame.pack(pady=10)
        self.create_grid()

        # Method Selection
        method_frame = ttk.Frame(self.main_frame, style="DarkFrame.TFrame")
        method_frame.pack(fill=tk.X, pady=10)

        ttk.Label(method_frame, text="Solving Method:", foreground="white", background="#1e1e1e").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(method_frame, text="Backtracking 🧠", variable=self.selected_method, value="1",
                        style="Method.TRadiobutton").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(method_frame, text="Brute Force 🔨", variable=self.selected_method, value="2",
                        style="Method.TRadiobutton").pack(side=tk.LEFT, padx=5)

        # Solve Button
        ttk.Button(self.main_frame, text="Solve Sudoku", command=self.solve_sudoku).pack(pady=10)

        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W,
                                    background="#2c2c2c", foreground="white")
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

    def create_grid(self):
        self.cells = []
        for i in range(9):
            row = []
            for j in range(9):
                cell_var = tk.StringVar()
                cell_frame = tk.Frame(self.grid_frame, background="#2c2c2c", width=40, height=40)
                cell_frame.grid(row=i, column=j, padx=1, pady=1)

                entry = tk.Entry(cell_frame, textvariable=cell_var, width=2, font=("Helvetica", 16), justify="center",
                                 background="#333", foreground="white", relief="flat", insertbackground="white")
                entry.pack(expand=True, fill="both")
                entry.bind("<FocusIn>", lambda e, x=i, y=j: self.highlight_cell(x, y))
                entry.bind("<Key>", self.validate_input)

                row.append({"var": cell_var, "entry": entry, "frame": cell_frame})
            self.cells.append(row)

    def highlight_cell(self, row, col):
        for i in range(9):
            for j in range(9):
                bg = "#2c2c2c"
                if i == row or j == col or (i // 3 == row // 3 and j // 3 == col // 3):
                    bg = "#404040"
                self.cells[i][j]["frame"].config(background=bg)
                self.cells[i][j]["entry"].config(background=bg)

        self.cells[row][col]["frame"].config(background="#575757")
        self.cells[row][col]["entry"].config(background="#575757")

    def validate_input(self, event):
        char = event.char
        if char == '' or char == '\x08':  # Allow backspace
            return
        if not char.isdigit() or char == '0':
            self.root.bell()
            return "break"

    def load_example(self, num):
        file_path = os.path.join("examples", f"exemple{num}.txt")
        if os.path.exists(file_path):
            try:
                self.status_var.set(f"Loading Example {num}...")
                self.root.update()
                self.sudoku = Sudoku(file_path)
                self.update_grid_display()
                self.status_var.set(f"Example {num} loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load Example {num}:\n{str(e)}")
        else:
            messagebox.showerror("Error", f"Example file {num} not found.")

    def update_grid_display(self):
        if not self.sudoku:
            return
        for i in range(9):
            for j in range(9):
                value = self.sudoku.grid[i][j]
                self.cells[i][j]["var"].set(str(value) if value != 0 else "")

    def clear_grid(self):
        for i in range(9):
            for j in range(9):
                self.cells[i][j]["var"].set("")
        self.status_var.set("Grid cleared")

    def solve_sudoku(self):
        if self.solving:
            return
        self.status_var.set("Solving in progress...")
        self.root.update()

        method = self.selected_method.get()
        start_time = time.time()

        try:
            if method == "1":
                solved = self.sudoku.solve_backtracking()
            else:
                solved = self.sudoku.solve_ultra_stupid_brute_force()
            if solved:
                self.update_grid_display()
                self.status_var.set(f"Solved in {time.time() - start_time:.2f}s")
            else:
                messagebox.showinfo("No Solution", "No solution found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to solve Sudoku:\n{str(e)}")
        finally:
            self.solving = False

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()
