import csv
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from chess_ai.model import load_or_create_model, board_to_tensor
from chess_ai.board import Board

class ChessDataset(Dataset):
    def __init__(self, csv_file):
        """
        Loads the generated self-play data from a CSV file.
        Each row should contain a FEN string and the game outcome (1.0, 0.5, or 0.0).
        """
        self.data = []
        try:
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                next(reader) # Skip header
                for row in reader:
                    if len(row) == 2:
                        self.data.append((row[0], float(row[1])))
        except FileNotFoundError:
            print(f"Error: {csv_file} not found. Please run train_data_gen.py first.")
            exit(1)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        fen, outcome = self.data[idx]
        board = Board()
        board.set_from_fen(fen)
        tensor_input = board_to_tensor(board)
        tensor_output = torch.tensor([outcome], dtype=torch.float32)
        return tensor_input, tensor_output

def train_network(epochs=5, batch_size=32, lr=0.001):
    print("Initializing Training Sequence...")
    
    # 1. Load the dataset
    dataset = ChessDataset("training_data.csv")
    if len(dataset) == 0:
        print("Dataset is empty. Aborting.")
        return
        
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    print(f"Loaded {len(dataset)} positions for training.")

    # 2. Load or create the Neural Network
    model = load_or_create_model()
    model.train() # Set to training mode

    # 3. Setup optimizer (Adam) and loss function (Mean Squared Error)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    # 4. Training Loop
    print("\n--- Starting Training ---")
    for epoch in range(epochs):
        total_loss = 0.0
        
        for batch_inputs, batch_targets in dataloader:
            # Zero the parameter gradients
            optimizer.zero_grad()
            
            # Forward pass: Ask the model what it thinks about the board
            predictions = model(batch_inputs)
            
            # Calculate how wrong the model was (Loss)
            loss = criterion(predictions, batch_targets)
            
            # Backward pass: Adjust the weights (Learning)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch [{epoch+1}/{epochs}] | Average Loss: {avg_loss:.4f}")

    # 5. Save the trained brain
    torch.save(model.state_dict(), "chess_model.pth")
    print("\n--- Training Complete ---")
    print("Model weights successfully saved to chess_model.pth")

if __name__ == "__main__":
    # Feel free to adjust epochs based on dataset size
    train_network(epochs=10, batch_size=64, lr=0.001)
