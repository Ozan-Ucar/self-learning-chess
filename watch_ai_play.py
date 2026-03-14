import time
from chess_ai.board import Board
from chess_ai.search import find_best_move

def play_engine_vs_engine(num_halmoves=10):
    board = Board()
    print("--- Engine vs Engine Showcase ---")
    print("Starting Position:")
    board.print_board(pretty=True)
    print("-" * 30)

    for i in range(num_halmoves):
        color_name = "White" if board.turn == 0 else "Black"
        print(f"\n[{i+1}] {color_name} is thinking...")
        
        start_time = time.time()
        # The engine uses Minimax (depth 3) to find the best move
        best_move = find_best_move(board, depth=3)
        end_time = time.time()
        
        if not best_move:
            if board.is_in_check(board.turn):
                print(f"Checkmate! {'Black' if color_name == 'White' else 'White'} wins.")
            else:
                print("Stalemate! Game drawn.")
            break
            
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print(f"=> ENGINE CHOOSES: {best_move.to_uci()}")
        
        # Make the move on the board
        board.make_move(best_move)
        board.print_board(pretty=True)

if __name__ == "__main__":
    play_engine_vs_engine(6) # Show 6 half-moves (3 full turns)
