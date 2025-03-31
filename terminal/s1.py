# Importation des modules nécessaires
import time  # Pour mesurer les durées d'exécution
import itertools  # Pour générer des combinaisons exhaustives
import sys  # Pour gérer les arguments système
from copy import deepcopy  # Pour dupliquer les grilles sans modification
from colorama import init, Fore, Style  # Pour ajouter des couleurs dans le terminal
init()  # Initialisation de colorama pour les couleurs

# Vérification des contraintes initiales
def check_initial_validity(board):
    for i in range(9):
        row = [x for x in board[i] if x != 0]
        col = [board[j][i] for j in range(9) if board[j][i] != 0]
        if len(row) != len(set(row)) or len(col) != len(set(col)):
            return False
    for start_row in range(0, 9, 3):
        for start_col in range(0, 9, 3):
            block = [board[start_row + i][start_col + j] for i in range(3) for j in range(3) if board[start_row + i][start_col + j] != 0]
            if len(block) != len(set(block)):
                return False
    return True

# Méthode 1 : Backtracking (Résolution par retour arrière)
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

def solve_backtracking(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid_backtracking(board, row, col, num):
                        board[row][col] = num
                        if solve_backtracking(board):
                            return True
                        board[row][col] = 0
                return False
    return True

# Méthode 2 : Force Brute (Énumération exhaustive)
def get_empty_cells(board):
    return [(i, j) for i in range(9) for j in range(9) if board[i][j] == 0]

def is_valid_complete(board):
    for i in range(9):
        row = set(board[i])
        col = set(board[j][i] for j in range(9))
        if len(row - {0}) != len([x for x in board[i] if x != 0]) or len(col - {0}) != len([board[j][i] for j in range(9) if board[j][i] != 0]):
            return False
    for start_row in range(0, 9, 3):
        for start_col in range(0, 9, 3):
            block = set(board[start_row + i][start_col + j] for i in range(3) for j in range(3))
            if len(block - {0}) != len([j for i in range(3) for j in range(3) if board[start_row + i][start_col + j] != 0]):
                return False
    return True

def estimate_brute_force_time(board):
    empty_cells = get_empty_cells(board)
    total_combinations = 9 ** len(empty_cells)
    start_time = time.time()
    combinations_tested = 0
    
    for combination in itertools.product(range(1, 10), repeat=len(empty_cells)):
        if time.time() - start_time > 10:  # Échantillon sur 10 secondes
            break
        combinations_tested += 1
    
    elapsed_time = time.time() - start_time
    if combinations_tested == 0:
        return "Non estimable"
    rate = combinations_tested / elapsed_time
    estimated_time = total_combinations / rate
    return f"{estimated_time / 3600:.2f} heures"

def solve_brute_force(board, timeout):
    empty_cells = get_empty_cells(board)
    start_time = time.time()
    for combination in itertools.product(range(1, 10), repeat=len(empty_cells)):
        if time.time() - start_time > timeout:  # Limite dynamique basée sur Backtracking + 10s
            return None
        temp_board = deepcopy(board)
        for (row, col), num in zip(empty_cells, combination):
            temp_board[row][col] = num
        if is_valid_complete(temp_board):
            return temp_board
    return None

# Affichage avec couleurs
def print_board(board, original_board=None):
    for i in range(9):
        row = []
        for j in range(9):
            if board[i][j] == 0:
                row.append('.')
            elif original_board and original_board[i][j] != 0:
                row.append(f"{Fore.BLUE}{board[i][j]}{Style.RESET_ALL}")  # Bleu pour les nombres initiaux
            else:
                row.append(f"{Fore.RED}{board[i][j]}{Style.RESET_ALL}")  # Rouge pour les cases remplies
        print(" ".join(row))

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
    "4": [[3, 0, 0, 0, 0, 0, 0, 8, 0], [1, 0, 0, 6, 0, 3, 0, 0, 2], [5, 6, 0, 0, 0, 0, 0, 0, 0],
          [0, 8, 0, 1, 0, 0, 9, 7, 0], [0, 0, 0, 5, 0, 0, 0, 0, 0], [2, 0, 9, 0, 0, 4, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 6, 2, 0], [0, 0, 0, 0, 0, 0, 0, 4, 3], [0, 7, 0, 0, 5, 0, 1, 0, 0]],
    "5": [[0, 0, 9, 0, 6, 0, 0, 0, 0], [0, 0, 0, 3, 0, 0, 0, 1, 0], [0, 4, 5, 0, 1, 0, 0, 0, 6],
          [0, 0, 0, 0, 0, 8, 2, 0, 0], [0, 6, 1, 0, 3, 0, 0, 0, 5], [7, 0, 0, 0, 0, 0, 0, 0, 0],
          [9, 0, 0, 0, 4, 0, 0, 0, 0], [0, 7, 4, 2, 0, 0, 5, 0, 0], [3, 0, 0, 0, 0, 0, 0, 0, 7]]
}

# Programme principal avec interface améliorée
def main():
    while True:
        print(f"{Fore.CYAN}\nRésolution d'une grille Sudoku par deux algorithmes : Backtracking et Force Brute.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Sélectionnez une grille (1-5) :{Style.RESET_ALL}")

        if len(sys.argv) == 2 and sys.argv[1] in sudoku_grids:
            chosen_index = sys.argv[1]
            sys.argv = sys.argv[:1]
        else:
            chosen_index = input("Numéro de grille : ")

        if chosen_index not in sudoku_grids:
            print(f"{Fore.YELLOW}Erreur : choisissez un numéro entre 1 et 5.{Style.RESET_ALL}")
            continue

        original_board = sudoku_grids[chosen_index]
        print(f"{Fore.CYAN}\nGrille initiale {chosen_index} :{Style.RESET_ALL}")
        print_board(original_board)  # Grille initiale en bleu par défaut
        print(f"Validité : {'Valide' if check_initial_validity(original_board) else 'Invalide'}")

        # Structure des résultats
        results = {"Méthode": [], "Temps (s)": [], "Résultat": [], "Estimation": []}

        # Backtracking (toujours en premier)
        board_backtracking = deepcopy(original_board)
        start_time = time.time()
        success_backtracking = solve_backtracking(board_backtracking)
        time_backtracking = time.time() - start_time
        results["Méthode"].append("Backtracking")
        results["Temps (s)"].append(f"{time_backtracking:.4f}")
        results["Résultat"].append("Résolu" if success_backtracking else "Non résolu")
        results["Estimation"].append("N/A")

        # Force Brute avec temps supplémentaire
        brute_force_timeout = time_backtracking + 10  # 10 secondes de plus que Backtracking
        board_brute = deepcopy(original_board)
        start_time = time.time()
        result_brute = solve_brute_force(board_brute, brute_force_timeout)
        time_brute = time.time() - start_time
        brute_force_estimate = estimate_brute_force_time(original_board)
        results["Méthode"].append("Force Brute")
        results["Temps (s)"].append(f"{time_brute:.4f}")
        results["Résultat"].append("Résolu" if result_brute else f"Délai dépassé ({brute_force_timeout:.1f}s)")
        results["Estimation"].append(brute_force_estimate)

        # Affichage du tableau récapitulatif en vert
        print(f"{Fore.GREEN}\nRésultats :{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'-' * 65}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'Méthode':<15} | {'Temps (s)':<10} | {'Résultat':<20} | {'Estimation':<20}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'-' * 65}{Style.RESET_ALL}")
        for i in range(2):
            print(f"{Fore.GREEN}{results['Méthode'][i]:<15} | {results['Temps (s)'][i]:<10} | {results['Résultat'][i]:<20} | {results['Estimation'][i]:<20}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'-' * 65}{Style.RESET_ALL}")

        # Affichage des solutions avec couleurs
        if success_backtracking:
            print(f"{Fore.CYAN}\nSolution par Backtracking :{Style.RESET_ALL}")
            print_board(board_backtracking, original_board)  # Rouge pour les cases remplies
        if result_brute:
            print(f"{Fore.CYAN}\nSolution par Force Brute :{Style.RESET_ALL}")
            print_board(board_brute, original_board)  # Rouge pour les cases remplies

        # Choix de continuer
        while True:
            choice = input(f"{Fore.CYAN}\nNouvelle grille ? (o/n) : {Style.RESET_ALL}").lower()
            if choice in ['o', 'n']:
                break
            print(f"{Fore.YELLOW}Répondez par 'o' ou 'n'.{Style.RESET_ALL}")
        if choice == 'n':
            print(f"{Fore.CYAN}Programme terminé.{Style.RESET_ALL}")
            break

if __name__ == "__main__":
    main()