import pygame
import random
import sys

# 초기화
pygame.init()

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

# 게임 설정
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
GRID_X_OFFSET = 50
GRID_Y_OFFSET = 50

SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE + GRID_X_OFFSET * 2 + 200
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + GRID_Y_OFFSET * 2

# 테트리스 조각 정의 (I, O, T, S, Z, J, L)
SHAPES = [
    # I 조각
    [[1, 1, 1, 1]],
    # O 조각
    [[1, 1],
     [1, 1]],
    # T 조각
    [[0, 1, 0],
     [1, 1, 1]],
    # S 조각
    [[0, 1, 1],
     [1, 1, 0]],
    # Z 조각
    [[1, 1, 0],
     [0, 1, 1]],
    # J 조각
    [[1, 0, 0],
     [1, 1, 1]],
    # L 조각
    [[0, 0, 1],
     [1, 1, 1]]
]

SHAPE_COLORS = [CYAN, YELLOW, PURPLE, GREEN, RED, BLUE, ORANGE]

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_shape_index = 0
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_time = 0
        self.fall_speed = 500  # 밀리초
        self.game_over = False
        self.spawn_new_piece()
    
    def spawn_new_piece(self):
        self.current_shape_index = random.randint(0, len(SHAPES) - 1)
        self.current_piece = [row[:] for row in SHAPES[self.current_shape_index]]
        self.current_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0
        
        # 게임 오버 체크
        if self.check_collision(self.current_piece, self.current_x, self.current_y):
            self.game_over = True
    
    def rotate_piece(self):
        if self.current_piece is None:
            return
        
        # 90도 회전
        rotated = [[self.current_piece[y][x] 
                   for y in range(len(self.current_piece) - 1, -1, -1)]
                   for x in range(len(self.current_piece[0]))]
        
        if not self.check_collision(rotated, self.current_x, self.current_y):
            self.current_piece = rotated
    
    def check_collision(self, piece, x, y):
        for py, row in enumerate(piece):
            for px, cell in enumerate(row):
                if cell:
                    nx, ny = x + px, y + py
                    if nx < 0 or nx >= GRID_WIDTH or ny >= GRID_HEIGHT:
                        return True
                    if ny >= 0 and self.grid[ny][nx]:
                        return True
        return False
    
    def place_piece(self):
        for py, row in enumerate(self.current_piece):
            for px, cell in enumerate(row):
                if cell:
                    nx, ny = self.current_x + px, self.current_y + py
                    if ny >= 0:
                        self.grid[ny][nx] = SHAPE_COLORS[self.current_shape_index]
        
        # 완성된 줄 제거
        self.clear_lines()
        self.spawn_new_piece()
    
    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += len(lines_to_clear) * 100 * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 50)
    
    def move(self, dx, dy):
        if self.current_piece is None or self.game_over:
            return
        
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        
        if not self.check_collision(self.current_piece, new_x, new_y):
            self.current_x = new_x
            self.current_y = new_y
            return True
        elif dy > 0:  # 아래로 이동 실패 시 배치
            self.place_piece()
        return False
    
    def drop(self):
        while self.move(0, 1):
            pass
    
    def update(self, dt):
        if self.game_over:
            return
        
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.move(0, 1)
            self.fall_time = 0

def draw_grid(screen):
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(screen, GRAY,
                        (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET),
                        (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET + GRID_HEIGHT * CELL_SIZE))
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(screen, GRAY,
                        (GRID_X_OFFSET, GRID_Y_OFFSET + y * CELL_SIZE),
                        (GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE, GRID_Y_OFFSET + y * CELL_SIZE))

def draw_piece(screen, piece, x, y, color):
    for py, row in enumerate(piece):
        for px, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(
                    GRID_X_OFFSET + (x + px) * CELL_SIZE + 1,
                    GRID_Y_OFFSET + (y + py) * CELL_SIZE + 1,
                    CELL_SIZE - 2,
                    CELL_SIZE - 2
                )
                pygame.draw.rect(screen, color, rect)

def draw_board(screen, game):
    # 배경
    screen.fill(BLACK)
    
    # 게임 보드 배경
    board_rect = pygame.Rect(
        GRID_X_OFFSET - 5,
        GRID_Y_OFFSET - 5,
        GRID_WIDTH * CELL_SIZE + 10,
        GRID_HEIGHT * CELL_SIZE + 10
    )
    pygame.draw.rect(screen, WHITE, board_rect, 2)
    
    # 그리드 그리기
    draw_grid(screen)
    
    # 배치된 조각들 그리기
    for y, row in enumerate(game.grid):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(
                    GRID_X_OFFSET + x * CELL_SIZE + 1,
                    GRID_Y_OFFSET + y * CELL_SIZE + 1,
                    CELL_SIZE - 2,
                    CELL_SIZE - 2
                )
                pygame.draw.rect(screen, cell, rect)
    
    # 현재 조각 그리기
    if game.current_piece:
        draw_piece(screen, game.current_piece, game.current_x, game.current_y,
                  SHAPE_COLORS[game.current_shape_index])
    
    # 점수 및 정보 표시
    font = pygame.font.Font(None, 36)
    info_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 20
    
    score_text = font.render(f"점수: {game.score}", True, WHITE)
    screen.blit(score_text, (info_x, GRID_Y_OFFSET))
    
    level_text = font.render(f"레벨: {game.level}", True, WHITE)
    screen.blit(level_text, (info_x, GRID_Y_OFFSET + 40))
    
    lines_text = font.render(f"줄: {game.lines_cleared}", True, WHITE)
    screen.blit(lines_text, (info_x, GRID_Y_OFFSET + 80))
    
    # 조작법 표시
    small_font = pygame.font.Font(None, 24)
    controls = [
        "조작법:",
        "← → : 이동",
        "↑ : 회전",
        "↓ : 빠르게",
        "스페이스: 즉시 낙하"
    ]
    for i, text in enumerate(controls):
        control_text = small_font.render(text, True, WHITE)
        screen.blit(control_text, (info_x, GRID_Y_OFFSET + 140 + i * 25))
    
    # 게임 오버 메시지
    if game.game_over:
        game_over_font = pygame.font.Font(None, 48)
        game_over_text = game_over_font.render("게임 오버!", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(game_over_text, text_rect)
        
        restart_text = small_font.render("R키를 눌러 재시작", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        screen.blit(restart_text, restart_rect)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("테트리스")
    clock = pygame.time.Clock()
    
    game = Tetris()
    
    running = True
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game.game_over:
                    if event.key == pygame.K_r:
                        game = Tetris()
                else:
                    if event.key == pygame.K_LEFT:
                        game.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        game.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        game.move(0, 1)
                    elif event.key == pygame.K_UP:
                        game.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        game.drop()
        
        game.update(dt)
        draw_board(screen, game)
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

