import os
from deuces import Card
from deuces import Evaluator
from deuces import Deck
import random
import copy
################ README:
################ Only change the lines that explicitly tell you than can be changed, otherwise your final program will not work with our grading process

class Player:
	money = 0
	curHand = []
	def __init__(self, startMoney):
		self.money = startMoney
	def returnBestHand(self, board): #CHANGE THIS FUNCTION TO RETURN THE BEST HAND WHEN ASKED AT THE RIVER
		return evaluator.evaluate(board, self.curHand)
	def callAI(self, state): #CHANGE THIS FUNCTION. NEVER REFERENCE OTHER PLAYER'S CARDS. You are not allowed to cheat! (obviously) e.g. If we see curState.players[x].curHand, that's unacceptable.
		MAX_SCORE= 7462
		score = 0
		# we evaluate the score of the current situation and based on the estimated score, pick an acion
		# We randomly generate the board N times and get the average score
		N = 5
		i = 0

		if curState.curStage == "river":
			score = score + evaluator.evaluate(curState.board, self.curHand)
		else:
			while i < N:
				my_deck = Deck()
				my_board = my_deck.draw(0)

				if curState.curStage == "preflop":
					exclude = copy.deepcopy(self.curHand)
					my_board = self.draw(5, exclude, my_deck)

				elif curState.curStage == "flop":
					exclude = copy.deepcopy(self.curHand) + copy.deepcopy(curState.board)
					my_board = curState.board + self.draw(2, exclude, my_deck)

				elif curState.curStage == "turn":
					exclude = copy.deepcopy(self.curHand) + copy.deepcopy(curState.board)
					my_board = curState.board +  self.draw(1, exclude, my_deck)


				score = score + evaluator.evaluate(self.curHand, my_board)
				i = i + 1
			score = score / N
		#raiseAmount = random.randint(0, 100)
		#maxbid = max(raiseAmount, random.randint(0, 100))
		#if maxbid > self.money: #do not remove
		#	maxbid = self.money
		#if raiseAmount > self.money: #do not remove
		#	raiseAmount = self.money
		#possibleActions = ["check", ["raise", raiseAmount]] #can only check or raise, since only one action is processed. Fold if max bid is lower than the biggest raise.

		#There are 7462 scores in total (smaller is better). We choose an action based on the estimated score
		if score > MAX_SCORE * 9 / 10: # the score is too high, choose fold
			raiseAmount = 0
			action = ["raise", 0]
			maxbid = 0           # maxbid = 0, means fold
		elif score > MAX_SCORE / 2:
			action = ["check"]
			maxbid = 0
		else:
			raiseAmount = random.randint(0, self.money * (1 - score / MAX_SCORE) / 2)
			maxbid = max(raiseAmount, random.randint(0, self.money * (1 - score / MAX_SCORE)) )
			action = ["raise",raiseAmount ]
		return [ action, maxbid ]
	def draw(self, num, exclude, my_deck):
		my_board=[]
		while len(my_board) < num:
			my_deck.shuffle()
			d = my_deck.draw(1)
			if d not in exclude:
				my_board.append(d)
				exclude.append(d)

		return my_board

#holds state, you'll need to reference this in callAI
class State:
	stages = ["preflop", "flop", "turn", "river"]
	pot = 0
	curStage = ""
	players = []
	curPlayers = []
	board = []

	def __init__(self, players):
		self.players = players
	
#deal out cards to the board
def deal(cardAmt):
	draw = deck.draw(cardAmt)
	if isinstance(draw, int):
		curState.board.append(deck.draw(cardAmt))
	else:
		curState.board.extend(deck.draw(cardAmt))
	print("Board: ")
	print(Card.print_pretty_cards(curState.board)) 

#get bet amounts from each player
def bet():
	actions = []
	maxRaise = 0
	for player in curState.curPlayers:
		action = player.callAI(curState)
		actions.append([player, action])
		if action[0][0] == "raise" and action[0][1] > maxRaise:
			maxRaise = action[0][1]
	for action in actions:
		if maxRaise > action[1][1]:
			curState.curPlayers.remove(action[0])
		else:
			action[0].money -= maxRaise 
			curState.pot += maxRaise
	print("Stage: " + curState.curStage)
	print("Player Actions: " + str(actions))
	print("Pot: " + str(curState.pot))
	print("Current Players: ")
	for player in curState.curPlayers:
		print("   Hand: ")
		Card.print_pretty_cards(player.curHand)
		print("   Money: " + str(player.money))

#Setup for poker game
evaluator = Evaluator()
curPot = 0
players = [Player(2000), Player(2000), Player(2000)] #CAN CHANGE
curState = State(players)

i = 0
while len(players) > 1:
	print("-----------------")
	print("")
	i += 1
	curState.pot = 0
	#ante
	for player in curState.players:
		ante = min(player.money, 50)
		player.money -= ante
		curState.pot += ante
	#prepare board and deck
	deck = Deck()
	deck.shuffle()
	curState.board = deck.draw(0)
	for player in curState.players:
		player.curHand = [] 
		player.curHand = deck.draw(2)
	#create players for this round
	curState.curPlayers = curState.players[:]
	#go through betting stages
	for stage in range(0, len(curState.stages)):
		curState.curStage = curState.stages[stage]
		print("stage: " + curState.curStage )
		if curState.curStage == "flop":
			deal(3)
		elif curState.curStage == "turn":
			deal(1)
		elif curState.curStage == "river":
			deal(1)
		bet()
		#check if only one player is left
		if len(curState.curPlayers) == 1:
			print("Round Over")
			curState.curPlayers[0].money += curState.pot
			print("Winner: ") 
			Card.print_pretty_cards(curState.curPlayers[0].curHand)
			print("New Stack: " + str(curState.curPlayers[0].money))
			break
		#If river check who won
		if curState.curStage == "river":
			print("Round Over")
			scores = []
			for player in curState.curPlayers:
				scores.append(player.returnBestHand(curState.board))
			winner = scores.index(min(scores))
			curState.curPlayers[winner].money += curState.pot
			print("Winner: ") 
			Card.print_pretty_cards(curState.curPlayers[winner].curHand)
			print("New Stack: " + str(curState.curPlayers[winner].money))
			break
	#remove broke players
	for player in curState.players:
		if player.money == 0:
			curState.players.remove(player)


print(str(curState.players[0]) + " has won!")
