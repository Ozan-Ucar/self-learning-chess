import time
import os
import sys
from chess_ai.board import Board
from chess_ai.search import find_best_move

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def play_engine_vs_engine(max_halfmoves=200):
    board = Board()
    delay = 1.5 # Start with 1.5 seconds per move
    
    # Draw initial board
    clear_screen()
    print("--- Engine vs Engine Showcase ---")
    board.print_board(pretty=True)
    print("-" * 30)
    print("Starting Position...")
    time.sleep(1)
    
    for i in range(max_halfmoves):
        color_name = "White" if board.turn == 0 else "Black"
        
        # 1. The Engine Thinks
        start_time = time.time()
        best_move = find_best_move(board, depth=3)
        end_time = time.time()
        
        # 2. Check Game Over
        if not best_move:
            clear_screen()
            print("--- FINAL RESULT ---")
            board.print_board(pretty=True)
            if board.is_in_check(board.turn):
                print(f"\nCHECKMATE! {'Black' if color_name == 'White' else 'White'} wins.")
            else:
                print("\nSTALEMATE! Game drawn.")
            return

        if board.is_repetition():
            clear_screen()
            print("--- FINAL RESULT ---")
            board.print_board(pretty=True)
            print("\nDRAW! Threefold Repetition.")
            return
            
        # 3. Apply the move
        time_taken = end_time - start_time
        move_info = f"{color_name} played: {best_move.to_uci()} (Time: {time_taken:.2f}s)"
        board.make_move(best_move)
        
        # 4. Render the new screen
        clear_screen()
        print("--- Engine vs Engine Showcase ---")
        board.print_board(pretty=True)
        print("-" * 30)
        
        print(f"[{i+1}/{max_halfmoves}] {move_info}")
        
        next_color = "White" if board.turn == 0 else "Black"
        print(f"{next_color} is thinking...\n")
        
        # Print speed line once initially in case delay is 0
        sys.stdout.write(f"\r[Speed: {delay:.1f}s/move] Use <- Slower | Faster ->      ")
        sys.stdout.flush()
        
        # 5. Delay and listen for keys
        start_wait = time.time()
        while time.time() - start_wait < delay:
            if sys.platform == 'win32':
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key in (b'\xe0', b'\x00'): 
                        arrow = msvcrt.getch()
                        if arrow == b'K': delay = min(5.0, delay + 0.5)
                        elif arrow == b'M': delay = max(0.0, delay - 0.5)
                    elif key == b'-': delay = min(5.0, delay + 0.5)
                    elif key == b'+': delay = max(0.0, delay - 0.5)
                        
                    # Live update the speed text
                    sys.stdout.write(f"\r[Speed: {delay:.1f}s/move] Use <- Slower | Faster ->      ")
                    sys.stdout.flush()
            time.sleep(0.05)

    # Show final frame (if max moves reached without mate)
    clear_screen()
    print("--- Draw by Move Limit ---")
    board.print_board(pretty=True)
    print("-" * 30)

if __name__ == "__main__":
    play_engine_vs_engine() # Plays until mate or 200 moves
