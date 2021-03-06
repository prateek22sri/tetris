'''
REPORT for part 2:

Initial State: Empty board with 20 rows and 10 columns
Valid states: A set of successors where new piece of size 4 is placed 
Successor function: Set in which all possible rotations of the piece placed on each column after checking collision .
Goal State: Player looses when no piece can be placed on the board(i.e. the top row of board has a (part of ) piece

1) Algorithm:

Generates successors for the piece and finds the best possible place using heuristic

2) heuristic:

Following things are considered in the heuristic:
a)increase in height
b)change in number of holes
c)no of blockings added
d)award for no of clears


3)Problems faced:

a)Designing the heuristic
b)assigning weights to each parameters in the heuristic

Author: Sucessor, heuristic, getmoves, and all functions related to heuristic by Sairam Rakshith bhyravabhotla
Others: David Crandall. 
functions from TetrisGame() object used from TetrisGame.py written by David Crandall.
'''



# Simple tetris program! v0.2
# D. Crandall, Sept 2016
from itertools import groupby
from AnimatedTetris import *
from SimpleTetris import *
from kbinput import *
import time, sys
from copy import deepcopy
class HumanPlayer:
	def get_moves(self, tetris):
		print "Type a sequence of moves using: \n  b for move left \n  m for move right \n	n for rotation\nThen press enter. E.g.: bbbnn\n"
		moves = raw_input()
		return moves

	def control_game(self, tetris):
		while 1:
			c = get_char_keyboard()
			commands =	{ "b": tetris.left, "n": tetris.rotate, "m": tetris.right, " ": tetris.down }
			commands[c]()

#####
# This is the part you'll want to modify!
# Replace our super simple algorithm with something better
#
class ComputerPlayer:
	# This function should generate a series of commands to move the piece into the "optimal"
	# position. The commands are a string of letters, where b and m represent left and right, respectively,
	# and n rotates. tetris is an object that lets you inspect the board, e.g.:
	#	- tetris.col, tetris.row have the current column and row of the upper-left corner of the 
	#	  falling piece
	#	- tetris.get_piece() is the current piece, tetris.get_next_piece() is the next piece after that
	#	- tetris.left(), tetris.right(), tetris.down(), and tetris.rotate() can be called to actually
	#	  issue game commands
	#	- tetris.get_board() returns the current state of the board, as a list of strings.
	#
	#awards if a successor clears a line	
	def clears(self,board,piece,piece_col,score):
		succ= self.successors(board,piece,piece_col,score)
		count=0
		clear_list=[]
		for board in succ:
			for row in board:
				if row == 'xxxxxxxxxx':
					count+=1	
			clear_list.append(count)	
		return clear_list

	#base reward: reward if a piece touches the base
	def base_reward(self,board,piece,piece_col,score):
		succ= self.successors(board,piece,piece_col,score)	
		current_base= board[-1].count('x')
		base_reward_list=[]
		for item in succ:
			brd = item[0]
			base_reward_list.append((brd[-1].count('x')-current_base, item[1]))

		return base_reward_list
			

	#edge reward: reward if a piece touches edges
	def edge_reward(self, board, piece, piece_col, score):
		col_board= zip(*board)
		succ= self.successors(board,piece,piece_col,score)
		current_edge= col_board[0].count('x')+col_board[-1].count('x')
		reward_list=[]
		for item in succ:
			x= item[0]
			brd = zip(*x)
			reward_list.append((board[0].count('x')+board[-1].count('x')-current_edge, item[1]))
		return reward_list
	
	def get_positions(self, board):
		
		b= zip(*board)
		ind_list=[]
		col_no=0
		for col in b:
			lcol= list(col)
			if 'x' in lcol:
				ind_list.append((col_no,lcol.index('x')))
			else:
				ind_list.append((col_no,20))
			col_no+=1
		#print ind_list, "indlist"
		return ind_list
	
	def successors(self,board,piece,piece_col, score):	
		try:	
			#brd = ['         '*20]
			#print self.get_positions(brd),"her"
			temp_obj= TetrisGame()
			#piece= temp_obj.get_piece()[0]
			temp_board=board
			positions= self.get_positions(temp_board)
			#print positions,"pos"
			#positions= [[(row,col) for col in range(len(board[0])) if board[row][col]==' '] for row in range(len(board))]
			possible_rotations=[]
			possible_rotations.append(piece)		
			possible_rotations.append(temp_obj.rotate_piece(piece,90))
			possible_rotations.append(temp_obj.rotate_piece(piece,180))
			possible_rotations.append(temp_obj.rotate_piece(piece,270))
			#print possible_rotations,"pr"
			successor_list=[]
			for piece in possible_rotations: 
				move=""
				if possible_rotations.index(piece)==1:
					move+="n"
				elif possible_rotations.index(piece)==2:
					move+="nn"
				elif possible_rotations.index(piece)==3:
					move+="nnn"
				piece_height = len(piece)
				piece_width= len(max(piece, key=len))
				#print positions,"fds"
				for element in positions:
					#print element,"el"
					if not TetrisGame.check_collision((board, score),piece,element[1]-piece_height,element[0]):
						if element[0]+piece_width<=10 and element[1]-piece_height-1>=0:
							#print element[0], element[1],element[0]+piece_width, element[1]-piece_height, "elch"
							new_board = TetrisGame().place_piece((temp_board, score), piece,element[1]-piece_height-1 ,element[0])
							if element[0]<piece_col:
								successor_list.append((new_board[0], move+"b"*(piece_col-element[0])))
							elif element[0]>piece_col:
								successor_list.append((new_board[0], move+"m"*(element[0]-piece_col)))
							elif element[0]==piece_col:
								successor_list.append((new_board[0], move))				
			#print successor_list
			if successor_list:
				return successor_list
			else:
				sys.exit(0)
		except IndexError:
			#eog= EndofGame()
			raise EndOfGame("Game over!")
			sys.exit(0)
	
	def calculate_penalty(self, board, piece, piece_col, score):
		succ = self.successors(board, piece, piece_col, score)
		base=self.base_reward(board, piece, piece_col, score) 
		edge = self.edge_reward(board, piece, piece_col, score)
		height= self.height_penalty(board, piece, piece_col, score)
		block = self.calculate_blocks( board, piece, piece_col, score)
		holes= self.calculate_holes( board, piece, piece_col, score)
		clears= self.clears(board,piece,piece_col,score)
		penalty_list=[]
		for i in range(len(succ)):
			#print (height[i][0], holes[i][0], block[i][0], clears[i], "heurvas")	
			#penalty_list.append((-clears[i],base[i][1]))
			#if len(height) == len(succ) == len(holes)==len(block)==len(clears):
			penalty_list.append((7.5*height[i][0]-5*holes[i][0]- 5*block[i][0]+ 30*clears[i]+2*edge[i][0]+3*base[i][0] ,succ[i][1]))
		sorted_list= sorted(penalty_list,key=lambda tup:tup[0])
		#print sorted_list,"sadf"
		return sorted_list[-1]
		
		
	#calculates penalty for height
	def height_penalty(self, board, piece, piece_col, score):
		succ= self.successors(board, piece, piece_col, score)
		current_height= self.height(board)
		height_penalty=[]
		for item in succ:
			height_penalty.append((self.height(item[0])-current_height, item[1]))
		return height_penalty

	def height(self, board):
		x_list=[]
		for row in board:
			if 'x' in row:
				x_list.append(board.index(row))	
		return min(x_list) if x_list else 0
	
	def calculate_height(self, board,piece,piece_col, score):	
		current_height= self.height(board)
   		succ = self.successors(board,piece,piece_col,score)	
		#print succ, "successors"
		height_list=[]
		for item in succ:
			#print item, "item"
			move= item[1]
			new_board = item[0]
			height_list.append((self.height(new_board)- current_height,move))
		sorted_list = sorted(height_list, key=lambda tup:tup[0])
		#print sorted_list, "sl"
		return sorted_list[-1]

	#function to calculate holes in a given board	
	def holes_count(self, board):
		count=0
		count_col= [[(i, len(list(g))) for i, g in groupby(col)] for col in zip(*board)]
		for col in count_col:
			for i in range(1, len(col)):
				if col[i][0]==' ' and col[i-1][0]=='x':
					count+=col[i][1]	
		return count

	#function to calculate blockings in a given board
	def block_count(self, board):
		count=0	
		count_col= [[(i, len(list(g))) for i, g in groupby(col)] for col in zip(*board)]
		for col in count_col:
			for i in range(0, len(col)-1):
				if col[i][0]=='x' and col[i+1][0]==' ':
					count+=col[i][1]	
		return count

	#calculates holes for each board in successors
	def calculate_holes(self, board, piece, piece_col, score):
		current_holes= self.holes_count(board)
		succ = self.successors(board,piece,piece_col,score)
		hole_list=[]
		for item in succ:
			move= item[1]
			hole_list.append((self.holes_count(item[0])-current_holes,item[1]))
		#print hole_list, "hl"
		return hole_list

	#calculates blocks for each board in successors			
	def calculate_blocks(self, board, piece, piece_col, score):
		current_blocks= self.block_count(board)
		succ = self.successors(board,piece,piece_col,score)
		block_list=[]
		for item in succ:
			move= item[1]
			block_list.append((self.block_count(item[0])-current_blocks,item[1]))
		return block_list
	
	def get_moves(self, tetris):
		temp= TetrisGame()	
		brd = tetris.get_board()
		current_col= tetris.col
		piece= tetris.get_piece()[0]
		piece_col= tetris.get_piece()[2]
		row =tetris.row
		col= tetris.col
		#print self.get_positions(board)
		score = temp.get_score()
		#moves= self.get_possible_moves(current_col)
		#self.successors(board,piece,score)
		temp_board= deepcopy(brd)
		#print brd
		best_move=self.calculate_holes(temp_board, piece,piece_col, score) 
		succ= self.calculate_penalty(brd, piece,piece_col, score)
		
		
		return succ[1]
	   
	# This is the version that's used by the animted version. This is really similar to get_moves,
	# except that it runs as a separate thread and you should access various methods and data in
	# the "tetris" object to control the movement. In particular:
	#	- tetris.col, tetris.row have the current column and row of the upper-left corner of the 
	#	  falling piece
	#	- tetris.get_piece() is the current piece, tetris.get_next_piece() is the next piece after that
	#	- tetris.left(), tetris.right(), tetris.down(), and tetris.rotate() can be called to actually
	#	  issue game commands
	#	- tetris.get_board() returns the current state of the board, as a list of strings.
	#
	def control_game(self, tetris):
		# another super simple algorithm: just move piece to the least-full column
		while 1:
			#time.sleep(0.1)

			
			temp= TetrisGame()	
			brd = tetris.get_board()
			current_col= tetris.col
			piece= tetris.get_piece()[0]
			piece_col= tetris.get_piece()[2]
			row =tetris.row
			col= tetris.col
			#print self.get_positions(board)
			score = temp.get_score()
			#moves= self.get_possible_moves(current_col)
			#self.successors(board,piece,score)
			temp_board= deepcopy(brd)
			#print brd
			best_move=self.calculate_holes(temp_board, piece,piece_col, score) 
			succ= self.calculate_penalty(temp_board, piece,piece_col, score)
			for index in succ[1]:
				if(index == 'b'):
					tetris.left()
				elif(index == 'm'):
					tetris.right()
				elif(index == 'n'):
					tetris.rotate()
			
				tetris.down()


###################
#### main program

(player_opt, interface_opt) = sys.argv[1:3]

try:
	if player_opt == "human":
		player = HumanPlayer()
	elif player_opt == "computer":
		player = ComputerPlayer()
	else:
		print "unknown player!"

	if interface_opt == "simple":
		tetris = SimpleTetris()
	elif interface_opt == "animated":
		tetris = AnimatedTetris()
	else:
		print "unknown interface!"

	tetris.start_game(player)

except EndOfGame as s:
	print "\n\n\n", s



