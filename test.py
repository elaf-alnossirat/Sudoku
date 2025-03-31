import time
import pygame

# 🎨 Paramètres d'affichage
WIDTH, HEIGHT = 540, 600
CELL_SIZE = WIDTH // 9
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (50, 50, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# 🎯 Grille de Sudoku à résoudre
grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

class SudokuSolver:
    def __init__(self, grid):
        self.grid = grid
        pygame.init()
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sudoku Solver 🧩")
        self.font = pygame.font.Font(None, 40)

    def draw_grid(self):
        """ Dessine la grille de Sudoku """
        self.win.fill(WHITE)
        
        for i in range(10):
            thickness = 3 if i % 3 == 0 else 1
            pygame.draw.line(self.win, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), thickness)
            pygame.draw.line(self.win, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), thickness)
        
        # Remplir la grille avec les valeurs
        for row in range(9):
            for col in range(9):
                num = self.grid[row][col]
                if num != 0:
                    color = BLACK  # Valeur initiale en noir
                    text = self.font.render(str(num), True, color)
                    self.win.blit(text, (col * CELL_SIZE + 20, row * CELL_SIZE + 15))

    def draw_number(self, row, col, num, color=BLUE):
        """ Dessine un nombre dans la case donnée """
        pygame.draw.rect(self.win, WHITE, (col * CELL_SIZE + 5, row * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10))
        text = self.font.render(str(num), True, color)
        self.win.blit(text, (col * CELL_SIZE + 20, row * CELL_SIZE + 15))
        pygame.display.update()
        time.sleep(0.1)  # Petite pause pour l'animation

    def is_valid(self, row, col, num):
        """ Vérifie si 'num' peut être placé à (row, col) """
        for i in range(9):
            if self.grid[row][i] == num or self.grid[i][col] == num:
                return False

        box_x, box_y = row // 3 * 3, col // 3 * 3
        for i in range(3):
            for j in range(3):
                if self.grid[box_x + i][box_y + j] == num:
                    return False
        return True

    def find_empty(self):
        """ Trouve une case vide """
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    return (i, j)
        return None

    def solve(self):
        """ Applique le backtracking et affiche l'animation """
        empty_cell = self.find_empty()
        if not empty_cell:
            return True  # Sudoku résolu

        row, col = empty_cell
        for num in range(1, 10):
            if self.is_valid(row, col, num):
                self.grid[row][col] = num
                self.draw_number(row, col, num, BLUE)  # Animation

                if self.solve():
                    return True
                
                self.grid[row][col] = 0  # Backtrack
                self.draw_number(row, col, 0, RED)  # Effacer le chiffre faux

        return False  # Aucun chiffre valide, backtrack

    def run(self):
        """ Lance l'affichage de la résolution """
        running = True
        while running:
            self.draw_grid()
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            self.solve()
            time.sleep(10)
            running = False

        pygame.quit()

# Lancer le Sudoku Solver
solver = SudokuSolver(grid)
solver.run()