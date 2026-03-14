import sys

def uci_loop():
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
            
        elif command == "quit":
            break
            
if __name__ == "__main__":
    uci_loop()
