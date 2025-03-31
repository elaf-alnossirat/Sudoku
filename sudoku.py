import time
import os
import math
import signal
import sys
from itertools import product

class Sudoku:
    def __init__(self, file_path):
        self.grid = self.load_grid(file_path)
        self.original_grid = [row.copy() for row in self.grid]
        self.attempts = 0
        self.start_time = None
        self.abort = False

    def load_grid(self, file_path):
        grid = []
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                row = []
                for ch in line.strip():
                    if ch.isdigit():
                        row.append(int(ch))
                    elif ch == '_':
                        row.append(0)
                if len(row) != 9:
                    raise ValueError(f"Ligne {line_num} invalide : doit contenir exactement 9 chiffres ou underscores")
                grid.append(row)
        if len(grid) != 9:
            raise ValueError("La grille doit contenir exactement 9 lignes.")
        return grid

    def display(self):
      print("\n\033[1;37m+--------------------- Grille ----------------------+\033[0m")
      for i, row in enumerate(self.grid):
        if i % 3 == 0 and i != 0:
            print("------+-------+------")
        row_str = ""
        for j, val in enumerate(row):
            if j % 3 == 0 and j != 0:
                row_str += "| "
            if val == 0:
                row_str += ". "
            elif self.original_grid[i][j] == 0:
                row_str += f"\033[0;32m{val}\033[0m "  # couleur = valeur trouvée
            else:
                row_str += f"{val} "  # Blanc = valeur de départ
        print(row_str.strip())
    print("\033[1;37m+--------------------------------------------------+\033[0m")

    def is_valid(self, row, col, num):
        for i in range(9):
            if self.grid[row][i] == num or self.grid[i][col] == num:
                return False
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if self.grid[start_row + i][start_col + j] == num:
                    return False
        return True

    def is_valid_grid(self):
        for row in range(9):
            for col in range(9):
                num = self.grid[row][col]
                if num != 0:
                    self.grid[row][col] = 0
                    if not self.is_valid(row, col, num):
                        self.grid[row][col] = num
                        return False
                    self.grid[row][col] = num
        return True

    def solve_backtracking(self):
        for row in range(9):
            for col in range(9):
                if self.grid[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_valid(row, col, num):
                            self.grid[row][col] = num
                            self.attempts += 1
                            if self.solve_backtracking():
                                return True
                            self.grid[row][col] = 0
                    return False
        return True

    def solve_ultra_stupid_brute_force(self):
        empty_positions = [(i, j) for i in range(9) for j in range(9) if self.grid[i][j] == 0]
        total = len(empty_positions)
        print(f"\033[1;34m\nCases vides : {total}\033[0m")
        print("\033[1;34mBrute force en cours...\033[0m\n")

        try:
            for combo in product(range(1, 10), repeat=total):
                for index, (i, j) in enumerate(empty_positions):
                    self.grid[i][j] = combo[index]
                self.attempts += 1
                if self.is_valid_grid():
                    return True
        except Exception as e:
            print(f"\nErreur : {e}")
        return False

    def estimate_brute_force_time(self):
        empty_cells = sum(row.count(0) for row in self.grid)
        possibilities = 9 ** empty_cells
        essais_par_seconde = 1000
        secondes = possibilities / essais_par_seconde

        if secondes < 60:
            return f"Temps estimé \033[1;33m≈ {secondes:.2f} secondes\033[0m"
        elif secondes < 3600:
            return f"Temps estimé \033[1;33m≈ {secondes/60:.2f} minutes\033[0m"
        elif secondes < 86400:
            return f"Temps estimé \033[1;33m≈ {secondes/3600:.2f} heures\033[0m"
        elif secondes < 31_536_000:
            return f"Temps estimé \033[1;33m≈ {secondes/86400:.2f} jours\033[0m"
        elif secondes < 1e12:
            return f"Temps estimé \033[1;33m≈ {secondes/31_536_000:.2f} années\033[0m"
        else:
            puissance = math.log10(secondes)
            return f"Temps estimé \033[1;33m≈ 10^{puissance:.1f} secondes (ridiculement long)\033[0m"

def handle_interrupt(signal_received, frame):
    print("\n\n[!] Interruption utilisateur.")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_interrupt)

    print("\nQuel exemple veux-tu resoudre ? (1 a 5)")
    exemple_num = input("Numero de l'exemple : ").strip()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "examples", f"exemple{exemple_num}.txt")

    if not os.path.exists(file_path):
        print(f"\nLe fichier {file_path} n'existe pas.")
        exit()

    sudoku = Sudoku(file_path)
    print("\nGrille initiale :")
    sudoku.display()

    print("\n\033[1;36m+------------------------------------+")
    print("| Comment va-tu résoudre le sudoku ? |")
    print("+------------------------------------+\033[0m")
    print("1. Backtracking 🧠")
    print("2. Force Brute 🔨")
    choix_methode = input("\033[1;36mTon choix (1 ou 2) : \033[0m").strip()

    print("\n\033[1;34m+--------------------------+")
    print("|   Résolution en cours   |")
    print("+--------------------------+\033[0m")
    sudoku.start_time = time.time()

    if choix_methode == "1":
        print("\n\033[1;35mMethode : Backtracking\033[0m")
        solved = sudoku.solve_backtracking()
    elif choix_methode == "2":
        print("\n\033[1;33mMethode : Force Brute\033[0m")
        print(sudoku.estimate_brute_force_time())
        time.sleep(2)
        solved = sudoku.solve_ultra_stupid_brute_force()
    else:
        print("\nChoix invalide.")
        exit()

    end = time.time()

    if solved:
        sudoku.display()
        print("\n\033[1;32m✅ Sudoku résolu !\033[0m")
        print(f"Tentatives totales : {sudoku.attempts}")
        print(f"Temps total : {end - sudoku.start_time:.2f} secondes")
    else:
        print("\n\033[1;31m❌ Aucune solution trouvée.\033[0m")
