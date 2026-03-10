from chess_ai.board import Board
from chess_ai.evaluation import get_full_evaluation
from chess_ai.move_gen import get_knight_moves, get_pawn_moves
from chess_ai.constants import Color

def test_current_state():
    print("--- 1. Testing Board Representation ---")
    board = Board()
    board.print_board()
    
    print("\n--- 2. Testing Initial Evaluation ---")
    score = get_full_evaluation(board)
    print(f"Current Evaluation Score: {score} (0 means equal)")
    
    print("\n--- 3. Testing Piece Logic (White Knights) ---")
    white_knights = board.pieces[Color.WHITE][1] # Piece.KNIGHT is 1
    occupied = board.get_occupancy()
    
    # Let's see where the knights can jump from their starting positions
    knight_moves = get_knight_moves(white_knights)
    # Filter out squares occupied by own pieces
    valid_knight_jumps = knight_moves & ~board.get_occupancy(Color.WHITE)
    
    print(f"Bitboard for potential knight moves: {hex(valid_knight_jumps)}")
    
    # ... (rest of test_current_state)
    for r in range(7, -1, -1):
        row = ""
        for f in range(8):
            mask = 1 << (r * 8 + f)
            if valid_knight_jumps & mask:
                row += "K "
            else:
                row += ". "
        print(row)

    board.pieces[Color.WHITE][4] = 0 # Piece.QUEEN is 4
    new_score = get_full_evaluation(board)
    print(f"Board with missing White Queen. Score: {new_score}")
    if new_score == -900:
        print("Success! Engine correctly evaluates -900 (Black advantage).")
    else:
        print(f"Strange... Expected -900, got {new_score}")

    print("\n--- 5. Testing Legal Move Generation ---")
    board.reset_board() # Reset for clean test
    legal_moves = board.get_legal_moves()
    print(f"Number of legal moves from starting position: {len(legal_moves)}")
    if len(legal_moves) == 20:
        print("Success! Correctly found 20 legal moves.")
    else:
        print(f"Wait, found {len(legal_moves)} moves. Expected 20.")

if __name__ == "__main__":
    test_current_state()
