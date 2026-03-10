# self-learning-chess

building a chess engine from scratch in python to mess around with bitboards and reinforcement learning.

the idea is to have it learn to evaluate positions by playing against itself. it uses alpha-beta search along with a simple pytorch neural network.

### how to run
```bash
pip install torch

# watch it play
python watch_ai_play.py

# run the learning pipeline (generate data + train + evaluate)
python pipeline.py
```

### structure
- `chess_ai/board.py`: bitboards and move logic
- `chess_ai/search.py`: minimax with alpha-beta and iterative deepening
- `chess_ai/model.py`: simple pytorch nn 
- `chess_ai/evaluation.py`: material + piece square tables + nn eval blended together
