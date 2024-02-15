# evaluate_pylint_score.py

import sys
import re

def evaluate_pylint_score():
    lines = sys.stdin.readlines()
    
    score_line = next((line for line in lines if 'Your code has been rated at' in line), None)
    if score_line:
        score_match = re.search(r'(\d+\.\d+)', score_line)
        if score_match:
            print(f"The score is{score}")
            score = float(score_match.group(1))
            if score >= 6:
                print("Pylint score is acceptable. Proceeding with the push.")
                sys.exit(0)
            else:
                print("Pylint score is below 6. Skipping the push.")
                sys.exit(1)
        else:
            print("Unable to parse pylint score. Skipping the push.")
            sys.exit(1)
    else:
        print("Pylint score not found in output. Skipping the push.")
        sys.exit(1)

if __name__ == "__main__":
    evaluate_pylint_score()
