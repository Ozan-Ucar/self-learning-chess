import time
import random
from chess_ai.board import Board

def play_demo_game(num_moves=10):
    board = Board()
    print("--- Starting Demo Game (Random Moves) ---")
    board.print_board()
    
    for i in range(num_moves):
        time.sleep(1) # Slow down for visualization
        legal_moves = board.get_legal_moves()
        
        if not legal_moves:
            print("Game Over (Checkmate or Stalemate)")
            break
            
        # Pick a random legal move for demonstration
        move = random.choice(legal_moves)
        
        print(f"\nMove {i+1}: {'White' if board.turn == 0 else 'Black'} plays {move}")
        board.make_move(move)
        board.print_board()

if __name__ == "__main__":
    play_demo_game(8) # Let's see 8 moves
