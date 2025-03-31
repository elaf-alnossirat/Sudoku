import tkinter as tk
from tkinter import ttk, messagebox
import time
from sudoku import Sudoku
import os
from itertools import cycle

class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Neon Sudoku Solver")
        self.root.geometry("900x800")
        self.root.configure(bg='#121212')
        self.style = ttk.Style()
        self.setup_style()
        
        # Variables
        self.sudoku = None
        self.solving = False
        self.selected_method = tk.StringVar(value="1")
        self.cell_highlight = None
        self.animation_sequence = cycle(['#FF5555', '#55FF55', '#5555FF', '#FFFF55', '#FF55FF', '#55FFFF'])
        
        # Main container
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()
        self.setup_animations()
        
    def setup_style(self):
        self.style.theme_use('alt')
        self.style.configure('.', background='#121212', foreground='#e0e0e0')
        self.style.configure('TFrame', background='#1e1e1e')
        self.style.configure('TButton', padding=8, relief='flat', 
                           background='#333333', foreground='#ffffff',
                           font=('Segoe UI', 10, 'bold'))
        self.style.map('TButton', 
                      background=[('active', '#444444'), ('pressed', '#222222')])
        self.style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), 
                            background='#1e1e1e', foreground='#4fc3f7')
        self.style.configure('Method.TRadiobutton', background='#1e1e1e', 
                           foreground='#e0e0e0', font=('Segoe UI', 10))
        self.style.configure('TRadiobutton', indicatorbackground='#1e1e1e',
                           selectcolor='#333333')
        self.style.configure('Status.TLabel', background='#1e1e1e', 
                           foreground='#4fc3f7', font=('Segoe UI', 10, 'bold'))
        
    def setup_animations(self):
        # Status bar animation
        self.status_animation_id = None
        self.animate_status_bar()
        
    def animate_status_bar(self):
        color = next(self.animation_sequence)
        self.style.configure('Status.TLabel', foreground=color)
        self.status_animation_id = self.root.after(1500, self.animate_status_bar)
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.main_frame, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(header_frame, text="NEON SUDOKU SOLVER", style='Title.TLabel').pack(side=tk.LEFT)
        
        # Example selection buttons
        example_frame = ttk.Frame(self.main_frame, style='TFrame')
        example_frame.pack(fill=tk.X, pady=10)
        
        example_buttons = [
            ("Example 1", 1, '#FF5555'),
            ("Example 2", 2, '#55FF55'),
            ("Example 3", 3, '#5555FF'),
            ("Example 4", 4, '#FFFF55'),
            ("Example 5", 5, '#FF55FF')
        ]
        
        for text, num, color in example_buttons:
            btn = ttk.Button(example_frame, text=text, 
                            command=lambda n=num: self.load_example(n),
                            style='TButton')
            btn.pack(side=tk.LEFT, padx=5, ipadx=10)
            btn.bind('<Enter>', lambda e, b=btn, c=color: 
                    b.config(style='Hover.TButton') or 
                    self.root.config(cursor='hand2'))
            btn.bind('<Leave>', lambda e, b=btn: 
                    b.config(style='TButton') or 
                    self.root.config(cursor=''))
            
            self.style.configure(f'Hover.TButton', background=color)
        
        ttk.Button(example_frame, text="Clear Grid", command=self.clear_grid,
                  style='TButton').pack(side=tk.LEFT, padx=5, ipadx=10)
        
        # Sudoku grid
        self.grid_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.grid_frame.pack(pady=15)
        self.create_grid()
        
        # Method selection
        method_frame = ttk.Frame(self.main_frame, style='TFrame')
        method_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(method_frame, text="SOLVING METHOD:", 
                 style='Method.TRadiobutton').pack(side=tk.LEFT, padx=5)
        
        methods = [
            ("Backtracking 🧠", "1", '#4fc3f7'),
            ("Brute Force 🔨", "2", '#ff5252')
        ]
        
        for text, val, color in methods:
            btn = ttk.Radiobutton(method_frame, text=text, variable=self.selected_method, 
                                 value=val, style='Method.TRadiobutton')
            btn.pack(side=tk.LEFT, padx=15)
            btn.bind('<Enter>', lambda e, c=color: self.root.config(cursor='hand2'))
            btn.bind('<Leave>', lambda e: self.root.config(cursor=''))
        
        # Solve button with animation
        self.solve_btn = ttk.Button(self.main_frame, text="SOLVE SUDOKU", 
                                  command=self.solve_sudoku, style='TButton')
        self.solve_btn.pack(pady=15, ipadx=20, ipady=8)
        self.solve_btn.bind('<Enter>', lambda e: self.animate_button(self.solve_btn, '#4fc3f7'))
        self.solve_btn.bind('<Leave>', lambda e: self.animate_button(self.solve_btn, '#333333'))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to solve! Choose an example or input your own puzzle.")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, 
                                  style='Status.TLabel', padding=5)
        self.status_bar.pack(fill=tk.X, pady=(15, 0))
        
    def animate_button(self, button, target_color):
        current_color = button.cget('style')
        steps = 10
        start_color = '#333333'
        
        def update_color(step):
            if step <= steps:
                r = int(int(target_color[1:3], 16) * step/steps + 
                        int(start_color[1:3], 16) * (1-step/steps))
                g = int(int(target_color[3:5], 16) * step/steps + 
                        int(start_color[3:5], 16) * (1-step/steps))
                b = int(int(target_color[5:7], 16) * step/steps + 
                        int(start_color[5:7], 16) * (1-step/steps))
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.style.configure('ButtonAnim.TButton', background=color)
                button.config(style='ButtonAnim.TButton')
                self.root.after(20, update_color, step+1)
        
        update_color(1)
        
    def create_grid(self):
        self.cells = []
        for i in range(9):
            row = []
            for j in range(9):
                cell_frame = tk.Frame(self.grid_frame, 
                                    bg='#1e1e1e',
                                    highlightbackground='#333333', 
                                    highlightthickness=1)
                cell_frame.grid(row=i, column=j, padx=1, pady=1)
                
                cell_var = tk.StringVar()
                entry = tk.Entry(cell_frame, textvariable=cell_var, width=3, 
                                font=('Segoe UI', 16, 'bold'), justify='center',
                                borderwidth=0, relief='flat', bg='#252525',
                                fg='#ffffff', insertbackground='white')
                entry.pack(expand=True, fill='both')
                entry.bind('<FocusIn>', lambda e, i=i, j=j: self.on_cell_focus(i, j))
                entry.bind('<Key>', self.validate_input)
                
                row.append({'var': cell_var, 'entry': entry, 'frame': cell_frame})
            self.cells.append(row)
    
    def on_cell_focus(self, row, col):
        if self.cell_highlight:
            for i, j in self.cell_highlight:
                self.cells[i][j]['frame'].config(bg='#252525')
                self.cells[i][j]['entry'].config(bg='#252525')
        
        to_highlight = set()
        for i in range(9):
            to_highlight.add((row, i))
            to_highlight.add((i, col))
        
        box_row, box_col = row // 3 * 3, col // 3 * 3
        for i in range(3):
            for j in range(3):
                to_highlight.add((box_row + i, box_col + j))
        
        for i, j in to_highlight:
            if i == row and j == col:
                self.cells[i][j]['frame'].config(bg='#4a148c')
                self.cells[i][j]['entry'].config(bg='#4a148c')
            elif i == row or j == col:
                self.cells[i][j]['frame'].config(bg='#311b92')
                self.cells[i][j]['entry'].config(bg='#311b92')
            else:
                self.cells[i][j]['frame'].config(bg='#1a237e')
                self.cells[i][j]['entry'].config(bg='#1a237e')
        
        self.cell_highlight = to_highlight
    
    def validate_input(self, event):
        char = event.char
        if char == '' or char == '\x08':
            return
        if not char.isdigit() or char == '0':
            self.root.bell()
            return 'break'
    
    def load_example(self, num):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        examples_dir = os.path.join(script_dir, "examples")
        if not os.path.exists(examples_dir):
            examples_dir = script_dir
        
        file_path = os.path.join(examples_dir, f"exemple{num}.txt")
        if os.path.exists(file_path):
            try:
                self.status_var.set(f"Loading Example {num}...")
                self.root.update()
                
                self.sudoku = Sudoku(file_path)
                self.animate_grid_load()
                self.status_var.set(f"Example {num} loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load Example {num}:\n{str(e)}")
                self.status_var.set(f"Error loading Example {num}: {str(e)}")
        else:
            messagebox.showerror("Error", f"Example file {num} not found at:\n{file_path}")
            self.status_var.set(f"Example {num} not found")
    
    def animate_grid_load(self):
        for i in range(9):
            for j in range(9):
                value = self.sudoku.grid[i][j]
                original = self.sudoku.original_grid[i][j] != 0
                
                self.cells[i][j]['var'].set('')
                self.cells[i][j]['entry'].config(fg='#252525')
                
                def fill_cell(i=i, j=j, value=value, original=original):
                    if value != 0:
                        self.cells[i][j]['var'].set(str(value))
                        color = '#ffffff' if original else '#4fc3f7'
                        self.cells[i][j]['entry'].config(fg=color)
                
                delay = (i * 9 + j) * 20
                self.root.after(delay, fill_cell)
    
    def update_grid_display(self):
        if not self.sudoku:
            return
            
        for i in range(9):
            for j in range(9):
                value = self.sudoku.grid[i][j]
                self.cells[i][j]['var'].set(str(value) if value != 0 else '')
                
                if self.sudoku.original_grid[i][j] != 0:
                    self.cells[i][j]['entry'].config(fg='#ffffff', font=('Segoe UI', 16, 'bold'))
                else:
                    self.cells[i][j]['entry'].config(fg='#4fc3f7', font=('Segoe UI', 16))
    
    def clear_grid(self):
        self.animate_grid_clear()
        self.sudoku = None
        self.status_var.set("Grid cleared")
    
    def animate_grid_clear(self):
        for n in range(80, -1, -1):
            i, j = n // 9, n % 9
            if n % 2 == 0:
                i, j = 8 - i, 8 - j
            
            def clear_cell(i=i, j=j):
                self.cells[i][j]['var'].set('')
                self.cells[i][j]['entry'].config(fg='#ffffff')
            
            delay = (80 - n) * 10
            self.root.after(delay, clear_cell)
    
    def solve_sudoku(self):
        if self.solving:
            return
            
        self.solve_btn.config(state=tk.DISABLED)
        self.solving = True
        self.status_var.set("Solving in progress...")
        self.root.update()
        
        if not self.sudoku:
            grid = []
            for i in range(9):
                row = []
                for j in range(9):
                    val = self.cells[i][j]['var'].get()
                    row.append(int(val) if val else 0)
                grid.append(row)
            
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                    for row in grid:
                        line = ''.join(str(num) if num != 0 else '_' for num in row) + '\n'
                        f.write(line)
                    file_path = f.name
                
                self.sudoku = Sudoku(file_path)
                os.unlink(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Invalid Sudoku grid:\n{str(e)}")
                self.solve_btn.config(state=tk.NORMAL)
                self.solving = False
                self.status_var.set(f"Error: {str(e)}")
                return
        
        method = self.selected_method.get()
        start_time = time.time()
        
        def solve_thread():
            try:
                if method == "1":
                    solved = self.sudoku.solve_backtracking()
                else:
                    solved = self.sudoku.solve_ultra_stupid_brute_force()
                
                end_time = time.time()
                solve_time = end_time - start_time
                
                if solved:
                    self.animate_solution()
                    self.status_var.set(
                        f"Solved successfully! Attempts: {self.sudoku.attempts}, Time: {solve_time:.2f} seconds"
                    )
                else:
                    messagebox.showinfo("No Solution", "No solution found for this Sudoku.")
                    self.status_var.set(f"No solution found (Time: {solve_time:.2f}s)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to solve Sudoku:\n{str(e)}")
                self.status_var.set(f"Error during solving: {str(e)}")
            finally:
                self.solve_btn.config(state=tk.NORMAL)
                self.solving = False
        
        self.root.after(100, solve_thread)
    
    def animate_solution(self):
        solution_cells = []
        for i in range(9):
            for j in range(9):
                if self.sudoku.original_grid[i][j] == 0:
                    solution_cells.append((i, j))
        
        for idx, (i, j) in enumerate(solution_cells):
            def reveal_cell(i=i, j=j):
                value = self.sudoku.grid[i][j]
                self.cells[i][j]['var'].set(str(value))
                self.cells[i][j]['entry'].config(fg='#4fc3f7')
                
                for alpha in [0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2]:
                    def set_alpha(a=alpha):
                        r = int(79 * a + 37 * (1-a))
                        g = int(195 * a + 37 * (1-a))
                        b = int(247 * a + 37 * (1-a))
                        color = f"#{r:02x}{g:02x}{b:02x}"
                        self.cells[i][j]['entry'].config(fg=color)
                    self.root.after(idx * 50 + int(alpha * 100), set_alpha)
            
            self.root.after(idx * 50, reveal_cell)

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()