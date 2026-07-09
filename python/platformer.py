import pygame
import sys

WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_SPEED = -12
MOVE_SPEED = 5

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
BROWN = (139, 69, 19)
RED = (255, 50, 50)
GOLD = (255, 215, 0)


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.vx = 0
        self.vy = 0
        self.on_ground = False

    def update(self, platforms):
        self.rect.x += self.vx
        self.collide_x(platforms)

        self.vy += GRAVITY
        if self.vy > 15:
            self.vy = 15
        self.rect.y += self.vy

        self.on_ground = False
        self.collide_y(platforms)

    def collide_x(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vx > 0:
                    self.rect.right = p.left
                elif self.vx < 0:
                    self.rect.left = p.right

    def collide_y(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vy > 0:
                    self.rect.bottom = p.top
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = p.bottom
                self.vy = 0

    def jump(self):
        if self.on_ground:
            self.vy = JUMP_SPEED

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)
        pygame.draw.circle(screen, WHITE, (self.rect.x + 8, self.rect.y + 10), 4)
        pygame.draw.circle(screen, WHITE, (self.rect.x + 22, self.rect.y + 10), 4)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Платформер")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset()

    def reset(self):
        platforms = [
            (0, 550, 800, 50),
            (100, 470, 100, 20),
            (250, 400, 100, 20),
            (150, 330, 100, 20),
            (400, 440, 100, 20),
            (500, 370, 100, 20),
            (350, 300, 100, 20),
            (550, 240, 100, 20),
            (400, 170, 100, 20),
            (650, 130, 120, 20),
        ]
        self.platforms = [pygame.Rect(*p) for p in platforms]
        self.player = Player(50, 500)
        self.flag_rect = pygame.Rect(700, 90, 30, 40)
        self.won = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.won:
                        self.reset()
                    else:
                        self.player.jump()
                if event.key == pygame.K_r and self.won:
                    self.reset()
        return True

    def update(self):
        if self.won:
            return

        keys = pygame.key.get_pressed()
        self.player.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -MOVE_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = MOVE_SPEED

        self.player.update(self.platforms)

        if self.player.rect.y > HEIGHT + 50:
            self.reset()

        if self.player.rect.colliderect(self.flag_rect):
            self.won = True

    def draw(self):
        self.screen.fill(BLACK)

        for p in self.platforms:
            pygame.draw.rect(self.screen, BROWN, p)
            pygame.draw.rect(self.screen, (100, 50, 0), p, 2)

        pygame.draw.rect(self.screen, RED, self.flag_rect)
        pygame.draw.line(self.screen, GOLD,
                        (self.flag_rect.centerx, self.flag_rect.top),
                        (self.flag_rect.centerx, self.flag_rect.top - 30), 3)
        pygame.draw.polygon(self.screen, RED, [
            (self.flag_rect.centerx, self.flag_rect.top - 30),
            (self.flag_rect.centerx + 20, self.flag_rect.top - 15),
            (self.flag_rect.centerx, self.flag_rect.top)
        ])

        self.player.draw(self.screen)

        hint = self.font.render(
            "Стрелки / WASD — движение, Пробел — прыжок", True, WHITE)
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 10))

        if self.won:
            text = self.font.render(
                "ТЫ ПОБЕДИЛ! Пробел / R — заново", True, GOLD)
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
