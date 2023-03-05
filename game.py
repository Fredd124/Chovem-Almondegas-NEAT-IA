import pygame
import os
import random

pygame.font.init()


bg_img = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs","1709.jpg")),1/5)
boy_img_left = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs","flint.png")),1/4)
boy_img_right = pygame.transform.flip(boy_img_left, True, False)
object_img = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs","pork-meatball-1.png")),1/7)

WIN_WIDTH = bg_img.get_width()
WIN_HEIGHT = bg_img.get_height()
STAT_FONT = pygame.font.SysFont("comicsans", 50)


WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

class Boy:
    IMGS = [boy_img_right,boy_img_left]

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.horizontal = self.x
        self.turn = False
        self.img = self.IMGS[0]

    def draw(self, win):
        
        if self.turn == False:
            self.img = self.IMGS[0]
        else:
            self.img = self.IMGS[1]

        win.blit(self.img, (self.x,self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Meatball:
    
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.height = self.y
        self.vel = 0
        self.img = object_img

    def move(self, vel):
        self.y = self.y + vel

    def draw(self, win):
        win.blit(self.img, (self.x,self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    
    def collide(self, character):
        """
        returns if a point is colliding with the meatball
        :param bird: Boy object
        :return: Bool
        """
        character_mask = character.get_mask()
        meatball_mask = self.get_mask()
        offset = (self.x-character.x, self.y-character.y)

        collision_point = character_mask.overlap(meatball_mask,offset)
        
        if collision_point:
            return True

        return False
    

def draw_window(win, character, obj, score):
    win.blit(bg_img, (0,0))
    character.draw(win)
    obj.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    pygame.display.update()


def main():
    character = Boy(WIN_WIDTH//2,WIN_HEIGHT-200)
    meatball = Meatball(150,0)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    score = 0
    vel = 1

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            character.turn = True
            character.x -= 0.5
        
        if keys[pygame.K_RIGHT]:
            character.turn = False
            character.x += 0.5
        
        if meatball.y >= WIN_HEIGHT-90:
            meatball.y = 0
            meatball.x = random.randrange(object_img.get_width(),WIN_WIDTH-object_img.get_width())
            score += 1
            if score%5 == 0:
                vel += 0.1
        
        if meatball.collide(character) == True:
            run = False

    
        meatball.move(vel)
        draw_window(win, character, meatball,score)
        
    pygame.quit()
    quit()

main()