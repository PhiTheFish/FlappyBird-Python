import pygame
import random
import os
from sys import exit

# setting của game
WIDTH = 480
HEIGHT = 853

GRAVITY = 0.4
JUMP_FORCE = -6
PIPE_SPEED = -2
PIPE_GAP = HEIGHT // 4

# class bird
class Bird:
    def __init__(self, img):
        self.img = img
        self.rect = self.img.get_rect(center=(WIDTH // 8, HEIGHT // 2))
        self.velocity = 0

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += self.velocity

        if self.rect.top < 0:
            self.rect.top = 0

    def jump(self):
        self.velocity = JUMP_FORCE

    def draw(self, surface):
        rotated = pygame.transform.rotate(self.img, -self.velocity * 3)
        surface.blit(rotated, rotated.get_rect(center=self.rect.center))


# class pipe
class Pipe:
    def __init__(self, x, y, img):
        self.img = img
        self.rect = self.img.get_rect(topleft=(x, y))
        self.passed = False

    def update(self):
        self.rect.x += PIPE_SPEED

    def draw(self, surface):
        surface.blit(self.img, self.rect)


# game
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy Bird Pro")
        self.clock = pygame.time.Clock()

        # load images
        self.bg = pygame.image.load("flappybirdbg.png")

        self.logo = pygame.image.load("logo.png")
        self.logo = pygame.transform.scale(self.logo, (400, 200))

        self.bird_img = pygame.transform.scale(
            pygame.image.load("flappybird.png"), (34, 24)
        )

        self.top_pipe_img = pygame.transform.scale(
            pygame.image.load("toppipe.png"), (64, 512)
        )

        self.bottom_pipe_img = pygame.transform.scale(
            pygame.image.load("bottompipe.png"), (64, 512)
        )

        # load sounds
        self.jump_sound = pygame.mixer.Sound("jump.mp3")
        self.hit_sound = pygame.mixer.Sound("hit.mp3")
        self.point_sound = pygame.mixer.Sound("point.mp3")

        # font
        self.font_big = pygame.font.Font("Font.ttf", 32)
        self.font_small = pygame.font.Font("Font.ttf", 16)

        self.high_score = self.load_high_score()

        self.state = "MENU"  # MENU, PLAYING, GAME_OVER, PAUSE

        self.reset()

        self.CREATE_PIPE = pygame.USEREVENT
        pygame.time.set_timer(self.CREATE_PIPE, 1500)

    def load_high_score(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as f:
                return int(f.read())
        return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(int(self.high_score)))

    def reset(self):
        self.bird = Bird(self.bird_img)
        self.pipes = []
        self.score = 0

    def create_pipes(self):
        y = -random.randint(100, 300)

        self.pipes.append(Pipe(WIDTH, y, self.top_pipe_img))
        self.pipes.append(
            Pipe(WIDTH, y + self.top_pipe_img.get_height() + PIPE_GAP, self.bottom_pipe_img)
        )

    def update(self):
        if self.state != "PLAYING":
            return

        self.bird.update()

        if self.bird.rect.bottom > HEIGHT:
            self.game_over()

        for pipe in self.pipes:
            pipe.update()

            if not pipe.passed and self.bird.rect.left > pipe.rect.right:
                self.score += 0.5
                pipe.passed = True

                if pipe.img == self.bottom_pipe_img:
                    self.point_sound.play()

            if self.bird.rect.colliderect(pipe.rect):
                self.game_over()

        self.pipes = [p for p in self.pipes if p.rect.right > 0]

    def game_over(self):
        self.hit_sound.play()
        self.state = "GAME_OVER"

        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def draw(self):
        self.window.blit(self.bg, (0, 0))

        if self.state == "MENU":
            self.draw_menu()

        elif self.state == "PLAYING":
            self.bird.draw(self.window)
            for pipe in self.pipes:
                pipe.draw(self.window)
            self.draw_score()

        elif self.state == "PAUSE":
            self.draw_pause()

        elif self.state == "GAME_OVER":
            self.draw_game_over()

        pygame.display.update()

    def draw_score(self):
        text = self.font_big.render(str(int(self.score)), True, "white")
        self.window.blit(text, (WIDTH // 2 - 20, 50))

    def draw_menu(self):
        # nền
        self.window.blit(self.bg, (0, 0))

        # logo
        logo_rect = self.logo.get_rect(center=(WIDTH // 2, 250))
        self.window.blit(self.logo, logo_rect)

        # text
        text = self.font_small.render("Nhấn SPACE để bắt đầu", True, "white")
        text_rect = text.get_rect(center=(WIDTH // 2, 500))
        self.window.blit(text, text_rect)

    def draw_pause(self):
        text = self.font_big.render("TẠM DỪNG", True, "white")
        self.window.blit(text, (150, 400))

    def draw_game_over(self):
        # Thua
        over = self.font_big.render("GAME OVER", True, "red")
        over_rect = over.get_rect(center=(WIDTH // 2, 250))
        self.window.blit(over, over_rect)

        # Điểm
        score = self.font_small.render(f"Điểm: {int(self.score)}", True, "white")
        score_rect = score.get_rect(center=(WIDTH // 2, 350))
        self.window.blit(score, score_rect)

        # Điểm cao
        high = self.font_small.render(f"Điểm cao: {int(self.high_score)}", True, "yellow")
        high_rect = high.get_rect(center=(WIDTH // 2, 400))
        self.window.blit(high, high_rect)

        hint = self.font_small.render("Nhấn SPACE để bắt đầu lại", True, "white")
        hint_rect = hint.get_rect(center=(WIDTH // 2, 500))
        self.window.blit(hint, hint_rect)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == self.CREATE_PIPE and self.state == "PLAYING":
            self.create_pipes()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == "MENU":
                    self.state = "PLAYING"
                elif self.state == "GAME_OVER":
                    self.reset()
                    self.state = "PLAYING"
                elif self.state == "PLAYING":
                    self.bird.jump()
                    self.jump_sound.play()

            if event.key == pygame.K_p:
                if self.state == "PLAYING":
                    self.state = "PAUSE"
                elif self.state == "PAUSE":
                    self.state = "PLAYING"

    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)

            self.update()
            self.draw()
            self.clock.tick(60)


#main
if __name__ == "__main__":
    Game().run()