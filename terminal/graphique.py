import tkinter as tk
from tkinter import messagebox, ttk
import time
from copy import deepcopy
import itertools

# Fonctions de résolution
def is_valid_backtracking(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve_backtracking_fast(board):
    """Version rapide pour mesurer le temps réel"""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid_backtracking(board, row, col, num):
                        board[row][col] = num
                        if solve_backtracking_fast(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def solve_backtracking_slow(board, gui=None, slow=True):
    """Version avec option pour visualisation ralentie ou rapide"""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid_backtracking(board, row, col, num):
                        board[row][col] = num
                        if gui:
                            gui.update_cell(row, col, num, 'red')
                            gui.root.update()
                            if slow:
                                time.sleep(0.05)
                        if solve_backtracking_slow(board, gui, slow):
                            return True
                        board[row][col] = 0
                        if gui:
                            gui.update_cell(row, col, 0, 'black')
                            gui.root.update()
                            if slow:
                                time.sleep(0.05)
                return False
    return True

def get_empty_cells(board):
    return [(i, j) for i in range(9) for j in range(9) if board[i][j] == 0]

def estimate_brute_force_time(board):
    empty_cells = get_empty_cells(board)
    total_combinations = 9 ** len(empty_cells)
    ref_speed = 1_000_000  # 1 million de combinaisons par seconde
    estimated_seconds = total_combinations / ref_speed
    
    days = estimated_seconds / (60 * 60 * 24)
    years = days / 365.25
    centuries = years / 100
    
    return (f"{int(days):,} jours | {int(years):,} années | {int(centuries):,} siècles\n"
            f"Combinaisons : 9^{len(empty_cells)} = {total_combinations:,}")

# Grilles prédéfinies
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

# Classe pour l'interface graphique
class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver")
        self.root.configure(bg='#2c3e50')
        self.board = None
        self.original_board = None
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        self.real_time = 0

        # Style moderne
        style = ttk.Style()
        style.configure("TButton", font=('Arial', 12, 'bold'), padding=8, background='#3498db', foreground='#0000FF')
        style.map("TButton", background=[('active', '#2980b9')])
        style.configure("TLabel", font=('Arial', 14), background='#2c3e50', foreground='white')

        # Grille au centre
        grid_frame = tk.Frame(root, bg='black', padx=3, pady=3)
        grid_frame.grid(row=0, column=0, columnspan=9, pady=20)
        for i in range(9):
            for j in range(9):
                cell = tk.Entry(grid_frame, width=2, font=('Arial', 22, 'bold'), justify='center', 
                                borderwidth=2, relief='solid', bg='#ecf0f1', fg='black')
                cell.grid(row=i, column=j, padx=(2 if j % 3 != 0 else 4), 
                          pady=(2 if i % 3 != 0 else 4))
                if (i // 3 + j // 3) % 2 == 0:
                    cell.config(bg='#bdc3c7')
                self.cells[i][j] = cell

        # Boutons principaux
        btn_frame = ttk.Frame(root)
        btn_frame.grid(row=9, column=0, columnspan=9, pady=15)
        ttk.Button(btn_frame, text="Calculer", command=lambda: self.show_grid_options(slow=False)).grid(row=0, column=3, padx=10)
        ttk.Button(btn_frame, text="Simuler", command=lambda: self.show_grid_options(slow=True)).grid(row=0, column=4, padx=10)
        ttk.Button(btn_frame, text="Réinitialiser", command=self.reset_grid).grid(row=0, column=5, padx=10)

        # Noms des développeurs en bas à droite
        devs_label = ttk.Label(root, text="Redha - Elaf - Pierre - Dehlia", font=('Arial', 12, 'italic'), foreground='#ecf0f1')
        devs_label.grid(row=10, column=7, columnspan=2, pady=10, sticky="se")

        # Label vitesse locale
        self.speed_label = ttk.Label(root, text="Vitesse locale : N/A", font=('Arial', 10, 'italic'), foreground='#ecf0f1')
        self.speed_label.grid(row=10, column=0, columnspan=3, pady=10, sticky="sw")

    def update_cell(self, row, col, val, color):
        self.cells[row][col].delete(0, tk.END)
        if val != 0:
            self.cells[row][col].insert(0, str(val))
        self.cells[row][col].config(fg=color)

    def load_grid(self, grid_num):
        self.original_board = deepcopy(sudoku_grids[grid_num])
        self.board = deepcopy(self.original_board)
        for i in range(9):
            for j in range(9):
                val = self.board[i][j]
                self.cells[i][j].delete(0, tk.END)
                if val != 0:
                    self.cells[i][j].insert(0, str(val))
                    self.cells[i][j].config(fg='blue')
                else:
                    self.cells[i][j].config(fg='black')

    def reset_grid(self):
        if self.original_board:
            self.load_grid(next(k for k, v in sudoku_grids.items() if v == self.original_board))
        else:
            self.load_grid("1")

    def show_grid_options(self, slow):
        options_window = tk.Toplevel(self.root)
        options_window.title("Choisissez une grille")
        options_window.configure(bg='#2c3e50')
        options_window.geometry("300x200")

        tk.Label(options_window, text="Sélectionnez une grille", font=('Arial', 16, 'bold'), fg='#3498db', bg='#2c3e50').pack(pady=20)
        
        btn_frame = ttk.Frame(options_window)
        btn_frame.pack(pady=10)
        for i in range(1, 6):
            ttk.Button(btn_frame, text=f"Grille {i}", 
                       command=lambda x=str(i): [options_window.destroy(), self.solve_grid(x, slow)]).grid(row=0, column=i-1, padx=5)

    def show_results(self, backtracking_time, brute_force_estimation, grid_num):
        result_window = tk.Toplevel(self.root)
        result_window.title(f"Résultats - Grille {grid_num}")
        result_window.configure(bg='#2c3e50')
        result_window.geometry("600x300")

        tk.Label(result_window, text="VICTOIRE !", font=('Arial', 30, 'bold'), fg='#3498db', bg='#2c3e50').pack(pady=20)
        tk.Label(result_window, text=f"Backtracking : {backtracking_time:.4f} s", 
                 font=('Arial', 24, 'bold'), fg='white', bg='#2c3e50').pack(pady=10)
        tk.Label(result_window, text=f"Force Brute : {brute_force_estimation}", 
                 font=('Arial', 20, 'bold'), fg='#ecf0f1', bg='#2c3e50', justify='center').pack(pady=10)
        ttk.Button(result_window, text="Fermer", command=result_window.destroy).pack(pady=20)

    def solve_grid(self, grid_num, slow):
        self.load_grid(grid_num)
        self.root.update()

        # Étape 1 : Calcul rapide du temps réel
        temp_board = deepcopy(self.original_board)
        start_time = time.time()
        success = solve_backtracking_fast(temp_board)
        self.real_time = time.time() - start_time

        if not success:
            messagebox.showerror("Erreur", f"Impossible de résoudre la grille {grid_num} !")
            return

        # Étape 2 : Calcul de la vitesse locale
        empty_cells = len(get_empty_cells(self.original_board))
        operations = 9 * empty_cells
        self.local_speed = operations / self.real_time if self.real_time > 0 else 0
        self.speed_label.config(text=f"Vitesse locale : ~{int(self.local_speed):,} opérations/s")

        # Étape 3 : Visualisation
        self.board = deepcopy(self.original_board)
        solve_backtracking_slow(self.board, self, slow)

        # Étape 4 : Affichage de la solution finale
        for i in range(9):
            for j in range(9):
                if self.original_board[i][j] == 0:
                    self.update_cell(i, j, self.board[i][j], 'green')

        # Étape 5 : Estimation Force Brute et affichage
        brute_force_estimation = estimate_brute_force_time(self.board)
        self.show_results(self.real_time, brute_force_estimation, grid_num)

# Lancement de l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()