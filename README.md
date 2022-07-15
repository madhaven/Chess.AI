# CHESS . AI

This is an attempt to design an AI to play chess.
The idea is to train the model on sample games with itself alone. Learning by experience.

* ```Chess``` class in ```Chess.py``` contains all game logic.  
The ```Chess``` class represents an instance of the board in a game.  
Each move made will result in a new state of the board. This could lead to a graph-like picture with each board instance being a node in the game tree.

```python
# load a game
game = Chess()
game = Chess.loadFrom(r'file')

# print the board to the prompt
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

# find all available moves of the player
>>> allMoves = game.getMoves()

# find moves that a piece in a particular cell(a2) could make
>>> moves = game.movesOf('a2')

# find moves a cell could possibly attack
>>> moves = game.checkableMoves('a2')

# find default legal moves of a cell
>>> moves = game.legalMoves('a2')

# make a move
>>> newGameState = game.makeMove('a2', 'a4')

# check what state the game is in
>>> result = game.result

# for more help
>>> help(game)
```

* ```playChess.py``` contains all UI logic required by a human to test the game manually. This would be better for a casual human player to use.
* ```Test_Chess.py``` is for use in the command line. It could load up a .save file and provide an interactive console from an instance of the game and gives control for testing.
* The assets folder contain sample games for the test to load and also images of pieces for the game to use.

## Documentation

I began the project with the intention of implementing Regressive Learning on the Chess board.  

* A form of representation of a chess game was necassary.  
  This is how the Chess class was born.  
  Each move would return another state of the chess board, this I believe was supportive of the learning mechanism.  
  The game thus moved in a loop with each move leading to a new node in the game.
* At some point testing the game via command line became too much of a trouble.  
  This is when the advent of a UI window became inevitable.  
  UI was implemented such that the whole game started off from UI and control completely resided in the UI code.  
  UI code controlled the game menus and the controls to the game.

  > This I later realized to be a bad practice as Game Logic and UI logic seemed to mix throughout the code and seperate concerns got entangled together.  
