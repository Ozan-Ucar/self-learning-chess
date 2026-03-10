from chess_ai.board import Board
from chess_ai.search import find_best_move
from chess_ai.constants import Color, Piece

def test_engine_intelligence():
    board = Board()
    
    # Let's set up a scenario where white can win a knight
    # Position: White to move, black knight is hanging
    print("--- Scenario: Black Knight is hanging on e5 ---")
    board.reset_board()
    
    # Manually move a knight to e5 (index 36)
    board.pieces[Color.BLACK][Piece.KNIGHT] = (1 << 36)
    # Clear other pieces for simple view
    board.pieces[Color.WHITE][Piece.PAWN] = (1 << 12) # Pawn on e2
    
    board.print_board()
    
    print("\nEngine is thinking (Depth 3)...")
    best_move = find_best_move(board, depth=3)
    
    if best_move:
        print(f"Engine decided: {best_move}")
        if best_move.captured_piece == Piece.KNIGHT:
            print("SUCCESS: Engine found the move that wins the knight!")
        else:
            print(f"Engine missed the knight. It played: {best_move}")
    else:
        print("No move found.")

if __name__ == "__main__":
    test_engine_intelligence()
