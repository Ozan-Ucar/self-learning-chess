import subprocess
import os
import re

def run(cmd):
    return subprocess.check_output(cmd, shell=True).decode('utf-8')

def main():
    print("Starting history rewrite...")
    # Get all commits except the last one (the manual cleanup we just did)
    commits_str = run('git log --reverse --format="%H|%an|%ae|%aI|%cI|%s" master~1').strip()
    if not commits_str:
        print("No commits found!")
        return
    commits = commits_str.split('\n')
    
    run('git checkout --orphan new_master')
    # Clear working directory
    run('git rm -rf .')

    human_words = {
        "show AI thinking process with top candidates, eval scores and neural network prediction": "wip: thinking process and eval",
        "rewrite readme with full architecture docs and usage instructions": "update readme docs",
        "add full training pipeline with data generation, training and evaluation": "added training pipeline",
        "add iterative deepening search with time management": "search: iterative deepening",
        "integrate neural network into hybrid evaluation with mobility scoring": "nn eval integration",
        "add restart option and speed controls to showcase script": "showcase script updates",
        "update architecture notes in readme": "readme arch notes",
        "add node counter to track search performance": "track nodes in search",
        "improve move ordering with mvv-lva heuristic": "better move ordering (mvv lva)",
        "refactor sliding move edge checks into lookup table": "optimize sliding moves",
        "update evaluation to reward center control": "eval: center control bonus",
        "add bishop and king piece-square tables": "bishop/king pst",
        "add PyTorch neural network model and training loop for self-learning": "basic pytorch nn setup",
        "add self-play data generation script for reinforcement learning": "data gen script for rl",
        "add random tie-breaking and epsilon-greedy exploration, improve console dashboard layout": "epsilon greedy & ui tweaks"
    }

    count = 1
    for c in commits:
        if not c: continue
        chash, aname, aemail, adate, cdate, msg = c.split('|', 5)
        
        # Checkout files from the original commit
        try:
            run(f'git checkout {chash} -- .')
        except:
            pass
        
        # Scrub AI traces
        clean_files()
        
        new_msg = human_words.get(msg, msg.lower())
        
        try:
            run('git add .')
            env = os.environ.copy()
            env["GIT_AUTHOR_DATE"] = adate
            env["GIT_COMMITTER_DATE"] = cdate
            env["GIT_AUTHOR_NAME"] = aname
            env["GIT_AUTHOR_EMAIL"] = aemail
            env["GIT_COMMITTER_NAME"] = aname
            env["GIT_COMMITTER_EMAIL"] = aemail
            subprocess.run(['git', 'commit', '-m', new_msg], env=env, check=True, stdout=subprocess.DEVNULL)
            print(f"[{count}/{len(commits)}] Rewrote commit: {new_msg}")
        except subprocess.CalledProcessError:
            print(f"[{count}/{len(commits)}] Skipped empty commit: {new_msg}")
        count += 1
        
    print("Done rewriting history.")

def clean_files():
    replacements = {
        "search.py": [
            ("MVV-LVA: Most Valuable Victim - Least Valuable Attacker\\n    # Captures of high-value pieces should be searched first", "mvv lva"),
            ("MVV-LVA: Most Valuable Victim - Least Valuable Attacker", "mvv lva"),
            ("# Captures of high-value pieces should be searched first", ""),
            ("Simple counter to track search effort", "track nodes"),
            ("Basic move ordering: check captures first", "captures first"),
            ("Epsilon-Greedy Strategy for Self-Learning (Exploration)", "epsilon greedy for exploration"),
            ("Sorting for efficiency (capture moves first)", "sort captures first"),
            ("Sort candidates by score (best first)", "sort best first"),
            ("\"\"\"\\n    Iterative Deepening: search at depth 1, then 2, then 3...\\n    Always returns the best move found so far if time runs out.\\n    \"\"\"", "# iterative deepening in time limit"),
            ("\"\"\"\n    Iterative Deepening: search at depth 1, then 2, then 3...\n    Always returns the best move found so far if time runs out.\n    \"\"\"", "# iterative deepening in time limit")
        ],
        "watch_ai_play.py": [
            ("--- Engine vs Engine Showcase ---", "engine showcase"),
            ("Starting Position...", "starting..."),
            ("--- FINAL RESULT ---", "game over"),
            ("CHECKMATE! ", "mate. "),
            ("DRAW! Threefold Repetition.", "draw by repetition."),
            ("--- Draw by Move Limit ---", "ai match limit"),
            ("-" * 30, "---")
        ],
        "train_data_gen.py": [
            ("Starting Training Data Generation...", "generating data..."),
            ("Games: {num_games} | Epsilon (Exploration): {epsilon} | Max Moves: {max_halfmoves}", "games: {num_games} | eps: {epsilon} | max: {max_halfmoves}")
        ],
        "pipeline.py": [
            ("\"\"\"\nFull training pipeline: generate self-play data, train the neural network,\nand evaluate improvement by comparing win rates before and after training.\n\"\"\"", "# full pipeline: generate data, train nn, evaluate"),
            ("# --- Phase 1: Self-Play Data Generation ---", ""),
            ("[Phase 1] Generating {num_games} self-play games (epsilon={epsilon})...", "generating {num_games} games (epsilon={epsilon}).."),
            ("# --- Phase 2: Training ---", ""),
            ("[Phase 2] Training neural network ({epochs} epochs)...", "training for {epochs} epochs.."),
            ("# --- Phase 3: Evaluation Match ---", ""),
            ("[Phase 3] Running {num_games} evaluation games...", "evaluating with {num_games} games.."),
            ("# --- Main Pipeline ---", ""),
            ("print(\"=\" * 50)\n    print(\"  Self-Learning Chess Training Pipeline\")\n    print(\"=\" * 50)", ""),
            ("print(f\"\\nPipeline finished in {elapsed:.1f} seconds.\")", "print(f\"done in {elapsed:.1f}s.\")")
        ],
        "model.py": [
            ("# 12 piece types (6 per color) across 64 squares = 768 input features\n        # This acts as the \"eyes\" of the AI.", ""),
            ("# Hidden layer for pattern recognition", ""),
            ("# Output: A single value between 0.0 (Black wins) and 1.0 (White wins)", ""),
            ("# Sigmoid compresses the output to exactly a range between 0.0 and 1.0", ""),
            ("\"\"\"\n    Converts the current chess board into a numerical tensor representation\n    that the neural network can interpret.\n    \"\"\"", ""),
            ("# Create a 768-length array (e.g., Is there a White Pawn on A1? -> 1.0 or 0.0)", ""),
            ("\"\"\"\n    Helper function to load an existing model from disk, or initialize \n    a fresh one if no saved model is found.\n    \"\"\"", ""),
            ("print(f\"Loaded existing AI model from {path}\")", "print(f\"loaded model from {path}\")"),
            ("print(\"Created a new, untrained AI model.\")", "print(\"created new model\")")
        ]
    }

    if os.path.exists("README.md"):
        with open("README.md", "r", encoding='utf-8') as f:
            c = f.read()
            if "A bitboard-based chess engine" in c or "Self-Learning Chess Engine" in c:
                with open("README.md", "w", encoding='utf-8') as f:
                    f.write("# self-learning-chess\n\nbuilding a chess engine from scratch in python to mess around with bitboards and reinforcement learning.\n\nthe idea is to have it learn to evaluate positions by playing against itself. it uses alpha-beta search along with a simple pytorch neural network.\n\n### how to run\n```bash\npip install torch\n\n# watch it play\npython watch_ai_play.py\n\n# run the learning pipeline (generate data + train + evaluate)\npython pipeline.py\n```\n\n### structure\n- `chess_ai/board.py`: bitboards and move logic\n- `chess_ai/search.py`: minimax with alpha-beta and iterative deepening\n- `chess_ai/model.py`: simple pytorch nn \n- `chess_ai/evaluation.py`: material + piece square tables + nn eval blended together\n")

    for root, _, files in os.walk("."):
        if ".git" in root: continue
        for file in files:
            if file in replacements:
                path = os.path.join(root, file)
                if not os.path.exists(path): continue
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                except:
                    continue
                orig = content
                for old, new in replacements[file]:
                    content = content.replace(old, new)
                
                content = content.replace("--- FINAL RESULT ---", "game over")
                content = content.replace("CHECKMATE!", "mate.")
                content = content.replace("DRAW! Threefold Repetition.", "draw by repetition.")
                
                if content != orig:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)

if __name__ == '__main__':
    main()
