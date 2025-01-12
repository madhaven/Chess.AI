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

# find default legal moves of a cell
>>> moves = game.legalMoves('a2')

# find moves a cell could possibly attack
>>> moves = game.checkableMoves('a2')

# find moves that a piece in a particular cell(a2) could make
>>> moves = game.movesOfCell('a2')

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

## History

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
* I had architected the game in such a way that control started from the UI.
  The UI code controlled UI logic, instantiated the player and game object classes. The UI code was responsible for displaying the game state and handling User Interaction and also delegating the choices made by the players to the game.  
* A lot of effort was already spent on UI and architecture design, maybe that must be the aftermath of poor project planning and a lack of personal consistency.  
  I decided to focus more of my efforts on implementing Player classes and tapping into Intelligence part of the project.  

## The rise of Intelligence

Here I record the journey to developing better performing Chess players.  
The observations and improvements made are also summarized.  

* Random and Greedy Players  
  I had already started out with a `PlayerRandom` and a `GreedyPlayer` to start off with.  
  As the name suggests, the random player makes random moves out of the available moves and the greedy player additionally tries to take pieces in a greedy fashion if there are pieces to take.  
  This helped test out scenarios involving non-human players.  
  This didn't serve any intelligence as such and the satisfaction waned away really fast.  
* Minimax Players  
  Here is [the Minimax algorithm from Wikipedia](https://en.wikipedia.org/wiki/Minimax)  
  The idea is to choose a move, but for each possible move, we also calculate the move that the oponent will take, so and and so forth until N levels of depth are reached on the search tree.  
  
  ```txt
            (X)               minplayer
  move 1  /     \ move 2
       (Y)       (Z)          maxplayer
      /   \     /   \
    (A)   (B) (C)   (D)
    -5     9   2     1

            (X)               minplayer
          /     \
       (Y)       (Z)          maxplayer chooses move with max value
        9         2

            (X) takes move with minimum value
             2
  ```

  Without a limit on the depth, the algorithm might end up finding all possible moves in the game. This is not a practical choice for a game like Chess which has too many possibilities to evaluate. So on the last depth level, an estimate value of the game is used.  

  Implementing the Minimax algorithm improved gameplay but there were edge cases, partly due to errors in my implementation and partly due to the value estimation I had set up.  
  * `MinimaxPlayer_00` only has a value function that maximized the "opportunity" of taking pieces by counting the number of pieces that were available for take on a game position.  
    It only estimated a single move and didn't really perform a Minimax search.  
  * `MinimaxPlayer_01`, `MinimaxPlayer_02` and `MinimaxPlayer_03` experimented with minor improvements that helped setup the minimax algorithm.  
    Evaluating just 3 successions of game positions started to take more than a minute to complete.  
    Another noteable issue was the UI blocking during this time when the player was making its calculations.  
    **Threads** helped to solve this issue by parallelizing the player process.  

    The value function still optimized only the "possibility" of a take.  
    To no surprise, it didn't prioritize takes but only the opportunity.  
    The player played the game moving pieces into good positions but it didn't attack.  
    o___0  
  * `MinimaxPlayer_04` solved the long calculation times taken by the older versions by implementing **alpha-beta pruning** on the search tree.  
    the alpha-beta pruning maintains two values alpha and beta across the search algorithm.
