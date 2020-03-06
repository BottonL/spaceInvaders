import pygame
import random
import time
import sqlite3

conn = sqlite3.connect('space.db')


cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS resultat(
     id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
     username TEXT,
     score INTEGER
)
""")
conn.commit()


cols = 7
rows = 5

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
 
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 800

ENEMY_IMG = pygame.image.load('enemy.png')
UFO_IMG = pygame.image.load('ufo.png')
 
class Laser(pygame.sprite.Sprite):
    def __init__(self, Block, direction):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = Block.rect.x + 2
        self.rect.y = Block.rect.y
        self.direction = direction

    def reset_pos(self):
        pass
    
    def update(self):
        if self.direction == "down":
            self.rect.y += 5
        elif self.direction == "up":
            self.rect.y -= 5
        if self.rect.y > SCREEN_HEIGHT + self.rect.height:
            self.reset_pos()
        
        
class Block(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        #self.image = pygame.Surface([20, 20])
        self.image = ENEMY_IMG
        #self.image.fill(BLACK)
        self.rect = self.image.get_rect()
 
    def reset_pos(self):
        pass

    def update(self):
        if self.rect.y > SCREEN_HEIGHT + self.rect.height:
            self.reset_pos()
 
 
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        #self.image = pygame.Surface([20, 20])
        self.image = UFO_IMG
        #self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = (SCREEN_WIDTH - self.rect.width) / 2
        self.rect.y = (SCREEN_HEIGHT - self.rect.height ) - 10
    
    def reset_pos(self):
        self.rect.x = SCREEN_WIDTH / 2 - self.rect.width

    def update(self):
        pressed_key = pygame.key.get_pressed()
        if pressed_key[pygame.K_LEFT]:
            self.rect.x -= 5
        elif pressed_key[pygame.K_RIGHT]:
            self.rect.x += 5
 
class Game(object):
    def __init__(self):
        self.score = 0
        self.game_over = False
        self.enemies_rows = rows
        self.enemies_cols = cols
        self.lastshoot = time.time()
        self.block_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
 
        y = 5
        for row in range(self.enemies_rows):
            x = 20
            for col in range(self.enemies_cols):
                block = Block()

                block.rect.x = x
                block.rect.y = y
    
                self.block_list.add(block)
                self.all_sprites_list.add(block)
                x += 85
            y += 50
 
        self.player = Player()
        self.all_sprites_list.add(self.player)
 
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    self.__init__()
 
        return False
 
    def run_logic(self):
        if not self.game_over:
            self.all_sprites_list.update()
            pressed_key = pygame.key.get_pressed()
            blocks_hit_list = pygame.sprite.spritecollide(self.player, self.block_list, True)

            for hit in blocks_hit_list:
                self.game_over = True
 
            for sprite in self.all_sprites_list:
                if "Laser" in str(sprite):
                    for block in self.block_list:
                        if sprite.rect.colliderect(block.rect):
                            block.rect.x = SCREEN_WIDTH + 10
                            block.rect.y = SCREEN_HEIGHT + 10
                            sprite.rect.x = SCREEN_WIDTH + 10
                            sprite.rect.y = SCREEN_HEIGHT + 10

                            self.score += 1
                            self.block_list.remove(block)
                            self.all_sprites_list.remove(sprite)

            for block in blocks_hit_list:
                self.score += 1
                print(self.score)

            r = random.randrange(0, 2)
            if r == 1:
                for block in self.block_list:
                    block.rect.y += 1
                    if block.rect.y > (SCREEN_HEIGHT - 30):
                        self.game_over = True
 
            if len(self.block_list) == 0:
                self.game_over = True

            if pressed_key[pygame.K_SPACE]:
                if time.time() - self.lastshoot > 0.5:
                    laser = Laser(self.player, "up")
                    self.all_sprites_list.add(laser)
                    self.lastshoot = time.time()
            
 
    def display_frame(self, screen):
        screen.fill(WHITE)
        if self.game_over:
            cursor.execute("""
            INSERT INTO resultat(username, score) VALUES(?, ?)""", ("USER", self.score))
            cursor.execute("""SELECT * FROM resultat""")
            users = cursor.fetchall()

            font = pygame.font.SysFont("serif", 25)
            text = font.render("GAME OVER. SCORE: " + str(self.score), True, BLACK)
            text2 = font.render("Cliquez pour redémarrer", True, GREEN)
            center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) - (text.get_height() // 2)
            screen.blit(text, [center_x, center_y])
            screen.blit(text2, [center_x, center_y + 40])
            
 
        if not self.game_over:
            self.all_sprites_list.draw(screen)
            font = pygame.font.SysFont("serif", 25)
            score_text = font.render("SCORE: " + str(self.score), True, RED)
            screen.blit(score_text, [10, 10])

 
        pygame.display.flip()
 
 
def main():
    pygame.init()
 
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
 
    pygame.display.set_caption("My Game")
    pygame.mouse.set_visible(False)
    done = False
    clock = pygame.time.Clock()
    game = Game()

    while not done:
        done = game.process_events()
        game.run_logic()
        game.display_frame(screen)
        clock.tick(60)
    pygame.quit()
 
if __name__ == "__main__":
    main()