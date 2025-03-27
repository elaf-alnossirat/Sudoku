# Section : Importations des bibliothèques nécessaires
import tkinter as tk              # Importe Tkinter pour l'interface graphique
from tkinter import ttk           # Importe ttk pour des widgets stylisés
import time                       # Importe time pour mesurer le temps et gérer les délais
from copy import deepcopy         # Importe deepcopy pour copier les grilles
import threading                  # Importe threading pour exécuter la résolution en parallèle
from typing import List, Optional # Importe List et Optional pour typer les variables

# Section : Définition des constantes globales
GRID_SIZE = 9                     # Taille de la grille de Sudoku (9x9)
CELL_SIZE = 50                    # Taille en pixels de chaque cellule
COLORS = {                        # Dictionnaire des couleurs utilisées
    'bg': '#f0f0f0',              # Fond général : gris clair
    'grid_bg': '#ffffff',         # Fond de la grille : blanc
    'cell_bg': '#e0e0e0',         # Fond des cellules : gris clair
    'cell_alt': '#d0d0d0',        # Fond alternatif des cellules : gris un peu plus foncé
    'text': '#000000',            # Couleur du texte : noir
    'original': '#0000FF',        # Couleur des chiffres originaux : bleu
    'solving': '#FF0000',         # Couleur pendant la résolution : rouge
    'solved': '#00FF00',          # Couleur des chiffres résolus : vert
    'button_active': '#90ee90',   # Couleur des boutons actifs : vert clair
    'button_inactive': '#4682b4'  # Couleur des boutons inactifs : bleu acier
}

# Section : Classe pour résoudre le Sudoku
class SudokuSolver:
    # Méthode : Vérifie si un chiffre peut être placé
    @staticmethod
    def is_valid(board: List[List[int]], row: int, col: int, num: int) -> bool:
        for i in range(GRID_SIZE):  # Parcours chaque colonne de la ligne
            if board[row][i] == num or board[i][col] == num:  # Vérifie ligne et colonne
                return False          # Retourne faux si le chiffre est déjà là
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)  # Calcule le coin de la boîte 3x3
        for i in range(3):        # Parcours les lignes de la boîte
            for j in range(3):    # Parcours les colonnes de la boîte
                if board[start_row + i][start_col + j] == num:  # Vérifie la boîte
                    return False      # Retourne faux si le chiffre est trouvé
        return True               # Retourne vrai si le chiffre est valide

    # Méthode : Résout le Sudoku avec backtracking
    @staticmethod
    def solve_fast(board: List[List[int]]) -> bool:
        empty = SudokuSolver.find_empty(board)  # Trouve une cellule vide
        if not empty:            # Si aucune cellule vide, puzzle résolu
            return True          # Retourne vrai
        row, col = empty         # Récupère les coordonnées de la cellule vide
        for num in range(1, 10): # Essaie les chiffres de 1 à 9
            if SudokuSolver.is_valid(board, row, col, num):  # Si le chiffre est valide
                board[row][col] = num  # Place le chiffre
                if SudokuSolver.solve_fast(board):  # Résout le reste récursivement
                    return True      # Si ça marche, retourne vrai
                board[row][col] = 0  # Sinon, efface (backtrack)
        return False             # Retourne faux si aucune solution

    # Méthode : Trouve une cellule vide
    @staticmethod
    def find_empty(board: List[List[int]]) -> Optional[tuple]:
        for i in range(GRID_SIZE):  # Parcours les lignes
            for j in range(GRID_SIZE):  # Parcours les colonnes
                if board[i][j] == 0:  # Si la cellule est vide (0)
                    return (i, j)     # Retourne ses coordonnées
        return None               # Retourne None si aucune cellule vide

    # Méthode : Compte les cellules vides
    @staticmethod
    def count_empty_cells(board: List[List[int]]) -> int:
        return sum(row.count(0) for row in board)  # Compte les 0 dans chaque ligne

# Section : Classe pour l’interface graphique
class SudokuGUI:
    # Méthode : Initialise l’interface
    def __init__(self, root: tk.Tk):
        self.root = root          # Référence à la fenêtre principale
        self.root.title("Résolveur de Sudoku")  # Définit le titre
        self.root.configure(bg=COLORS['bg'])  # Configure le fond
        self.root.geometry("800x900")  # Définit la taille de la fenêtre
        self.solver = SudokuSolver()  # Crée une instance du solveur
        self.board = None         # Grille actuelle
        self.original_board = None  # Grille originale
        self.cells = []           # Liste des cellules graphiques
        self.is_solving = False   # Indicateur de résolution en cours
        self.selected_grid = None  # Grille sélectionnée
        self.selected_method = None  # Méthode sélectionnée
        self.visual_delay = 0.03  # Délai initial pour la visualisation (en secondes)
        
        self._setup_styles()      # Configure les styles
        self._create_ui()         # Crée l’interface
        self.load_grid("1")       # Charge la grille 1 par défaut

    # Méthode : Configure les styles des widgets
    def _setup_styles(self):
        style = ttk.Style()       # Crée un objet pour les styles
        style.theme_use('clam')   # Utilise le thème "clam"
        style.configure("TButton",  # Style des boutons
                       font=('Helvetica', 12, 'bold'),  # Police grasse
                       padding=10,        # Espacement interne
                       background=COLORS['button_inactive'],  # Fond inactif
                       foreground='#ffffff')  # Texte blanc
        style.map("TButton",      # Changements quand actif
                 background=[('active', COLORS['button_active'])],  # Vert clair
                 foreground=[('active', '#000000')])  # Texte noir
        style.configure("TLabel",  # Style des étiquettes
                       background=COLORS['bg'],  # Fond gris clair
                       foreground=COLORS['text'],  # Texte noir
                       font=('Helvetica', 12))  # Police standard
        style.configure("Selected.TButton",  # Style des boutons sélectionnés
                       background=COLORS['button_active'],  # Vert clair
                       foreground='#000000')  # Texte noir

    # Méthode : Crée l’interface utilisateur
    def _create_ui(self):
        main_frame = tk.Frame(self.root, bg=COLORS['bg'], padx=20, pady=20)  # Cadre principal
        main_frame.pack()         # Affiche le cadre

        self.grid_frame = tk.Canvas(main_frame,  # Toile pour la grille
                                  width=CELL_SIZE * 9 + 4,  # Largeur totale
                                  height=CELL_SIZE * 9 + 4,  # Hauteur totale
                                  bg=COLORS['grid_bg'],  # Fond blanc
                                  highlightthickness=2,  # Bordure de 2 pixels
                                  highlightbackground='#000000')  # Bordure noire
        self.grid_frame.pack(pady=10)  # Affiche la grille
        self._create_grid()       # Crée les cellules

        control_frame = ttk.Frame(main_frame)  # Cadre pour les boutons de contrôle
        control_frame.pack(pady=10)  # Affiche le cadre

        self.fast_button = ttk.Button(control_frame, text="Résoudre Rapidement",  # Bouton rapide
                                    command=lambda: self.select_method("fast"),  # Appelle méthode rapide
                                    style="TButton")  # Style TButton
        self.fast_button.grid(row=0, column=0, padx=5)  # Place le bouton

        self.visualize_button = ttk.Button(control_frame, text="Visualiser",  # Bouton visualisation
                                         command=lambda: self.select_method("visualize"),  # Appelle visualisation
                                         style="TButton")  # Style TButton
        self.visualize_button.grid(row=0, column=1, padx=5)  # Place le bouton

        ttk.Button(control_frame, text="Réinitialiser", command=self.reset_grid,  # Bouton réinitialisation
                  style="TButton").grid(row=0, column=2, padx=5)  # Place le bouton

        grid_frame = ttk.Frame(main_frame)  # Cadre pour les boutons de grille
        grid_frame.pack(pady=10)  # Affiche le cadre

        self.grid_buttons = {}    # Dictionnaire des boutons de grille
        for i in range(1, 6):     # Crée 5 boutons pour les grilles
            btn = ttk.Button(grid_frame, text=f"Grille {i}",  # Bouton pour grille i
                           command=lambda x=str(i): self.select_grid(x),  # Appelle select_grid
                           style="TButton")  # Style TButton
            btn.grid(row=0, column=i-1, padx=5)  # Place le bouton
            self.grid_buttons[str(i)] = btn  # Stocke le bouton

        # Ajout du slider pour la vitesse de visualisation
        speed_frame = ttk.Frame(main_frame)  # Cadre pour le slider de vitesse
        speed_frame.pack(pady=5)  # Affiche le cadre
        speed_label = ttk.Label(speed_frame, text="Vitesse de Simulation")  # Étiquette pour le slider
        speed_label.pack(side=tk.LEFT, padx=5)  # Place l’étiquette à gauche
        self.speed_slider = ttk.Scale(speed_frame, from_=0.5, to=0.01, orient=tk.HORIZONTAL,  # Slider de vitesse
                                     length=200, command=self.update_speed)  # Longueur et fonction de mise à jour
        self.speed_slider.set(self.visual_delay)  # Définit la valeur initiale du slider
        self.speed_slider.pack(side=tk.LEFT)  # Place le slider

        self.status_label = ttk.Label(main_frame, text="Prêt", font=('Helvetica', 10, 'italic'))  # Étiquette de statut
        self.status_label.pack(pady=5)  # Affiche l’étiquette

        self.results_frame = ttk.Frame(main_frame)  # Cadre pour les résultats
        self.results_frame.pack(pady=10)  # Affiche le cadre

        self.backtracking_time_label = ttk.Label(self.results_frame, text="")  # Temps backtracking
        self.backtracking_time_label.pack()  # Affiche l’étiquette

        self.brute_force_label = ttk.Label(self.results_frame, text="")  # Estimation brute
        self.brute_force_label.pack()  # Affiche l’étiquette

        self.speed_label = ttk.Label(self.results_frame, text="")  # Vitesse
        self.speed_label.pack()  # Affiche l’étiquette

        footer_label = ttk.Label(main_frame,  # Crédits en bas
                               text="By: Redha-Elaf-Pierre-Dehlia, Supervisor AKRAM, La_Plateforme Mar2025",
                               font=('Helvetica', 10, 'italic'))  # Police italique
        footer_label.pack(side=tk.BOTTOM, pady=10)  # Place en bas

    # Méthode : Crée les cellules de la grille
    def _create_grid(self):
        self.cells = []           # Initialise la liste des cellules
        for i in range(GRID_SIZE):  # Boucle sur les lignes
            row = []              # Liste pour la ligne actuelle
            for j in range(GRID_SIZE):  # Boucle sur les colonnes
                bg = COLORS['cell_bg'] if (i // 3 + j // 3) % 2 == 0 else COLORS['cell_alt']  # Couleur alternée
                cell = tk.Entry(self.grid_frame,  # Crée une cellule
                               width=2,   # Largeur de 2 caractères
                               font=('Helvetica', 20, 'bold'),  # Police grande
                               justify='center',  # Texte centré
                               bg=bg,     # Couleur de fond
                               fg=COLORS['text'],  # Couleur du texte
                               borderwidth=1,  # Bordure fine
                               relief='flat')  # Pas de relief
                cell.place(x=j * CELL_SIZE + 2, y=i * CELL_SIZE + 2,  # Positionne la cellule
                          width=CELL_SIZE - 1, height=CELL_SIZE - 1)  # Définit la taille
                row.append(cell)  # Ajoute la cellule à la ligne
            self.cells.append(row)  # Ajoute la ligne à la liste

    # Méthode : Met à jour une cellule
    def update_cell(self, row: int, col: int, val: int, color: str):
        cell = self.cells[row][col]  # Récupère la cellule
        cell.delete(0, tk.END)    # Efface le contenu
        if val != 0:              # Si la valeur n’est pas zéro
            cell.insert(0, str(val))  # Insère la nouvelle valeur
        cell.config(fg=color)     # Change la couleur du texte

    # Méthode : Charge une grille
    def load_grid(self, grid_num: str):
        self.original_board = deepcopy(sudoku_grids[grid_num])  # Copie la grille originale
        self.board = deepcopy(self.original_board)  # Copie pour travailler
        for i in range(GRID_SIZE):  # Parcours les lignes
            for j in range(GRID_SIZE):  # Parcours les colonnes
                val = self.board[i][j]  # Récupère la valeur
                color = COLORS['original'] if val != 0 else COLORS['text']  # Bleu si original
                self.update_cell(i, j, val, color)  # Met à jour la cellule
        self.clear_results()      # Efface les résultats

    # Méthode : Réinitialise la grille
    def reset_grid(self):
        if self.original_board:   # Si une grille existe
            self.load_grid(next(k for k, v in sudoku_grids.items() if v == self.original_board))  # Recharge
        self.status_label.config(text="Réinitialisation terminée")  # Met à jour le statut
        self.selected_method = None  # Réinitialise la méthode
        self.selected_grid = None  # Réinitialise la grille
        self.fast_button.configure(style="TButton")  # Remet le bouton rapide à l’état normal
        self.visualize_button.configure(style="TButton")  # Remet le bouton visualisation à l’état normal
        for btn in self.grid_buttons.values():  # Parcours les boutons de grille
            btn.configure(style="TButton")  # Remet à l’état normal
        self.clear_results()      # Efface les résultats

    # Méthode : Sélectionne une méthode
    def select_method(self, method: str):
        if self.is_solving:       # Si résolution en cours
            return                # Ne fait rien
        self.selected_method = method  # Stocke la méthode
        self.fast_button.configure(style="TButton")  # Remet le bouton rapide à l’état normal
        self.visualize_button.configure(style="TButton")  # Remet le bouton visualisation à l’état normal
        if method == "fast":      # Si méthode rapide
            self.fast_button.configure(style="Selected.TButton")  # Met en surbrillance
        elif method == "visualize":  # Si méthode visualisation
            self.visualize_button.configure(style="Selected.TButton")  # Met en surbrillance
        self.status_label.config(text="Méthode sélectionnée, choisissez une grille")  # Met à jour le statut

    # Méthode : Sélectionne une grille
    def select_grid(self, grid_num: str):
        if self.is_solving:       # Si résolution en cours
            return                # Ne fait rien
        self.selected_grid = grid_num  # Stocke la grille
        for btn in self.grid_buttons.values():  # Parcours les boutons
            btn.configure(style="TButton")  # Remet à l’état normal
        self.grid_buttons[grid_num].configure(style="Selected.TButton")  # Met en surbrillance
        self.load_grid(grid_num)  # Charge la grille
        if self.selected_method:  # Si méthode sélectionnée
            self.solve_grid()     # Lance la résolution
        else:                     # Sinon
            self.status_label.config(text="Grille sélectionnée, choisissez une méthode")  # Met à jour le statut

    # Méthode : Met à jour la vitesse de visualisation
    def update_speed(self, value):
        self.visual_delay = float(value)  # Met à jour le délai en fonction du slider

    # Méthode : Calcule le temps estimé pour la force brute
    def calculate_brute_force_time(self):
        empty_cells = self.solver.count_empty_cells(self.original_board)  # Compte les cellules vides
        combinations = 9 ** empty_cells  # Calcule les combinaisons possibles
        seconds = combinations / 1_000_000  # Estime les secondes
        months = seconds / (60 * 60 * 24 * 30.44)  # Convertit en mois
        years = months / 12      # Convertit en années
        centuries = years / 100   # Convertit en siècles
        return centuries, years, months, combinations  # Retourne les valeurs

    # Méthode : Formate les nombres en notation scientifique
    def format_scientific(self, value: float) -> str:
        return f"{value:.2e}"     # Retourne en notation scientifique (ex : 1.23e4)

    # Méthode : Résout la grille
    def solve_grid(self):
        if self.is_solving or not self.selected_method or not self.selected_grid:  # Vérifie les conditions
            return                # Ne fait rien si non valides
        
        self.is_solving = True    # Indique que la résolution commence
        self.status_label.config(text="Résolution en cours...")  # Met à jour le statut
        
        def solve_thread():       # Fonction pour le fil parallèle
            temp_board = deepcopy(self.original_board)  # Copie la grille
            start_time = time.time()  # Temps de départ
            success = self.solver.solve_fast(temp_board)  # Résout avec backtracking
            solve_time = time.time() - start_time  # Temps écoulé
            
            if not success:       # Si échec
                self.root.after(0, lambda: self.status_label.config(text="Aucune solution trouvée!"))  # Met à jour
                self.is_solving = False  # Fin de résolution
                return            # Quitte
            
            visualize = self.selected_method == "visualize"  # Vérifie la méthode
            if not visualize:     # Si rapide
                self.board = temp_board  # Met à jour la grille
                for i in range(GRID_SIZE):  # Parcours les lignes
                    for j in range(GRID_SIZE):  # Parcours les colonnes
                        if self.original_board[i][j] == 0:  # Si vide à l’origine
                            self.update_cell(i, j, self.board[i][j], COLORS['solved'])  # Affiche en vert
            else:                 # Si visualisation
                self.board = deepcopy(self.original_board)  # Réinitialise
                self._visualize_solution(self.board)  # Visualise
            
            empty_cells = self.solver.count_empty_cells(self.original_board)  # Compte les vides
            operations = empty_cells * 9  # Estime les opérations
            speed = operations / solve_time if solve_time > 0 else 0  # Calcule la vitesse
            centuries, years, months, combinations = self.calculate_brute_force_time()  # Temps brute
            
            self.root.after(0, lambda: [  # Met à jour l’interface
                self.status_label.config(text="Résolu!"),  # Statut résolu
                self.backtracking_time_label.config(text=f"Temps Backtracking: {solve_time:.4f} secondes"),  # Temps
                self.brute_force_label.config(text=f"Force Brute estimée: ~{self.format_scientific(centuries)} siècles | "
                                                  f"~{self.format_scientific(years)} années | "
                                                  f"~{self.format_scientific(months)} mois"),  # Estimation
                self.speed_label.config(text=f"Vitesse: ~{int(speed):,} opérations/s"),  # Vitesse
                setattr(self, 'is_solving', False)  # Fin de résolution
            ])
        
        threading.Thread(target=solve_thread, daemon=True).start()  # Lance le fil

    # Méthode : Visualise la résolution avec délai ajustable
    def _visualize_solution(self, board: List[List[int]]) -> bool:
        empty = self.solver.find_empty(board)  # Trouve une cellule vide
        if not empty:             # Si aucune vide
            return True           # Puzzle résolu
        row, col = empty          # Coordonnées de la cellule
        
        for num in range(1, 10):  # Essaie 1 à 9
            if self.solver.is_valid(board, row, col, num):  # Si valide
                board[row][col] = num  # Place le chiffre
                self.root.after(0, lambda: self.update_cell(row, col, num, COLORS['solving']))  # Affiche en rouge
                self.root.update()    # Met à jour l’interface
                time.sleep(self.visual_delay)  # Pause ajustable selon le slider
                
                if self._visualize_solution(board):  # Résout le reste
                    if self.original_board[row][col] == 0:  # Si vide à l’origine
                        self.update_cell(row, col, num, COLORS['solved'])  # Affiche en vert
                    return True       # Succès
                board[row][col] = 0   # Efface (backtrack)
                self.root.after(0, lambda: self.update_cell(row, col, 0, COLORS['text']))  # Efface visuellement
                self.root.update()    # Met à jour l’interface
                time.sleep(self.visual_delay)  # Pause ajustable
        return False              # Échec si aucune solution

    # Méthode : Efface les résultats
    def clear_results(self):
        self.backtracking_time_label.config(text="")  # Efface le temps
        self.brute_force_label.config(text="")  # Efface l’estimation
        self.speed_label.config(text="")  # Efface la vitesse

# Section : Grilles prédéfinies
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

# Section : Point d’entrée du programme
if __name__ == "__main__":
    root = tk.Tk()            # Crée la fenêtre principale
    app = SudokuGUI(root)     # Crée l’interface
    root.mainloop()           # Lance la boucle principale