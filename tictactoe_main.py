##TICTACTOE
import random

board = [[' ',' ',' '],[' ',' ',' '],[' ',' ',' ']]

def player1_win():
  print('Player 1 wins!')
  quit()

def player2_win():
  print('Player 2 wins!')
  quit()

def set_mark(board,player):
  letter = ['a','b','c']
  number = ['1','2','3']
  marker = input('Player ' + str(player) + ' Turn!\nChoose a square (ex. b2): ')
  if (len(marker) == 2) and (marker[0] in letter) and (marker[1] in number):
    if (board[int(marker[1])-1][int(ord(marker[0])-97)] == 'X') or (board[int(marker[1])-1][int(ord(marker[0])-97)] == 'O'):
      set_mark(board,player)
    else:
      if player == 1:
        board[int(marker[1])-1][int(ord(marker[0])-97)] = 'X'
      else:
        board[int(marker[1])-1][int(ord(marker[0])-97)] = 'O'
  else:
    set_mark(board,player)

def check(board):
  for n in range(2):
    if board[n] == ['X','X','X']:
      player1_win()
      break
    elif board[n] == ['O','O','O']:
      player2_win()
      break
    elif board[0][n] == 'X' and board[1][n] == 'X' and board[2][n] == 'X':
      player1_win()
      break
    elif board[0][n] == 'O' and board[1][n] == '0' and board[2][n] == 'O':
      player2_win()
      break
  if (board[0][0] == 'X' and board[1][1] == 'X' and board[2][2] == 'X') or (board[0][2] == 'X' and board[1][1] == 'X' and board[2][0] == 'X'):
      player1_win()
  elif (board[0][0] == 'O' and board[1][1] == 'O' and board[2][2] == 'O') or (board[0][2] == 'O' and board[1][1] == 'O' and board[2][0] == 'O'):
      player2_win()

def reset(board):
  board = [['','',''],['','',''],['','','']]

def printboard(board):
  print('    A   B   C')
  print('  ╔═══╦═══╦═══╗')
  for i in range(1,4):
    print(i,'║',board[i-1][0],'║',board[i-1][1],'║',board[i-1][2],'║')
    if not i == 3:
      print('  ╠═══╬═══╬═══╣')
  print('  ╚═══╩═══╩═══╝\n')

def turn(board,player):
  printboard(board)
  check(board)
  set_mark(board,player)

def start(player):
  print('Welcome to TICTACTOE!')
  input('Press [ENTER] to play')
  if player == 1:
    print('Player 1 plays first!\n')
  else:
    print('Player 2 plays first!\n')
  return player

player = random.randint(1,2)
start(player)
turn(board,player)
while (True):
  if player == 1:
    player+=1
  elif player == 2:
    player = player -1
  turn(board,player)