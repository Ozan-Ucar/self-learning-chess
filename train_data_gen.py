import csv
import os
import time
from chess_ai.board import Board
from chess_ai.search import find_best_move

DATA_FILE = "training_data.csv"

def generate_games(num_games=10, max_halfmoves=150, epsilon=0.15):
    print(f"generating data...")
    print(f"games: {num_games} | eps: {epsilon} | max: {max_halfmoves}")
    
    # We will log (FEN, Outcome)
    # Outcome: 1.0 (White Wins), 0.0 (Black Wins), 0.5 (Draw)
    
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["FEN", "Outcome"])
            
        total_positions = 0
        start_time = time.time()
        
        for g in range(num_games):
            board = Board()
            game_fens = []
            
            # Default is draw
            outcome = 0.5 
            
            for i in range(max_halfmoves):
                # 1. Record the current state before we move
                game_fens.append(board.get_fen())
                
                # 2. Pick a move (use low depth for fast generation, but inject randomness)
                # Epsilon means: with 15% probability, do something completely random
                best_move = find_best_move(board, depth=2, epsilon=epsilon)
                
                if not best_move:
                    if board.is_in_check(board.turn):
                        # If it's White's turn (0) and there are no legal moves -> Black wins -> 0.0
                        # If it's Black's turn (1) -> White wins -> 1.0
                        outcome = 0.0 if board.turn == 0 else 1.0
                    else:
                        outcome = 0.5 # Stalemate
                    break
                    
                if board.is_repetition():
                    outcome = 0.5
                    break
                    
                board.make_move(best_move)
                
            # If the loop simply finishes without break, it hit the max_halfmoves limit -> Draw
                
            # 3. Save all positions to CSV now that we know who finally won!
            for fen in game_fens:
                writer.writerow([fen, outcome])
                
            total_positions += len(game_fens)
            result_str = "White Won " if outcome == 1.0 else ("Black Won " if outcome == 0.0 else "Draw      ")
            print(f"[Game {g+1:02d}/{num_games:02d}] {result_str} | Positions saved: {len(game_fens)}")
            
        end_time = time.time()
        print(f"\n--- Report ---")
        print(f"Gathered {total_positions} fresh training positions.")
        print(f"Time Taken: {end_time - start_time:.2f} seconds.")
        print(f"Data appended to {DATA_FILE}")

if __name__ == "__main__":
    # Let's generate a batch of 10 games for our very first dataset
    generate_games(10, max_halfmoves=150, epsilon=0.15)
