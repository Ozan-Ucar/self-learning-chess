import time
import os
import sys
from chess_ai.board import Board
from chess_ai.search import find_best_move_timed
from chess_ai.evaluation import get_nn_evaluation

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_restart():
    print("\nPress R to restart or Q to quit.")
    if sys.platform == 'win32':
        import msvcrt
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key in (b'\xe0', b'\x00'):
                    msvcrt.getch()
                    continue
                if key.lower() == b'r': return True
                if key.lower() == b'q': return False
            time.sleep(0.05)
    return False

def format_score(score):
    if score >= 300: return f"+{score} (winning)"
    elif score >= 100: return f"+{score} (better)"
    elif score > 30: return f"+{score} (slight edge)"
    elif score >= -30: return f"{score} (equal)"
    elif score > -100: return f"{score} (slight edge)"
    elif score > -300: return f"{score} (worse)"
    else: return f"{score} (losing)"

def play_engine_vs_engine(max_halfmoves=200):
    board = Board()
    delay = 0.3 # seconds per move (use arrow keys to adjust)
    
    # Draw initial board
    clear_screen()
    print("engine showcase")
    board.print_board(pretty=True)
    print("-" * 30)
    print("starting...")
    time.sleep(1)
    
    for i in range(max_halfmoves):
        color_name = "White" if board.turn == 0 else "Black"
        
        # 1. The Engine Thinks
        start_time = time.time()
        best_move, depth_reached, nodes, candidates = find_best_move_timed(board, time_limit=1.5, max_depth=6)
        end_time = time.time()
        
        # 2. Check Game Over
        if not best_move:
            clear_screen()
            print("game over")
            board.print_board(pretty=True)
            if board.is_in_check(board.turn):
                print(f"\nmate. {'Black' if color_name == 'White' else 'White'} wins.")
            else:
                print("\nSTALEMATE! Game drawn.")
            return wait_for_restart()

        if board.is_repetition():
            clear_screen()
            print("game over")
            board.print_board(pretty=True)
            print("\ndraw by repetition.")
            return wait_for_restart()
            
        # 3. Apply the move
        time_taken = end_time - start_time
        board.make_move(best_move)
        
        # Get NN prediction for current position
        nn_raw = get_nn_evaluation(board)
        nn_pct = ((nn_raw / 2000) + 0.5) * 100 if nn_raw is not None else None
        
        # 4. Render the new screen
        clear_screen()
        print("engine showcase")
        board.print_board(pretty=True)
        print("-" * 30)
        
        print(f"Move:    [{i+1}/{max_halfmoves}]")
        print(f"Played:  {color_name} chose {best_move.to_uci()}")
        print(f"Depth:   {depth_reached} | Nodes: {nodes:,}")
        print(f"Time:    {time_taken:.2f}s")
        print("-" * 30)
        
        # Show top 3 candidates the engine considered
        if candidates:
            top = candidates[:3]
            print("Candidates:")
            for rank, (m, s) in enumerate(top, 1):
                marker = " <--" if m.to_uci() == best_move.to_uci() else ""
                print(f"  {rank}. {m.to_uci():6s} Score: {format_score(s)}{marker}")
        
        # Show NN prediction
        if nn_pct is not None:
            bar_len = 20
            filled = int(nn_pct / 100 * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"NN eval: [{bar}] {nn_pct:.0f}% White")
        
        print("-" * 30)
        next_color = "White" if board.turn == 0 else "Black"
        print(f"Status:  {next_color} is thinking...\n")
        
        # Print speed line
        sys.stdout.write(f"\rSpeed:   [{delay:.1f}s/move]  (S = Slower | F = Faster)      ")
        sys.stdout.flush()
        
        # 5. Delay and listen for keys
        start_wait = time.time()
        while time.time() - start_wait < delay:
            if sys.platform == 'win32':
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key in (b'\xe0', b'\x00'):
                        msvcrt.getch() # consume second byte from arrow keys
                    elif key.lower() == b's': delay = min(5.0, delay + 0.1)
                    elif key.lower() == b'f': delay = max(0.05, delay - 0.1)
                        
                    # Live update the speed text
                    sys.stdout.write(f"\rSpeed:   [{delay:.1f}s/move]  (S = Slower | F = Faster)      ")
                    sys.stdout.flush()
            time.sleep(0.05)

    # Show final frame (if max moves reached without mate)
    clear_screen()
    print("ai match limit")
    board.print_board(pretty=True)
    print("-" * 30)
    return wait_for_restart()

if __name__ == "__main__":
    while play_engine_vs_engine():
        pass
