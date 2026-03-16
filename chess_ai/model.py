import torch
import torch.nn as nn
import torch.nn.functional as F
from chess_ai.constants import Color, Piece

class ChessNet(nn.Module):
    def __init__(self):
        super(ChessNet, self).__init__()
        
        self.fc1 = nn.Linear(768, 512)
        
        
        self.fc2 = nn.Linear(512, 128)
        
        
        self.fc3 = nn.Linear(128, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        
        x = torch.sigmoid(self.fc3(x)) 
        return x

def board_to_tensor(board):
    
    features = []
    
    
    for color in [Color.WHITE, Color.BLACK]:
        for pt in Piece:
            bb = board.pieces[color][pt]
            for i in range(64):
                features.append(1.0 if (bb & (1 << i)) else 0.0)
                
    return torch.tensor(features, dtype=torch.float32)

def load_or_create_model(path="chess_model.pth"):
    
    model = ChessNet()
    import os
    if os.path.exists(path):
        model.load_state_dict(torch.load(path))
        print(f"loaded model from {path}")
    else:
        print("created new model")
    return model
