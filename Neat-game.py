import pygame
import os
import random
import neat

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

    def move(self, distance):
        self.x += distance

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
    

def draw_window(win, boys, obj, score):
    win.blit(bg_img, (0,0))
    obj.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    for boy in boys:
        boy.draw(win)
    
    pygame.display.update()


def eval_genomes(genomes, config):
    nets = []
    ge = []
    boys = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        boys.append(Boy(WIN_WIDTH//2,WIN_HEIGHT-200))
        g.fitness = 0
        ge.append(g)

    meatball = Meatball(150,0)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    vel = 5
    #clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        #clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        if len(boys) == 0:
            run = False
            break

        
        for x, boy in enumerate(boys):
            ge[x].fitness += 0.1

            output = nets[x].activate((boy.x, meatball.x, abs(boy.y - meatball.y)))
            decision = output.index(max(output))

            if decision == 0:
                pass
            elif decision == 1:
                boy.move(5)
            else:
                boy.move(-5)
        
        
        if meatball.y >= WIN_HEIGHT-90:
            meatball.y = 0
            meatball.x = random.randrange(object_img.get_width()-10,WIN_WIDTH-object_img.get_width())
            score += 1
            for g in ge:
                g.fitness += 2
            if score%5 == 0:
                vel += 0.5
        
        for x, boy in enumerate(boys):
            if meatball.collide(boy) == True:
                ge[x].fitness -= 1
                boys.pop(x)
                nets.pop(x)
                ge.pop(x)

        for x, boy in enumerate(boys):
            if boy.x > WIN_WIDTH or boy.x < 0:
                boys.pop(x)
                nets.pop(x)
                ge.pop(x)

        meatball.move(vel)
        draw_window(win, boys, meatball,score)
        
def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
