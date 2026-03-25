# full pipeline: generate data, train nn, evaluate
import os
import csv
import time
import torch
from chess_ai.board import Board
from chess_ai.search import find_best_move
from chess_ai.model import load_or_create_model, board_to_tensor, ChessNet
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim
import torch.nn as nn

DATA_FILE = "training_data.csv"
MODEL_FILE = "chess_model.pth"



def generate_games(num_games=50, max_halfmoves=120, epsilon=0.2):
    print(f"\ngenerating {num_games} games (epsilon={epsilon})..")
    
    file_exists = os.path.isfile(DATA_FILE)
    total_positions = 0
    results = {"White": 0, "Black": 0, "Draw": 0}
    
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["FEN", "Outcome"])
            
        for g in range(num_games):
            board = Board()
            game_fens = []
            outcome = 0.5
            
            for _ in range(max_halfmoves):
                game_fens.append(board.get_fen())
                best_move = find_best_move(board, depth=2, epsilon=epsilon)
                
                if not best_move:
                    if board.is_in_check(board.turn):
                        outcome = 0.0 if board.turn == 0 else 1.0
                    break
                if board.is_repetition():
                    break
                board.make_move(best_move)
                
            for fen in game_fens:
                writer.writerow([fen, outcome])
            total_positions += len(game_fens)
            
            if outcome == 1.0: results["White"] += 1
            elif outcome == 0.0: results["Black"] += 1
            else: results["Draw"] += 1
            
            if (g + 1) % 10 == 0:
                print(f"  [{g+1}/{num_games}] games complete...")
    
    print(f"  Generated {total_positions} positions total.")
    print(f"  Results: W={results['White']} B={results['Black']} D={results['Draw']}")
    return total_positions



class ChessDataset(Dataset):
    def __init__(self, csv_file):
        self.data = []
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) == 2:
                    self.data.append((row[0], float(row[1])))
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        fen, outcome = self.data[idx]
        board = Board()
        board.set_from_fen(fen)
        return board_to_tensor(board), torch.tensor([outcome], dtype=torch.float32)

def train_network(epochs=10, batch_size=64, lr=0.001):
    print(f"\ntraining for {epochs} epochs..")
    
    dataset = ChessDataset(DATA_FILE)
    if len(dataset) == 0:
        print("  No training data found. Skipping.")
        return
    
    # Split into train/validation (90/10)
    train_size = int(0.9 * len(dataset))
    val_size = len(dataset) - train_size
    train_set, val_set = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=batch_size)
    
    model = load_or_create_model(MODEL_FILE)
    model.train()
    
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    
    for epoch in range(epochs):
        total_loss = 0.0
        for inputs, targets in train_loader:
            optimizer.zero_grad()
            predictions = model(inputs)
            loss = criterion(predictions, targets)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        # Validation loss
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for inputs, targets in val_loader:
                preds = model(inputs)
                val_loss += criterion(preds, targets).item()
        model.train()
        
        avg_train = total_loss / max(len(train_loader), 1)
        avg_val = val_loss / max(len(val_loader), 1)
        print(f"  Epoch [{epoch+1}/{epochs}] Train Loss: {avg_train:.6f} | Val Loss: {avg_val:.6f}")
    
    torch.save(model.state_dict(), MODEL_FILE)
    print(f"  Model saved to {MODEL_FILE}")



def run_evaluation_match(num_games=10):
    print(f"\nevaluating with {num_games} games..")
    
    results = {"White": 0, "Black": 0, "Draw": 0}
    
    for g in range(num_games):
        board = Board()
        outcome = 0.5
        
        for _ in range(150):
            best_move = find_best_move(board, depth=3)
            if not best_move:
                if board.is_in_check(board.turn):
                    outcome = 0.0 if board.turn == 0 else 1.0
                break
            if board.is_repetition():
                break
            board.make_move(best_move)
        
        if outcome == 1.0: results["White"] += 1
        elif outcome == 0.0: results["Black"] += 1
        else: results["Draw"] += 1
    
    print(f"  Results: W={results['White']} B={results['Black']} D={results['Draw']}")
    return results



if __name__ == "__main__":
    
    
    start = time.time()
    
    # Step 1: Generate fresh self-play data
    generate_games(num_games=30, max_halfmoves=100, epsilon=0.2)
    
    # Step 2: Train the network on all accumulated data
    train_network(epochs=15, batch_size=64, lr=0.001)
    
    # Step 3: Run evaluation games to see how the engine plays
    run_evaluation_match(num_games=5)
    
    elapsed = time.time() - start
    print(f"done in {elapsed:.1f}s.")
