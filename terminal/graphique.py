import tkinter as tk
from tkinter import ttk
import time
from copy import deepcopy
import threading
from typing import List, Optional

# Constants
GRID_SIZE = 9
CELL_SIZE = 50
COLORS = {
    'bg': '#f0f0f0',      # Light gray background
    'grid_bg': '#ffffff',  # White grid background
    'cell_bg': '#e0e0e0',  # Light gray cells
    'cell_alt': '#d0d0d0', # Slightly darker gray
    'text': '#000000',     # Black text
    'original': '#0000FF', # Blue for original numbers
    'solving': '#FF0000',  # Red for solving process
    'solved': '#00FF00',   # Green for solved numbers
    'button_active': '#90ee90',  # Light green for active buttons
    'button_inactive': '#4682b4' # Steel blue for inactive buttons
}

class SudokuSolver:
    @staticmethod
    def is_valid(board: List[List[int]], row: int, col: int, num: int) -> bool:
        for i in range(GRID_SIZE):
            if board[row][i] == num or board[i][col] == num:
                return False
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False
        return True

    @staticmethod
    def solve_fast(board: List[List[int]]) -> bool:
        empty = SudokuSolver.find_empty(board)
        if not empty:
            return True
        row, col = empty
        for num in range(1, 10):
            if SudokuSolver.is_valid(board, row, col, num):
                board[row][col] = num
                if SudokuSolver.solve_fast(board):
                    return True
                board[row][col] = 0
        return False

    @staticmethod
    def find_empty(board: List[List[int]]) -> Optional[tuple]:
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if board[i][j] == 0:
                    return (i, j)
        return None

    @staticmethod
    def count_empty_cells(board: List[List[int]]) -> int:
        return sum(row.count(0) for row in board)

class SudokuGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Résolveur de Sudoku")
        self.root.configure(bg=COLORS['bg'])
        self.root.geometry("800x800")
        self.solver = SudokuSolver()
        self.board = None
        self.original_board = None
        self.cells = []
        self.is_solving = False
        self.selected_grid = None
        self.selected_method = None
        
        self._setup_styles()
        self._create_ui()
        self.load_grid("1")

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", 
                       font=('Helvetica', 12, 'bold'),
                       padding=10,
                       background=COLORS['button_inactive'],
                       foreground='#ffffff')
        style.map("TButton", 
                 background=[('active', COLORS['button_active'])],
                 foreground=[('active', '#000000')])
        style.configure("TLabel", 
                       background=COLORS['bg'],
                       foreground=COLORS['text'],
                       font=('Helvetica', 12))
        style.configure("Selected.TButton",
                       background=COLORS['button_active'],
                       foreground='#000000')

    def _create_ui(self):
        main_frame = tk.Frame(self.root, bg=COLORS['bg'], padx=20, pady=20)
        main_frame.pack()

        self.grid_frame = tk.Canvas(main_frame, 
                                  width=CELL_SIZE * 9 + 4,
                                  height=CELL_SIZE * 9 + 4,
                                  bg=COLORS['grid_bg'],
                                  highlightthickness=2,
                                  highlightbackground='#000000')
        self.grid_frame.pack(pady=10)
        self._create_grid()

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=10)
        
        self.fast_button = ttk.Button(control_frame, text="Résoudre Rapidement", 
                                    command=lambda: self.select_method("fast"),
                                    style="TButton")
        self.fast_button.grid(row=0, column=0, padx=5)
        
        self.visualize_button = ttk.Button(control_frame, text="Visualiser", 
                                         command=lambda: self.select_method("visualize"),
                                         style="TButton")
        self.visualize_button.grid(row=0, column=1, padx=5)
        
        ttk.Button(control_frame, text="Réinitialiser", command=self.reset_grid,
                  style="TButton").grid(row=0, column=2, padx=5)

        grid_frame = ttk.Frame(main_frame)
        grid_frame.pack(pady=10)
        
        self.grid_buttons = {}
        for i in range(1, 6):
            btn = ttk.Button(grid_frame, text=f"Grille {i}", 
                           command=lambda x=str(i): self.select_grid(x),
                           style="TButton")
            btn.grid(row=0, column=i-1, padx=5)
            self.grid_buttons[str(i)] = btn

        self.status_label = ttk.Label(main_frame, text="Prêt", font=('Helvetica', 10, 'italic'))
        self.status_label.pack(pady=5)

        self.results_frame = ttk.Frame(main_frame)
        self.results_frame.pack(pady=10)
        
        self.backtracking_time_label = ttk.Label(self.results_frame, text="")
        self.backtracking_time_label.pack()
        
        self.brute_force_label = ttk.Label(self.results_frame, text="")
        self.brute_force_label.pack()
        
        self.speed_label = ttk.Label(self.results_frame, text="")
        self.speed_label.pack()

        # Footer with credits
        footer_label = ttk.Label(main_frame, 
                               text="By: Redha-Elaf-Pierre-Dehlia, Supervisor AKRAM, La_Plateforme Mar2025",
                               font=('Helvetica', 10, 'italic'))
        footer_label.pack(side=tk.BOTTOM, pady=10)

    def _create_grid(self):
        self.cells = []
        for i in range(GRID_SIZE):
            row = []
            for j in range(GRID_SIZE):
                bg = COLORS['cell_bg'] if (i // 3 + j // 3) % 2 == 0 else COLORS['cell_alt']
                cell = tk.Entry(self.grid_frame,
                               width=2,
                               font=('Helvetica', 20, 'bold'),
                               justify='center',
                               bg=bg,
                               fg=COLORS['text'],
                               borderwidth=1,
                               relief='flat')
                cell.place(x=j * CELL_SIZE + 2, 
                          y=i * CELL_SIZE + 2,
                          width=CELL_SIZE - 1,
                          height=CELL_SIZE - 1)
                row.append(cell)
            self.cells.append(row)

    def update_cell(self, row: int, col: int, val: int, color: str):
        cell = self.cells[row][col]
        cell.delete(0, tk.END)
        if val != 0:
            cell.insert(0, str(val))
        cell.config(fg=color)

    def load_grid(self, grid_num: str):
        self.original_board = deepcopy(sudoku_grids[grid_num])
        self.board = deepcopy(self.original_board)
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                val = self.board[i][j]
                color = COLORS['original'] if val != 0 else COLORS['text']
                self.update_cell(i, j, val, color)
        self.clear_results()

    def reset_grid(self):
        if self.original_board:
            self.load_grid(next(k for k, v in sudoku_grids.items() 
                              if v == self.original_board))
        self.status_label.config(text="Réinitialisation terminée")
        self.selected_method = None
        self.selected_grid = None
        self.fast_button.configure(style="TButton")
        self.visualize_button.configure(style="TButton")
        for btn in self.grid_buttons.values():
            btn.configure(style="TButton")
        self.clear_results()

    def select_method(self, method: str):
        if self.is_solving:
            return
        self.selected_method = method
        self.fast_button.configure(style="TButton")
        self.visualize_button.configure(style="TButton")
        if method == "fast":
            self.fast_button.configure(style="Selected.TButton")
        elif method == "visualize":
            self.visualize_button.configure(style="Selected.TButton")
        self.status_label.config(text="Méthode sélectionnée, choisissez une grille")

    def select_grid(self, grid_num: str):
        if self.is_solving:
            return
        self.selected_grid = grid_num
        for btn in self.grid_buttons.values():
            btn.configure(style="TButton")
        self.grid_buttons[grid_num].configure(style="Selected.TButton")
        self.load_grid(grid_num)
        if self.selected_method:
            self.solve_grid()
        else:
            self.status_label.config(text="Grille sélectionnée, choisissez une méthode")

    def calculate_brute_force_time(self):
        empty_cells = self.solver.count_empty_cells(self.original_board)
        combinations = 9 ** empty_cells
        seconds = combinations / 1_000_000  # Assuming 1M operations/sec
        months = seconds / (60 * 60 * 24 * 30.44)
        years = months / 12
        centuries = years / 100
        return centuries, years, months, combinations

    def format_scientific(self, value: float) -> str:
        """Format large numbers in scientific notation."""
        return f"{value:.2e}"

    def solve_grid(self):
        if self.is_solving or not self.selected_method or not self.selected_grid:
            return
        
        self.is_solving = True
        self.status_label.config(text="Résolution en cours...")
        
        def solve_thread():
            temp_board = deepcopy(self.original_board)
            start_time = time.time()
            success = self.solver.solve_fast(temp_board)
            solve_time = time.time() - start_time
            
            if not success:
                self.root.after(0, lambda: self.status_label.config(text="Aucune solution trouvée!"))
                self.is_solving = False
                return
            
            visualize = self.selected_method == "visualize"
            if not visualize:
                self.board = temp_board
                for i in range(GRID_SIZE):
                    for j in range(GRID_SIZE):
                        if self.original_board[i][j] == 0:
                            self.update_cell(i, j, self.board[i][j], COLORS['solved'])
            else:
                self.board = deepcopy(self.original_board)
                self._visualize_solution(self.board)
            
            empty_cells = self.solver.count_empty_cells(self.original_board)
            operations = empty_cells * 9
            speed = operations / solve_time if solve_time > 0 else 0
            centuries, years, months, combinations = self.calculate_brute_force_time()
            
            self.root.after(0, lambda: [
                self.status_label.config(text="Résolu!"),
                self.backtracking_time_label.config(
                    text=f"Temps Backtracking: {solve_time:.4f} secondes"),
                self.brute_force_label.config(
                    text=f"Force Brute estimée: ~{self.format_scientific(centuries)} siècles | "
                         f"~{self.format_scientific(years)} années | ~{self.format_scientific(months)} mois"),
                self.speed_label.config(
                    text=f"Vitesse: ~{int(speed):,} opérations/s"),
                setattr(self, 'is_solving', False)
            ])
        
        threading.Thread(target=solve_thread, daemon=True).start()

    def _visualize_solution(self, board: List[List[int]]) -> bool:
        empty = self.solver.find_empty(board)
        if not empty:
            return True
        row, col = empty
        
        for num in range(1, 10):
            if self.solver.is_valid(board, row, col, num):
                board[row][col] = num
                self.root.after(0, lambda: self.update_cell(row, col, num, COLORS['solving']))
                self.root.update()
                time.sleep(0.03)
                
                if self._visualize_solution(board):
                    if self.original_board[row][col] == 0:
                        self.update_cell(row, col, num, COLORS['solved'])
                    return True
                    
                board[row][col] = 0
                self.root.after(0, lambda: self.update_cell(row, col, 0, COLORS['text']))
                self.root.update()
                time.sleep(0.03)
        return False

    def clear_results(self):
        self.backtracking_time_label.config(text="")
        self.brute_force_label.config(text="")
        self.speed_label.config(text="")

# Predefined grids
sudoku_grids = {
    "1": [[0, 7, 2, 9, 0, 0, 0, 3, 0], [0, 0, 1, 0, 0, 6, 0, 8, 0], [0, 0, 0, 0, 4, 0, 0, 6, 0],
          [9, 6, 0, 0, 0, 4, 1, 0, 8], [0, 4, 8, 7, 0, 5, 0, 9, 6], [0, 0, 5, 6, 0, 8, 0, 0, 3],
          [0, 0, 0, 4, 0, 2, 0, 1, 0], [8, 5, 0, 0, 6, 0, 3, 2, 7], [1, 0, 0, 8, 5, 0, 0, 0, 0]],
    "2": [[7, 0, 0, 9, 2, 0, 4, 0, 0], [0, 0, 0, 0, 0, 0, 7, 0, 0], [0, 0, 4, 0, 0, 8, 3, 1, 2],
          [4, 0, 0, 0, 0, 2, 5, 0, 0], [2, 0, 0, 0, 1, 0, 0, 0, 3], [0, 0, 8, 5, 0, 0, 0, 0, 4],
          [8, 4, 3, 2, 0, 0, 6, 0, 0], [0, 0, 5, 0, 0, 0, 0, 0, 0], [0, 0, 2, 0, 6, 4, 0, 0, 5]],
    "3": [[0, 0, 9, 0, 8, 5, 0, 6, 3], [0, 7, 0, 9, 6, 0, 0, 0, 0], [5, 0, 1, 0, 0, 4, 0, 0, 0],
          [0, 0, 6, 7, 0, 3, 0, 0, 4], [0, 4, 0, 2, 1, 0, 3, 9, 0], [8, 0, 0, 0, 9, 0, 0, 5, 7],
          [9, 8, 4, 5, 0, 0, 6, 0, 0], [0, 0, 7, 6, 4, 9, 0, 3, 0], [6, 1, 0, 0, 2, 0, 0, 4, 0]],
    "4": [[3, 0, 0, 0, 0, 0, 0, 8, 0], [0, 0, 0, 6, 0, 3, 0, 0, 2], [5, 6, 0, 0, 0, 0, 0, 0, 0],
          [0, 8, 0, 1, 0, 0, 9, 7, 0], [0, 0, 0, 5, 0, 0, 0, 0, 0], [2, 0, 9, 0, 0, 4, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 6, 2, 0], [0, 0, 0, 0, 0, 0, 0, 4, 3], [0, 7, 0, 0, 5, 0, 1, 0, 0]],
    "5": [[0, 0, 9, 0, 6, 0, 0, 0, 0], [0, 0, 0, 3, 0, 0, 0, 1, 0], [0, 4, 5, 0, 1, 0, 0, 0, 6],
          [0, 0, 0, 0, 0, 8, 2, 0, 0], [0, 6, 1, 0, 3, 0, 0, 0, 5], [7, 0, 0, 0, 0, 0, 0, 0, 0],
          [9, 0, 0, 0, 4, 0, 0, 0, 0], [0, 7, 4, 2, 0, 0, 5, 0, 0], [3, 0, 0, 0, 0, 0, 0, 0, 7]]
}

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()