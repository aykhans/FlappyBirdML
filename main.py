# Import module
import sys
import pygame
from pygame.locals import *
import os
from itertools import cycle
import json

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# All the Game Variables
window_width = 600
window_height = 499

with open('data.json') as json_file:
    data = json.load(json_file)

train = data['train']
pipe_lens = data['pipe_lens']

iter_pipe_lens = iter(pipe_lens)

# set height and width of window
window = pygame.display.set_mode((window_width, window_height))
elevation = window_height * 0.8
game_images = {}
framepersecond = 32
pipeimage = os.path.join(__location__, 'images/pipe.png')
background_image = os.path.join(__location__, 'images/background.jpg')
birdplayer_image = os.path.join(__location__, 'images/bird.png')
sealevel_image = os.path.join(__location__, 'images/base.jfif')

bird_flapped = False
bird_flap_velocity = 0
# data = [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]*9 + [1,1,1,1,1]

iter_one_zero = cycle([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1])
def flappygame():
    global iter_pipe_lens, bird_flap_velocity, bird_flapped, train
    

    your_score = 0
    horizontal = int(window_width/5)
    vertical = int(window_width/2)
    ground = 0
    mytempheight = 100

	# Generating two pipes for blitting on window
    first_pipe = createPipe()
    second_pipe = createPipe()

	# List containing lower pipes
    down_pipes = [
		{'x': window_width+300-mytempheight,
		'y': first_pipe[1]['y']},
		{'x': window_width+300-mytempheight+(window_width/2),
		'y': second_pipe[1]['y']},
	]

	# List Containing upper pipes
    up_pipes = [
		{'x': window_width+300-mytempheight,
		'y': first_pipe[0]['y']},
		{'x': window_width+200-mytempheight+(window_width/2),
		'y': second_pipe[0]['y']},
	]

	# pipe velocity along x
    pipeVelX = -4

	# bird velocity
    bird_velocity_y = -9
    bird_Max_Vel_Y = 10
    bird_Min_Vel_Y = -8
    birdAccY = 1

    bird_flap_velocity = -8
    bird_flapped = False
    
    x = iter(train)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                with open('data.json', 'w') as f:
                    json.dump({"train": train, 'pipe_lens': pipe_lens}, f)
                pygame.quit()
                sys.exit()
            
            # if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
            #     if vertical > 0:
            #         bird_velocity_y = bird_flap_velocity
            #         bird_flapped = True
        try:
            if next(x):
                bird_velocity_y = bird_flap_velocity
                bird_flapped = True

        except:
            train.append(next(iter_one_zero))

        game_over = isGameOver(horizontal,
							vertical,
							up_pipes,
							down_pipes)
        if game_over[0]:
            y = game_over[1]
            
            for i, v in enumerate(reversed(train)):
                if y != v:
                    train[-1 if i == 0 else (i*-1)+-1] = y
                    break

            print(train[len(train)-20:], len(train))
            iter_pipe_lens = iter(pipe_lens)
            x = iter(train)
            return

		# check for your_score
        playerMidPos = horizontal + game_images['flappybird'].get_width()/2
        for pipe in up_pipes:
            pipeMidPos = pipe['x'] + game_images['pipeimage'][0].get_width()/2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                your_score += 1
                print(f"Your your_score is {your_score}")

        if bird_velocity_y < bird_Max_Vel_Y and not bird_flapped:
            bird_velocity_y += birdAccY

        if bird_flapped:
            bird_flapped = False
        playerHeight = game_images['flappybird'].get_height()
        vertical = vertical + \
			min(bird_velocity_y, elevation - vertical - playerHeight)

		# move pipes to the left
        for upperPipe, lowerPipe in zip(up_pipes, down_pipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

		# Add a new pipe when the first is
		# about to cross the leftmost part of the screen
        if 0 < up_pipes[0]['x'] < 5:
            newpipe = createPipe()
            up_pipes.append(newpipe[0])
            down_pipes.append(newpipe[1])

		# if the pipe is out of the screen, remove it
        if up_pipes[0]['x'] < -game_images['pipeimage'][0].get_width():
            up_pipes.pop(0)
            down_pipes.pop(0)

		# Lets blit our game images now
        window.blit(game_images['background'], (0, 0))
        for upperPipe, lowerPipe in zip(up_pipes, down_pipes):
            window.blit(game_images['pipeimage'][0],
						(upperPipe['x'], upperPipe['y']))
            window.blit(game_images['pipeimage'][1],
						(lowerPipe['x'], lowerPipe['y']))

        window.blit(game_images['sea_level'], (ground, elevation))
        window.blit(game_images['flappybird'], (horizontal, vertical))

		# Fetching the digits of score.
        numbers = [int(x) for x in list(str(your_score))]
        width = 0

		# finding the width of score images from numbers.
        for num in numbers:
            width += game_images['scoreimages'][num].get_width()
        Xoffset = (window_width - width)/1.1

		# Blitting the images on the window.
        for num in numbers:
            window.blit(game_images['scoreimages'][num],
						(Xoffset, window_width*0.02))
            Xoffset += game_images['scoreimages'][num].get_width()

		# Refreshing the game window and displaying the score.
        pygame.display.update()
        framepersecond_clock.tick(framepersecond)


def isGameOver(horizontal, vertical, up_pipes, down_pipes):
	if vertical > elevation - 25: # down border
		return (True, 1)

	elif vertical < 0: # up border
		return (True, 0)

	for pipe in up_pipes:
		pipeHeight = game_images['pipeimage'][0].get_height()
		if(vertical < pipeHeight + pipe['y'] and\
		abs(horizontal - pipe['x']) < game_images['pipeimage'][0].get_width()): # up pipe
			return (True, 0)

	for pipe in down_pipes:
		if (vertical + game_images['flappybird'].get_height() > pipe['y']) and\
		abs(horizontal - pipe['x']) < game_images['pipeimage'][0].get_width(): # down pipe
			return (True, 1)
	return (False,)


def createPipe():
	offset = window_height/3
	pipeHeight = game_images['pipeimage'][0].get_height()
	try:
		y2 = offset + \
			next(iter_pipe_lens)
	
	except:
		with open('data.json', 'w') as f:
			json.dump({"train": train, 'pipe_lens': pipe_lens}, f)
		print("^^^^^^^^^^^^^^^^^^^^\WIN/^^^^^^^^^^^^^^^^^^^^")
		sys.exit()
		# random.randrange(
		# 	0, int(window_height - game_images['sea_level'].get_height() - 1.2 * offset))

	pipeX = window_width + 10
	y1 = pipeHeight - y2 + offset
	pipe = [
		# upper Pipe
		{'x': pipeX, 'y': -y1},

		# lower Pipe
		{'x': pipeX, 'y': y2}
	]
	return pipe


# program where the game starts
if __name__ == '__main__':
	# For initializing modules of pygame library
	pygame.init()
	framepersecond_clock = pygame.time.Clock()

	# Sets the title on top of game window
	pygame.display.set_caption('Flappy Bird Game')

	# Load all the images which we will use in the game

	# images for displaying score
	game_images['scoreimages'] = (
		pygame.image.load(os.path.join(__location__, 'images/0.png')).convert_alpha(),
		pygame.image.load(os.path.join(__location__, 'images/1.png')).convert_alpha(),
		pygame.image.load(os.path.join(__location__, 'images/2.png')).convert_alpha(),
		pygame.image.load(os.path.join(__location__, 'images/3.png')).convert_alpha(),
		pygame.image.load(os.path.join(__location__, 'images/4.png')).convert_alpha(),
		pygame.image.load(os.path.join(__location__, 'images/5.png')).convert_alpha(),
		pygame.image.load(os.path.join(__location__, 'images/6.png')).convert_alpha(),
		pygame.image.load(os.path.join(__location__, 'images/7.png')).convert_alpha(),
		pygame.image.load(os.path.join(__location__, 'images/8.png')).convert_alpha(),
		pygame.image.load(os.path.join(__location__, 'images/9.png')).convert_alpha()
	)
	game_images['flappybird'] = pygame.image.load(
		birdplayer_image).convert_alpha()
	game_images['sea_level'] = pygame.image.load(
		sealevel_image).convert_alpha()
	game_images['background'] = pygame.image.load(
		background_image).convert_alpha()
	game_images['pipeimage'] = (pygame.transform.rotate(pygame.image.load(
		pipeimage).convert_alpha(), 180), pygame.image.load(
	pipeimage).convert_alpha())

	# Here starts the main game

	while True:

		# sets the coordinates of flappy bird
		
		horizontal = int(window_width/5)
		vertical = int(
			(window_height - game_images['flappybird'].get_height())/2)
		ground = 0

		while True:
			for event in pygame.event.get():
				# if user clicks on cross button, close the game
				if event.type == QUIT or (event.type == KEYDOWN and \
										event.key == K_ESCAPE):
					with open('data.json', 'w') as f:
						json.dump({"train": train, 'pipe_lens': pipe_lens}, f)
					pygame.quit()
					sys.exit()

				# If the user presses space or
				# up key, start the game for them
				# elif event.type == KEYDOWN and (event.key == K_SPACE or\
				# 								event.key == K_UP):

				# if user doesn't press anykey Nothing happen
				else:
					# sleep(0.3)
					window.blit(game_images['background'], (0, 0))
					window.blit(game_images['flappybird'],
								(horizontal, vertical))
					window.blit(game_images['sea_level'], (ground, elevation))
					# window.blit(text , (601, 220))
					pygame.display.update()
					framepersecond_clock.tick(framepersecond)

				flappygame()

			