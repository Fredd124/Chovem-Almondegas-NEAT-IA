import pygame
import os
import random
import neat
import pickle

pygame.font.init()

# Load images
bg_img = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs","1709.jpg")),1/5)
boy_img_left = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs","flint.png")),1/4)
boy_img_right = pygame.transform.flip(boy_img_left, True, False)
object_img = pygame.transform.scale_by(pygame.image.load(os.path.join("imgs","pork-meatball-1.png")),1/7)

# Declare constants
WIN_WIDTH = bg_img.get_width()
WIN_HEIGHT = bg_img.get_height()
STAT_FONT = pygame.font.SysFont("comicsans", 50)

# Used to keep track of generations number
gen = 0



class Boy:
    """
    Boy class representing the character
    """
    IMGS = [boy_img_right,boy_img_left]

    def __init__(self,x,y):
        """
        Initialize the object
        :param x: starting x position (int)
        :param y: starting y position (int) 
        :return: None       
        """
        self.x = x
        self.y = y
        self.turn = False
        self.img = self.IMGS[0]

    def move(self, distance):
        """
        make the boy move
        :param distance: ditance to move (int)
        :return: None
        """
        self.x += distance

    def draw(self, win):
        """
        draw the boy
        :param win: pygame window or surface
        :return: None
        """
        
        # Invert image if he moves in the opposite direction
        if self.turn == False:
            self.img = self.IMGS[0]
        else:
            self.img = self.IMGS[1]

        # Draw the boy
        win.blit(self.img, (self.x,self.y))

    def get_mask(self):
        """
        get boy image mask for collision test
        :return: boy mask
        """
        return pygame.mask.from_surface(self.img)



class Meatball:
    """
    Represents the objects falling from the sky
    """

    def __init__(self,x,y):
        """
        Initialize the object
        :param x: starting x position (int)
        :param y: starting y position (int) 
        :return: None       
        """
        self.x = x
        self.y = y
        self.img = object_img

    def move(self, vel):
        """
        make the meatball fall
        :param vel: velocity corresponding to the falling object (int)
        :return: None
        """
        self.y = self.y + vel

    def draw(self, win):
        """
        draw the meatball
        :param win: pygame window or surface
        :return: None
        """
        win.blit(self.img, (self.x,self.y))

    def get_mask(self):
        """
        get meatball image mask for collision test
        :return: meatball mask
        """
        return pygame.mask.from_surface(self.img)
    
    def collide(self, character):
        """
        returns if a point is colliding with the meatball
        :param character: Boy object
        :return: Bool
        """

        # Get both masks
        character_mask = character.get_mask()
        meatball_mask = self.get_mask()
        offset = (self.x-character.x, self.y-character.y)
 
        # Check if the masks are overlapping
        collision_point = character_mask.overlap(meatball_mask,offset)
        
        if collision_point:
            return True

        return False
    


def draw_window(win, boys, obj, score, gen, alive):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param boys: a list of Boy object
    :param obj: Meatball object
    :param score: score of the game (int)
    :param gen: current generation
    :param alive: how many boys are alive
    :return: None
    """

    # Draw background image and meatball
    win.blit(bg_img, (0,0))
    obj.draw(win)

    # Score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # Generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # Alive
    score_label = STAT_FONT.render("Alive: " + str(alive),1,(255,255,255))
    win.blit(score_label, (10, 50))

    # Draw boys
    for boy in boys:
        boy.draw(win)
    
    pygame.display.update()



def eval_genomes(genomes, config):
    """
    runs the simulation of the current population of
    boys and sets their fitness based on the score they
    get in the game.
    """

    # Used to keep track of the current generation number
    global gen
    gen += 1

    # Start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # boy object that uses that network to play
    nets = []
    ge = []
    boys = []
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        boys.append(Boy(WIN_WIDTH//2,WIN_HEIGHT-200))
        g.fitness = 0
        ge.append(g)

    # Set pygame window size
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    
    meatball = Meatball(150,0)
    clock = pygame.time.Clock()

    vel = 30
    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # If there are no more boys, end the generation
        if len(boys) == 0:
            run = False
            break

        # For each boy, update their fitness for staying alive
        for x, boy in enumerate(boys):
            ge[x].fitness += 0.1

            # Provide each neural node with the distances between the boy, meatball and the end of the terrain
            output = nets[x].activate((boy.y, meatball.y, abs(boy.x - meatball.x), abs(boy.y - meatball.y),\
                                        abs(boy.x - 0), abs(boy.x-WIN_WIDTH-boy_img_left.get_width())))
            
            decision = output.index(max(output))

            # If the index is 0, stay still
            # If the index is 1, move right
            # If the index is 2, move left
            if decision == 0:
                pass
            elif decision == 1:
                boy.move(10)
            else:
                boy.move(-10)
        
        # If the meatball reachees the ground, "create" another one and update
        # both fitness of the boys alive and the score
        if meatball.y >= WIN_HEIGHT-90:
            meatball.y = 0
            meatball.x = random.randrange(0,WIN_WIDTH-object_img.get_width())
            score += 1
            for g in ge:
                g.fitness += 2
    
        # Check for collision with each boy and the meatball. Penalize those who have collided
        # and remove them from the boys "alive"
        for x, boy in enumerate(boys):
            if meatball.collide(boy) == True:
                ge[x].fitness -= 1
                boys.pop(x)
                nets.pop(x)
                ge.pop(x)

        # If a boy reaches the end of the map, it is penalized and removed from the list
        # of boys "alive"
        for x, boy in enumerate(boys):
            if boy.x >= WIN_WIDTH-boy_img_left.get_width() or boy.x <= 0:
                ge[x].fitness -= 5
                boys.pop(x)
                nets.pop(x)
                ge.pop(x)

        # If the score reaches 300, the AI is considered good enough
        if  score == 300:
            break

        # Make the meatball move
        meatball.move(vel)

        # Draw the pygame window
        draw_window(win, boys, meatball,score, gen, len(boys))
        


def use_best_genome(genome, config):
    global  gen
    gen += 1

    # Recreate the neural network for the previous best genome
    net = neat.nn.FeedForwardNetwork.create(genome,config)

    nets = [net]
    ge = [genome]
    boys = [Boy(WIN_WIDTH//2,WIN_HEIGHT-200)]

    # Set pygame window size
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    
    meatball = Meatball(150,0)
    clock = pygame.time.Clock()
    
    vel = 30
    score = 0

    run = True
    while run:
        clock.tick(30)
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

            output = nets[x].activate((boy.y, meatball.y, abs(boy.x - meatball.x), abs(boy.y - meatball.y),\
                                        abs(boy.x - 0), abs(boy.x-WIN_WIDTH-boy_img_left.get_width())))
            
            decision = output.index(max(output))

            if decision == 0:
                pass
            elif decision == 1:
                boy.move(10)
            else:
                boy.move(-10)

        if meatball.y >= WIN_HEIGHT-90:
            meatball.y = 0
            meatball.x = random.randrange(0,WIN_WIDTH-object_img.get_width())
            score += 1
            for g in ge:
                g.fitness += 2

        for x, boy in enumerate(boys):
            if meatball.collide(boy) == True:
                ge[x].fitness -= 1
                boys.pop(x)
                nets.pop(x)
                ge.pop(x)

        for x, boy in enumerate(boys):
            if boy.x >= WIN_WIDTH-boy_img_left.get_width() or boy.x <= 0:
                ge[x].fitness -= 5
                boys.pop(x)
                nets.pop(x)
                ge.pop(x)

        if  score == 300:
            break

        meatball.move(vel)
        draw_window(win, boys, meatball,score, gen, len(boys))



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

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # Show final stats
    print('\nBest genome:\n{!s}'.format(winner))
    
    # Save the best genome so it can be used later
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)



def test_best_ai(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    
    # Opens the previously saved best genome
    # "best.pickle" currently holds a AI previously trained
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)

    use_best_genome(winner,config)



if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    
    # If we don´t have the model train we choose the run function. If we 
    # already have a trained genome, we use the test_best_ai function
    #run(config_path)
    test_best_ai(config_path)
