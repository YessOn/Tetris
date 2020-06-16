import pygame
import random

pygame.init()
pygame.display.set_caption("Tetris Game!")
pygame.font.init()
clock = pygame.time.Clock()

# Global variables
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

# SHAPE FORMATS
S = [['.....', '......', '..00..', '.00...', '.....'], ['.....', '..0..', '..00.', '...0.', '.....']]

Z = [['.....', '.....', '.00..', '..00.', '.....'], ['.....', '..0..', '.00..', '.0...', '.....']]

I = [['..0..', '..0..', '..0..', '..0..', '.....'], ['.....', '0000.', '.....', '.....', '.....']]

O = [['.....', '.....', '.00..', '.00..', '.....']]

J = [['.....', '.0...', '.000.', '.....', '.....'], ['.....', '..00.', '..0..', '..0..', '.....'], ['.....', '.....', '.000.', '...0.', '.....'], ['.....', '..0..', '..0..', '.00..', '.....']]

L = [['.....', '...0.', '.000.', '.....', '.....'], ['.....', '..0..', '..0..', '..00.', '.....'], ['.....', '.....', '.000.', '.0...', '.....'], ['.....', '.00..', '..0..', '..0..', '.....']]

T = [['.....', '..0..', '.000.', '.....', '.....'], ['.....', '..0..', '..00.', '..0..', '.....'], ['.....', '.....', '.000.', '..0..', '.....'], ['.....', '..0..', '.00..', '..0..', '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]

class Piece(object):
	def __init__(self, x, y, shape):
		self.x = x
		self.y = y
		self.shape = shape
		self.color = shape_colors[shapes.index(shape)]
		self.rotation = 0

def create_grid(locked_positions={}):
	grid = [[(0,0,0) for x in range(10)] for x in range(20)]
	for i in range(len(grid)):
		for j in range(len(grid[i])):
			if (j,i) in locked_positions:
				cube = locked_positions[(j,i)]
				grid[i][j] = cube
	return grid

def convert_shape_format(shape):
	positions = []
	format = shape.shape[shape.rotation % len(shape.shape)]
	for i, line in enumerate(format):
		row = list(line)
		for j, column in enumerate(row):
			if column == '0': positions.append((shape.x + j, shape.y + i))
	for i, pos in enumerate(positions): positions[i] = (pos[0] - 2, pos[1] - 4)
	return positions

def valid_space(shape, grid):
	accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
	accepted_positions = [j for sub in accepted_positions for j in sub]
	formatted = convert_shape_format(shape)
	for pos in formatted:
		if pos not in accepted_positions:
			if pos[1] > -1: return False
	return True

def check_lost(positions):
	for pos in positions:
		x, y = pos
		if y < 1: return True
	return False

def get_shape(): return Piece(5, 0, random.choice(shapes))

def draw_text_middle(text, size, color):
	font = pygame.font.SysFont('comicsans', size, bold=True)
	label = font.render(text, 1, color)
	win.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2))

def draw_grid(row, col):
	sx = top_left_x
	sy = top_left_y
	for i in range(row):
		pygame.draw.line(win, (128,128,128), (sx, sy+ i*30), (sx + play_width, sy + i * 30))  # horizontal lines
		for j in range(col):
			pygame.draw.line(win, (128,128,128), (sx + j * 30, sy), (sx + j * 30, sy + play_height))  # vertical lines

def clear_rows(grid, locked):
	inc = 0
	for i in range(len(grid)-1,-1,-1):
		row = grid[i]
		if (0, 0, 0) not in row:
			inc += 1
			# add positions to remove from locked
			ind = i
			for j in range(len(row)):
				try: del locked[(j, i)]
				except: continue
	if inc > 0:
		for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
			x, y = key
			if y < ind:
				newKey = (x, y + inc)
				locked[newKey] = locked.pop(key)

def draw_next_shape(shape):
	font = pygame.font.SysFont('comicsans', 30)
	label = font.render('Next Shape', 1, (255, 255, 255))
	sx = top_left_x + play_width + 50
	sy = top_left_y + play_height/2 - 100
	format = shape.shape[shape.rotation % len(shape.shape)]
	for i, line in enumerate(format):
		row = list(line)
		for j, column in enumerate(row):
			if column == '0': pygame.draw.rect(win, shape.color, (sx + j*30, sy + i*30, 30, 30), 0)
	win.blit(label, (sx + 10, sy - 30))

def redraw_window():
	win.fill((0,0,0))
	font = pygame.font.SysFont('comicsans', 60)
	label = font.render('TETRIS', 1, (255,255,255))
	win.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))
	for i in range(len(grid)):
		for j in range(len(grid[i])):
			pygame.draw.rect(win, grid[i][j], (top_left_x + j* 30, top_left_y + i * 30, 30, 30), 0)
	draw_grid(20, 10)
	pygame.draw.rect(win, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

def mainloop():
	global grid
	locked_positions = {}  # (x,y):(255,0,0)
	grid = create_grid(locked_positions)
	change_piece = False
	current_piece = get_shape()
	next_piece = get_shape()
	fall_time = 0
	level_time = 0
	fall_speed = 0.27
	score = 0
	run = True
	while run:
		grid = create_grid(locked_positions)
		fall_time += clock.get_rawtime()
		level_time += clock.get_rawtime()
		clock.tick()
		if level_time/1000 > 4:
			level_time = 0
			if fall_speed > 0.15: fall_speed -= 0.005
		if fall_time/1000 >= fall_speed:
			fall_time = 0
			current_piece.y += 1
			if not (valid_space(current_piece, grid)) and current_piece.y > 0:
				current_piece.y -= 1
				change_piece = True
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
				pygame.display.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					current_piece.x -= 1
					if not valid_space(current_piece, grid): current_piece.x += 1
				elif event.key == pygame.K_RIGHT:
					current_piece.x += 1
					if not valid_space(current_piece, grid): current_piece.x -= 1
				elif event.key == pygame.K_UP:
					current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
					if not valid_space(current_piece, grid): current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)
				if event.key == pygame.K_DOWN:
					current_piece.y += 1
					if not valid_space(current_piece, grid): current_piece.y -= 1
		shape_pos = convert_shape_format(current_piece)
		for i in range(len(shape_pos)):
			x, y = shape_pos[i]
			if y > -1: grid[y][x] = current_piece.color
		if change_piece:
			for pos in shape_pos:
				p = (pos[0], pos[1])
				locked_positions[p] = current_piece.color
			current_piece = next_piece
			next_piece = get_shape()
			change_piece = False
			if clear_rows(grid, locked_positions): score += 10
		redraw_window()
		draw_next_shape(next_piece)
		pygame.display.update()
		if check_lost(locked_positions): run = False
	draw_text_middle("You Lost", 40, (255,255,255))
	pygame.display.update()
	pygame.time.delay(2000)

win = pygame.display.set_mode((s_width, s_height))
play = True
while play:
	win.fill((0,0,0))
	draw_text_middle('Press any key to begin.', 60, (255, 255, 255))
	pygame.display.update()
	for event in pygame.event.get():
		if event.type == pygame.QUIT: run = False
		if event.type == pygame.KEYDOWN: mainloop()
pygame.quit()