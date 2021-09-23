# CHESS . AI
This is an attempt to design an AI to play chess.
The idea is to train the model on sample games with itself alone. Learning by experience.

* ```Chess``` class in ```Chess.py``` contains all game logic. <br>The ```Chess``` class represents an instance of the board in a game. <br>Each move made will result in a new state of the board. This could lead to a graph-like picture with each board instance to be a node in the game.
```python
# to load the game
game = Chess()
game = Chess.loadFrom(r'file')

# prints the board to the prompt
>>> print(game)
8|   Q             |
7|                 |
6| k               |
5| p               |
4| P   p     N   P |
3|     P           |
2|   R         P   |
1|         K     R |
   a b c d e f g h

# to find all available moves
>>> allMoves = game.getMoves()

# to find moves a particular cell(a2) could make
>>> moves = game.movesOf('a2')

# to find moves a cell could possibly attack
>>> moves = game.checkableMoves('a2')

# to find default legal moves of a cell
>>> moves = game.legalMoves('a2')

# to make a move
>>> newGameState = game.makeMove('a2', 'a4')

# to check what state the game is in
# 1: White wins, 0: Draw, -1: Black wins, None: Game in progress
>>> result = game.result

#for more help
>>> help(game)
```
* ```playChess.py``` contains all UI logic required by a human to test the game manually. This would be better for a casual human player to use.
* ```Test_Chess.py``` is for use in the command line. It could load up a .save file and provide an interactive console from an instance of the game and gives control for testing.
* The assets folder contain sample games for the test to load and also images of pieces for the game to use.