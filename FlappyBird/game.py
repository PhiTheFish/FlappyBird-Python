import pygame, random, os; from sys import exit

# Settings
WIDTH, HEIGHT = 480, 853
GRAVITY, JUMP_FORCE, PIPE_SPEED, PIPE_GAP = 0.4, -6, -2, 853 // 4

class Bird:
    def __init__(self, img):
        self.img = img
        self.rect = self.img.get_rect(center=(WIDTH // 8, HEIGHT // 2))
        self.velocity = 0

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += self.velocity
        if self.rect.top < 0: self.rect.top = 0

    def draw(self, surf):
        rot = pygame.transform.rotate(self.img, -self.velocity * 3)
        surf.blit(rot, rot.get_rect(center=self.rect.center))

class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Load Assets
        self.bg = pygame.image.load("flappybirdbg.png")
        self.logo = pygame.transform.scale(pygame.image.load("logo.png"), (400, 200))
        self.bird_img = pygame.transform.scale(pygame.image.load("flappybird.png"), (34, 24))
        self.top_pipe_img = pygame.transform.scale(pygame.image.load("toppipe.png"), (64, 512))
        self.bottom_pipe_img = pygame.transform.scale(pygame.image.load("bottompipe.png"), (64, 512))
        
        self.jump_sound, self.hit_sound, self.point_sound = [pygame.mixer.Sound(f"{s}.mp3") for s in ["jump", "hit", "point"]]
        self.font_big, self.font_small = pygame.font.Font("Font.ttf", 32), pygame.font.Font("Font.ttf", 16)
        
        self.high_score = self.load_high_score()
        self.state = "MENU"
        self.CREATE_PIPE = pygame.USEREVENT
        pygame.time.set_timer(self.CREATE_PIPE, 1500)
        self.reset()

    def load_high_score(self):
        try:
            return int(open("highscore.txt").read())
        except:
            return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(int(self.high_score)))

    def reset(self):
        self.bird, self.pipes, self.score = Bird(self.bird_img), [], 0

    def blit_text(self, txt, pos, font, color="white", center=False):
        surf = font.render(str(txt), True, color)
        rect = surf.get_rect(center=pos) if center else surf.get_rect(topleft=pos)
        self.window.blit(surf, rect)

    def update(self):
        if self.state != "PLAYING": return
        self.bird.update()
        if self.bird.rect.bottom > HEIGHT: self.game_over()

        for p in self.pipes:
            p['rect'].x += PIPE_SPEED
            if not p['passed'] and self.bird.rect.left > p['rect'].right:
                self.score += 0.5
                p['passed'] = True
                if p['type'] == 'bottom':
                    self.point_sound.play()
            if self.bird.rect.colliderect(p['rect']): self.game_over()
        
        self.pipes = [p for p in self.pipes if p['rect'].right > 0]

    def game_over(self):
        self.hit_sound.play()
        self.state = "GAME_OVER"
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def draw(self):
        self.window.blit(self.bg, (0, 0))
        if self.state == "MENU":
            self.window.blit(self.logo, self.logo.get_rect(center=(WIDTH//2, 250)))
            self.blit_text("Nhấn SPACE để bắt đầu", (WIDTH // 2, 500), self.font_small, center=True)
        elif self.state in ["PLAYING", "PAUSE", "GAME_OVER"]:
            for p in self.pipes: self.window.blit(p['img'], p['rect'])
            self.bird.draw(self.window)
            self.blit_text(int(self.score), (WIDTH // 2, 50), self.font_big, center=True)
            
            if self.state == "PAUSE":
                self.blit_text("TẠM DỪNG", (WIDTH // 2, HEIGHT // 2), self.font_big, center=True)
            elif self.state == "GAME_OVER":
                self.blit_text("GAME OVER", (WIDTH // 2, 250), self.font_big, "red", True)
                self.blit_text(f"Điểm cao: {int(self.high_score)}", (WIDTH // 2, 400), self.font_small, "yellow", True)
                self.blit_text("Nhấn SPACE để chơi lại", (WIDTH // 2, 500), self.font_small, center=True)
        pygame.display.update()

    def run(self):
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: exit()
                if e.type == self.CREATE_PIPE and self.state == "PLAYING":
                    y = -random.randint(100, 300)
                    self.pipes.append({
                        'rect': self.top_pipe_img.get_rect(topleft=(WIDTH, y)),
                        'img': self.top_pipe_img,
                        'type': 'top',
                        'passed': False
                    })
                    self.pipes.append({
                        'rect': self.bottom_pipe_img.get_rect(topleft=(WIDTH, y + 512 + PIPE_GAP)),
                        'img': self.bottom_pipe_img,
                        'type': 'bottom',
                        'passed': False
                    })
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE:
                        if self.state == "PLAYING":
                            self.bird.velocity = JUMP_FORCE
                            self.jump_sound.play()
                        else: self.reset(); self.state = "PLAYING"
                    if e.key == pygame.K_p and self.state in ["PLAYING", "PAUSE"]:
                        self.state = "PAUSE" if self.state == "PLAYING" else "PLAYING"
            self.update(); self.draw(); self.clock.tick(60)

if __name__ == "__main__": Game().run() 