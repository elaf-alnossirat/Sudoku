# Section : Importations des bibliothèques nécessaires
import tkinter as tk              # Importe la bibliothèque Tkinter pour créer l'interface graphique
from tkinter import ttk           # Importe ttk pour des widgets stylisés (boutons, étiquettes)
import time                       # Importe time pour mesurer le temps d'exécution
from copy import deepcopy         # Importe deepcopy pour copier des listes sans les modifier
import threading                  # Importe threading pour exécuter des tâches en parallèle
from typing import List, Optional # Importe List et Optional pour typer les variables

# Section : Définition des constantes globales
GRID_SIZE = 9                     # Taille de la grille de Sudoku (9x9)
CELL_SIZE = 50                    # Taille en pixels de chaque cellule dans l'interface
COLORS = {                        # Dictionnaire des couleurs utilisées dans l'interface
    'bg': '#f0f0f0',              # Couleur de fond générale : gris clair
    'grid_bg': '#ffffff',         # Couleur de fond de la grille : blanc
    'cell_bg': '#e0e0e0',         # Couleur des cellules : gris clair
    'cell_alt': '#d0d0d0',        # Couleur alternative pour les cellules : gris un peu plus foncé
    'text': '#000000',            # Couleur du texte : noir
    'original': '#0000FF',        # Couleur des chiffres originaux : bleu
    'solving': '#FF0000',         # Couleur pendant la résolution : rouge
    'solved': '#00FF00',          # Couleur des chiffres résolus : vert
    'button_active': '#90ee90',   # Couleur des boutons actifs : vert clair
    'button_inactive': '#4682b4'  # Couleur des boutons inactifs : bleu acier
}

# Section : Classe pour résoudre le Sudoku
class SudokuSolver:
    # Méthode : Vérifie si un chiffre peut être placé à une position
    @staticmethod
    def is_valid(board: List[List[int]], row: int, col: int, num: int) -> bool:
        for i in range(GRID_SIZE):  # Parcours chaque colonne de la ligne
            if board[row][i] == num or board[i][col] == num:  # Vérifie la ligne et la colonne
                return False          # Retourne faux si le chiffre est déjà présent
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)  # Calcule le coin supérieur gauche de la boîte 3x3
        for i in range(3):        # Parcours les 3 lignes de la boîte
            for j in range(3):    # Parcours les 3 colonnes de la boîte
                if board[start_row + i][start_col + j] == num:  # Vérifie si le chiffre est dans la boîte
                    return False      # Retourne faux si trouvé
        return True               # Retourne vrai si le chiffre est valide

    # Méthode : Résout le Sudoku avec l'algorithme de retour en arrière (backtracking)
    @staticmethod
    def solve_fast(board: List[List[int]]) -> bool:
        empty = SudokuSolver.find_empty(board)  # Trouve une cellule vide
        if not empty:            # Si aucune cellule vide, le puzzle est résolu
            return True          # Retourne vrai
        row, col = empty         # Récupère les coordonnées de la cellule vide
        for num in range(1, 10): # Essaie les chiffres de 1 à 9
            if SudokuSolver.is_valid(board, row, col, num):  # Vérifie si le chiffre est valide
                board[row][col] = num  # Place le chiffre dans la cellule
                if SudokuSolver.solve_fast(board):  # Essaie de résoudre le reste récursivement
                    return True      # Si ça marche, retourne vrai
                board[row][col] = 0  # Si ça échoue, efface le chiffre (retour en arrière)
        return False             # Retourne faux si aucune solution n’est trouvée

    # Méthode : Trouve une cellule vide dans la grille
    @staticmethod
    def find_empty(board: List[List[int]]) -> Optional[tuple]:
        for i in range(GRID_SIZE):  # Parcours chaque ligne
            for j in range(GRID_SIZE):  # Parcours chaque colonne
                if board[i][j] == 0:  # Si la cellule est vide (0)
                    return (i, j)     # Retourne les coordonnées de la cellule vide
        return None               # Retourne None si aucune cellule vide n’est trouvée

    # Méthode : Compte le nombre de cellules vides
    @staticmethod
    def count_empty_cells(board: List[List[int]]) -> int:
        return sum(row.count(0) for row in board)  # Compte les 0 dans chaque ligne et fait la somme

# Section : Classe pour l’interface graphique du Sudoku
class SudokuGUI:
    # Méthode : Initialise l’interface
    def __init__(self, root: tk.Tk):
        self.root = root          # Référence à la fenêtre principale
        self.root.title("Résolveur de Sudoku")  # Définit le titre de la fenêtre
        self.root.configure(bg=COLORS['bg'])  # Configure la couleur de fond
        self.root.geometry("800x900")  # Définit la taille de la fenêtre (800x900 pixels)
        self.solver = SudokuSolver()  # Crée une instance du solveur de Sudoku
        self.board = None         # Grille actuelle (sera remplie plus tard)
        self.original_board = None  # Grille originale (pour réinitialisation)
        self.cells = []           # Liste des cellules graphiques
        self.is_solving = False   # Indicateur si une résolution est en cours
        self.selected_grid = None  # Grille sélectionnée par l’utilisateur
        self.selected_method = None  # Méthode de résolution sélectionnée
        
        self._setup_styles()      # Configure les styles des widgets
        self._create_ui()         # Crée l’interface utilisateur
        self.load_grid("1")       # Charge la grille numéro 1 par défaut

    # Méthode : Configure les styles des widgets
    def _setup_styles(self):
        style = ttk.Style()       # Crée un objet pour gérer les styles
        style.theme_use('clam')   # Utilise le thème "clam" pour un look moderne
        style.configure("TButton",  # Configure le style des boutons
                       font=('Helvetica', 12, 'bold'),  # Police : Helvetica, taille 12, gras
                       padding=10,        # Espacement interne de 10 pixels
                       background=COLORS['button_inactive'],  # Couleur de fond inactive
                       foreground='#ffffff')  # Couleur du texte : blanc
        style.map("TButton",      # Définit les changements quand le bouton est actif
                 background=[('active', COLORS['button_active'])],  # Vert clair quand cliqué
                 foreground=[('active', '#000000')])  # Texte noir quand actif
        style.configure("TLabel",  # Configure le style des étiquettes
                       background=COLORS['bg'],  # Fond gris clair
                       foreground=COLORS['text'],  # Texte noir
                       font=('Helvetica', 12))  # Police : Helvetica, taille 12
        style.configure("Selected.TButton",  # Style pour les boutons sélectionnés
                       background=COLORS['button_active'],  # Vert clair
                       foreground='#000000')  # Texte noir

    # Méthode : Crée l’interface utilisateur
    def _create_ui(self):
        main_frame = tk.Frame(self.root, bg=COLORS['bg'], padx=20, pady=20)  # Crée un cadre principal
        main_frame.pack()         # Affiche le cadre dans la fenêtre

        self.grid_frame = tk.Canvas(main_frame,  # Crée une toile pour la grille
                                  width=CELL_SIZE * 9 + 4,  # Largeur : 9 cellules + bordure
                                  height=CELL_SIZE * 9 + 4,  # Hauteur : 9 cellules + bordure
                                  bg=COLORS['grid_bg'],  # Fond blanc
                                  highlightthickness=2,  # Épaisseur de la bordure : 2 pixels
                                  highlightbackground='#000000')  # Couleur de la bordure : noir
        self.grid_frame.pack(pady=10)  # Affiche la grille avec un espacement vertical
        self._create_grid()       # Crée les cellules de la grille

        control_frame = ttk.Frame(main_frame)  # Crée un cadre pour les boutons de contrôle
        control_frame.pack(pady=10)  # Affiche le cadre avec un espacement

        self.fast_button = ttk.Button(control_frame, text="Résoudre Rapidement",  # Bouton pour résolution rapide
                                    command=lambda: self.select_method("fast"),  # Appelle select_method avec "fast"
                                    style="TButton")  # Utilise le style TButton
        self.fast_button.grid(row=0, column=0, padx=5)  # Place le bouton en ligne 0, colonne 0

        self.visualize_button = ttk.Button(control_frame, text="Visualiser",  # Bouton pour visualisation
                                         command=lambda: self.select_method("visualize"),  # Appelle avec "visualize"
                                         style="TButton")  # Utilise le style TButton
        self.visualize_button.grid(row=0, column=1, padx=5)  # Place en ligne 0, colonne 1

        ttk.Button(control_frame, text="Réinitialiser", command=self.reset_grid,  # Bouton pour réinitialiser
                  style="TButton").grid(row=0, column=2, padx=5)  # Place en ligne 0, colonne 2

        grid_frame = ttk.Frame(main_frame)  # Crée un cadre pour les boutons de sélection de grille
        grid_frame.pack(pady=10)  # Affiche le cadre avec espacement

        self.grid_buttons = {}    # Dictionnaire pour stocker les boutons des grilles
        for i in range(1, 6):     # Boucle pour créer 5 boutons (Grille 1 à 5)
            btn = ttk.Button(grid_frame, text=f"Grille {i}",  # Bouton avec texte "Grille i"
                           command=lambda x=str(i): self.select_grid(x),  # Appelle select_grid avec le numéro
                           style="TButton")  # Utilise le style TButton
            btn.grid(row=0, column=i-1, padx=5)  # Place le bouton dans la ligne 0, colonne i-1
            self.grid_buttons[str(i)] = btn  # Stocke le bouton dans le dictionnaire

        self.status_label = ttk.Label(main_frame, text="Prêt", font=('Helvetica', 10, 'italic'))  # Étiquette de statut
        self.status_label.pack(pady=5)  # Affiche l’étiquette avec espacement

        self.results_frame = ttk.Frame(main_frame)  # Crée un cadre pour les résultats
        self.results_frame.pack(pady=10)  # Affiche le cadre avec espacement

        self.backtracking_time_label = ttk.Label(self.results_frame, text="")  # Étiquette pour le temps backtracking
        self.backtracking_time_label.pack()  # Affiche l’étiquette

        self.brute_force_label = ttk.Label(self.results_frame, text="")  # Étiquette pour l’estimation brute
        self.brute_force_label.pack()  # Affiche l’étiquette

        self.speed_label = ttk.Label(self.results_frame, text="")  # Étiquette pour la vitesse
        self.speed_label.pack()  # Affiche l’étiquette

        footer_label = ttk.Label(main_frame,  # Étiquette pour les crédits en bas
                               text="By: Redha-Elaf-Pierre-Dehlia, Supervisor AKRAM, La_Plateforme Mar2025",
                               font=('Helvetica', 10, 'italic'))  # Police italique
        footer_label.pack(side=tk.BOTTOM, pady=10)  # Place en bas avec espacement

    # Méthode : Crée les cellules de la grille graphique
    def _create_grid(self):
        self.cells = []           # Initialise la liste des cellules
        for i in range(GRID_SIZE):  # Boucle sur les lignes
            row = []              # Crée une liste pour la ligne actuelle
            for j in range(GRID_SIZE):  # Boucle sur les colonnes
                bg = COLORS['cell_bg'] if (i // 3 + j // 3) % 2 == 0 else COLORS['cell_alt']  # Couleur alternée
                cell = tk.Entry(self.grid_frame,  # Crée une cellule éditable
                               width=2,   # Largeur de 2 caractères
                               font=('Helvetica', 20, 'bold'),  # Police grande et grasse
                               justify='center',  # Texte centré
                               bg=bg,     # Couleur de fond
                               fg=COLORS['text'],  # Couleur du texte
                               borderwidth=1,  # Bordure fine
                               relief='flat')  # Pas de relief
                cell.place(x=j * CELL_SIZE + 2,  # Positionne en x
                          y=i * CELL_SIZE + 2,  # Positionne en y
                          width=CELL_SIZE - 1,  # Largeur de la cellule
                          height=CELL_SIZE - 1)  # Hauteur de la cellule
                row.append(cell)  # Ajoute la cellule à la ligne
            self.cells.append(row)  # Ajoute la ligne à la liste des cellules

    # Méthode : Met à jour une cellule graphique
    def update_cell(self, row: int, col: int, val: int, color: str):
        cell = self.cells[row][col]  # Récupère la cellule à la position donnée
        cell.delete(0, tk.END)    # Efface le contenu actuel
        if val != 0:              # Si la valeur n’est pas zéro
            cell.insert(0, str(val))  # Insère la nouvelle valeur
        cell.config(fg=color)     # Change la couleur du texte

    # Méthode : Charge une grille prédéfinie
    def load_grid(self, grid_num: str):
        self.original_board = deepcopy(sudoku_grids[grid_num])  # Copie la grille originale
        self.board = deepcopy(self.original_board)  # Copie pour la grille de travail
        for i in range(GRID_SIZE):  # Parcours les lignes
            for j in range(GRID_SIZE):  # Parcours les colonnes
                val = self.board[i][j]  # Récupère la valeur
                color = COLORS['original'] if val != 0 else COLORS['text']  # Bleu si original, noir sinon
                self.update_cell(i, j, val, color)  # Met à jour la cellule
        self.clear_results()      # Efface les résultats précédents

    # Méthode : Réinitialise la grille
    def reset_grid(self):
        if self.original_board:   # Si une grille originale existe
            self.load_grid(next(k for k, v in sudoku_grids.items()  # Recharge la grille actuelle
                              if v == self.original_board))
        self.status_label.config(text="Réinitialisation terminée")  # Met à jour le statut
        self.selected_method = None  # Réinitialise la méthode sélectionnée
        self.selected_grid = None  # Réinitialise la grille sélectionnée
        self.fast_button.configure(style="TButton")  # Remet le bouton rapide à l’état normal
        self.visualize_button.configure(style="TButton")  # Remet le bouton visualisation à l’état normal
        for btn in self.grid_buttons.values():  # Parcours tous les boutons de grille
            btn.configure(style="TButton")  # Remet chaque bouton à l’état normal
        self.clear_results()      # Efface les résultats

    # Méthode : Sélectionne une méthode de résolution
    def select_method(self, method: str):
        if self.is_solving:       # Si une résolution est en cours
            return                # Ne fait rien
        self.selected_method = method  # Stocke la méthode choisie
        self.fast_button.configure(style="TButton")  # Remet le bouton rapide à l’état normal
        self.visualize_button.configure(style="TButton")  # Remet le bouton visualisation à l’état normal
        if method == "fast":      # Si la méthode est "rapide"
            self.fast_button.configure(style="Selected.TButton")  # Met en surbrillance le bouton rapide
        elif method == "visualize":  # Si la méthode est "visualisation"
            self.visualize_button.configure(style="Selected.TButton")  # Met en surbrillance le bouton visualisation
        self.status_label.config(text="Méthode sélectionnée, choisissez une grille")  # Met à jour le statut

    # Méthode : Sélectionne une grille
    def select_grid(self, grid_num: str):
        if self.is_solving:       # Si une résolution est en cours
            return                # Ne fait rien
        self.selected_grid = grid_num  # Stocke la grille choisie
        for btn in self.grid_buttons.values():  # Parcours tous les boutons de grille
            btn.configure(style="TButton")  # Remet chaque bouton à l’état normal
        self.grid_buttons[grid_num].configure(style="Selected.TButton")  # Met en surbrillance le bouton choisi
        self.load_grid(grid_num)  # Charge la grille sélectionnée
        if self.selected_method:  # Si une méthode est déjà sélectionnée
            self.solve_grid()     # Lance la résolution
        else:                     # Sinon
            self.status_label.config(text="Grille sélectionnée, choisissez une méthode")  # Met à jour le statut

    # Méthode : Calcule le temps estimé pour la force brute
    def calculate_brute_force_time(self):
        empty_cells = self.solver.count_empty_cells(self.original_board)  # Compte les cellules vides
        combinations = 9 ** empty_cells  # Calcule le nombre total de combinaisons possibles (9^cellules vides)
        seconds = combinations / 1_000_000  # Estime les secondes (1M opérations par seconde)
        months = seconds / (60 * 60 * 24 * 30.44)  # Convertit en mois
        years = months / 12      # Convertit en années
        centuries = years / 100   # Convertit en siècles
        return centuries, years, months, combinations  # Retourne les valeurs calculées

    # Méthode : Formate les grands nombres en notation scientifique
    def format_scientific(self, value: float) -> str:
        """Formate les grands nombres en notation scientifique."""
        return f"{value:.2e}"     # Retourne le nombre avec 2 décimales en notation scientifique (ex : 1.23e4)

    # Méthode : Résout la grille selon la méthode sélectionnée
    def solve_grid(self):
        if self.is_solving or not self.selected_method or not self.selected_grid:  # Vérifie si on peut résoudre
            return                # Ne fait rien si conditions non remplies
        
        self.is_solving = True    # Indique que la résolution commence
        self.status_label.config(text="Résolution en cours...")  # Met à jour le statut
        
        def solve_thread():       # Fonction exécutée dans un fil parallèle
            temp_board = deepcopy(self.original_board)  # Crée une copie de la grille originale
            start_time = time.time()  # Enregistre le temps de départ
            success = self.solver.solve_fast(temp_board)  # Résout avec backtracking
            solve_time = time.time() - start_time  # Calcule le temps écoulé
            
            if not success:       # Si aucune solution n’est trouvée
                self.root.after(0, lambda: self.status_label.config(text="Aucune solution trouvée!"))  # Met à jour le statut
                self.is_solving = False  # Indique que la résolution est terminée
                return            # Quitte la fonction
            
            visualize = self.selected_method == "visualize"  # Vérifie si la méthode est "visualisation"
            if not visualize:     # Si méthode rapide
                self.board = temp_board  # Met à jour la grille avec la solution
                for i in range(GRID_SIZE):  # Parcours les lignes
                    for j in range(GRID_SIZE):  # Parcours les colonnes
                        if self.original_board[i][j] == 0:  # Si la cellule était vide à l’origine
                            self.update_cell(i, j, self.board[i][j], COLORS['solved'])  # Affiche la solution en vert
            else:                 # Si méthode visualisation
                self.board = deepcopy(self.original_board)  # Réinitialise la grille
                self._visualize_solution(self.board)  # Visualise la résolution étape par étape
            
            empty_cells = self.solver.count_empty_cells(self.original_board)  # Compte les cellules vides
            operations = empty_cells * 9  # Estime le nombre d’opérations (9 essais par cellule)
            speed = operations / solve_time if solve_time > 0 else 0  # Calcule la vitesse en opérations/seconde
            centuries, years, months, combinations = self.calculate_brute_force_time()  # Calcule le temps brute
            
            self.root.after(0, lambda: [  # Met à jour l’interface après résolution
                self.status_label.config(text="Résolu!"),  # Affiche "Résolu!"
                self.backtracking_time_label.config(  # Affiche le temps backtracking
                    text=f"Temps Backtracking: {solve_time:.4f} secondes"),
                self.brute_force_label.config(  # Affiche l’estimation force brute
                    text=f"Force Brute estimée: ~{self.format_scientific(centuries)} siècles | "
                         f"~{self.format_scientific(years)} années | ~{self.format_scientific(months)} mois"),
                self.speed_label.config(  # Affiche la vitesse
                    text=f"Vitesse: ~{int(speed):,} opérations/s"),
                setattr(self, 'is_solving', False)  # Indique que la résolution est terminée
            ])
        
        threading.Thread(target=solve_thread, daemon=True).start()  # Lance la résolution dans un fil séparé

    # Méthode : Visualise la résolution étape par étape
    def _visualize_solution(self, board: List[List[int]]) -> bool:
        empty = self.solver.find_empty(board)  # Trouve une cellule vide
        if not empty:             # Si aucune cellule vide
            return True           # Retourne vrai (puzzle résolu)
        row, col = empty          # Récupère les coordonnées de la cellule vide
        
        for num in range(1, 10):  # Essaie les chiffres de 1 à 9
            if self.solver.is_valid(board, row, col, num):  # Vérifie si le chiffre est valide
                board[row][col] = num  # Place le chiffre
                self.root.after(0, lambda: self.update_cell(row, col, num, COLORS['solving']))  # Affiche en rouge
                self.root.update()    # Met à jour l’interface
                time.sleep(0.03)      # Pause de 0,03 seconde pour voir l’étape
                
                if self._visualize_solution(board):  # Résout récursivement le reste
                    if self.original_board[row][col] == 0:  # Si la cellule était vide
                        self.update_cell(row, col, num, COLORS['solved'])  # Affiche en vert
                    return True       # Retourne vrai si résolu
                board[row][col] = 0   # Efface le chiffre (retour en arrière)
                self.root.after(0, lambda: self.update_cell(row, col, 0, COLORS['text']))  # Efface visuellement
                self.root.update()    # Met à jour l’interface
                time.sleep(0.03)      # Pause pour voir l’effacement
        return False              # Retourne faux si aucune solution

    # Méthode : Efface les résultats affichés
    def clear_results(self):
        self.backtracking_time_label.config(text="")  # Efface le temps backtracking
        self.brute_force_label.config(text="")  # Efface l’estimation force brute
        self.speed_label.config(text="")  # Efface la vitesse

# Section : Grilles prédéfinies de Sudoku
sudoku_grids = {              # Dictionnaire contenant 5 grilles prédéfinies
    "1": [[0, 7, 2, 9, 0, 0, 0, 3, 0], [0, 0, 1, 0, 0, 6, 0, 8, 0], [0, 0, 0, 0, 4, 0, 0, 6, 0],  # Grille 1
          [9, 6, 0, 0, 0, 4, 1, 0, 8], [0, 4, 8, 7, 0, 5, 0, 9, 6], [0, 0, 5, 6, 0, 8, 0, 0, 3],
          [0, 0, 0, 4, 0, 2, 0, 1, 0], [8, 5, 0, 0, 6, 0, 3, 2, 7], [1, 0, 0, 8, 5, 0, 0, 0, 0]],
    "2": [[7, 0, 0, 9, 2, 0, 4, 0, 0], [0, 0, 0, 0, 0, 0, 7, 0, 0], [0, 0, 4, 0, 0, 8, 3, 1, 2],  # Grille 2
          [4, 0, 0, 0, 0, 2, 5, 0, 0], [2, 0, 0, 0, 1, 0, 0, 0, 3], [0, 0, 8, 5, 0, 0, 0, 0, 4],
          [8, 4, 3, 2, 0, 0, 6, 0, 0], [0, 0, 5, 0, 0, 0, 0, 0, 0], [0, 0, 2, 0, 6, 4, 0, 0, 5]],
    "3": [[0, 0, 9, 0, 8, 5, 0, 6, 3], [0, 7, 0, 9, 6, 0, 0, 0, 0], [5, 0, 1, 0, 0, 4, 0, 0, 0],  # Grille 3
          [0, 0, 6, 7, 0, 3, 0, 0, 4], [0, 4, 0, 2, 1, 0, 3, 9, 0], [8, 0, 0, 0, 9, 0, 0, 5, 7],
          [9, 8, 4, 5, 0, 0, 6, 0, 0], [0, 0, 7, 6, 4, 9, 0, 3, 0], [6, 1, 0, 0, 2, 0, 0, 4, 0]],
    "4": [[3, 0, 0, 0, 0, 0, 0, 8, 0], [0, 0, 0, 6, 0, 3, 0, 0, 2], [5, 6, 0, 0, 0, 0, 0, 0, 0],  # Grille 4
          [0, 8, 0, 1, 0, 0, 9, 7, 0], [0, 0, 0, 5, 0, 0, 0, 0, 0], [2, 0, 9, 0, 0, 4, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 6, 2, 0], [0, 0, 0, 0, 0, 0, 0, 4, 3], [0, 7, 0, 0, 5, 0, 1, 0, 0]],
    "5": [[0, 0, 9, 0, 6, 0, 0, 0, 0], [0, 0, 0, 3, 0, 0, 0, 1, 0], [0, 4, 5, 0, 1, 0, 0, 0, 6],  # Grille 5
          [0, 0, 0, 0, 0, 8, 2, 0, 0], [0, 6, 1, 0, 3, 0, 0, 0, 5], [7, 0, 0, 0, 0, 0, 0, 0, 0],
          [9, 0, 0, 0, 4, 0, 0, 0, 0], [0, 7, 4, 2, 0, 0, 5, 0, 0], [3, 0, 0, 0, 0, 0, 0, 0, 7]]
}

# Section : Point d’entrée du programme
if __name__ == "__main__":
    root = tk.Tk()            # Crée la fenêtre principale
    app = SudokuGUI(root)     # Crée une instance de l’interface SudokuGUI
    root.mainloop()           # Lance la boucle principale de l’interface graphique