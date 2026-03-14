import sys
from .board import Board
from .search import find_best_move

def uci_loop():
    board = Board()
    # Basic UCI protocol loop

    # Communicates via standard input/output
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            continue
            
        tokens = line.split()
        command = tokens[0]
        
        if command == "uci":
            print("id name Self-Learning Chess")
            print("id author Ozan Ucar")
            print("uciok")
            sys.stdout.flush()
            
        elif command == "isready":
            print("readyok")
            sys.stdout.flush()
            
        elif command == "position":
            if len(tokens) >= 2 and tokens[1] == "startpos":
                board.reset_board()
                moves_idx = tokens.index("moves") if "moves" in tokens else -1
                if moves_idx != -1:
                    # TODO: Properly apply moves to board state 
                    # For now just let it reset to startpos 
                    pass
            elif len(tokens) >= 2 and tokens[1] == "fen":
                fen = " ".join(tokens[2:8]) # Rough FEN reconstruction
                board.set_from_fen(fen)
                
        elif command == "go":
            # Simple fixed depth for now
            best = find_best_move(board, depth=3)
            if best:
                print(f"bestmove {best.to_uci()}")
            else:
                print("bestmove 0000") # Resign or error
            sys.stdout.flush()
            
        elif command == "quit":
            break
            
if __name__ == "__main__":
    uci_loop()

