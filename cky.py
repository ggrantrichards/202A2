# Store set of non-terminals in each cell
# Do NOT count duplicates as separate entries

from sympy.solvers.diophantine.diophantine import length
import tabulate

def CKYParse(sentence, terminals, rules):

    n = len(sentence)
    chart = [[set() for _ in range(n + 1)] for _ in range(n + 1)]

    for i in range(n):
        word = sentence[i]
        if word in terminals:
            for node in terminals[word]:
                chart[i][i+1].add(node)

    for length in range(2, n + 1): # Length of span
        for i in range(n - length + 1): # Start of span
            j = i + length # End of span

            for k in range(i + 1, j): # Split
                for B in chart[i][k]:
                    for C in chart[k][j]:
                        if (B, C) in rules:
                            for A in rules[(B, C)]:
                                chart[i][j].add(A)
    return chart


def buildTree(backpointers, i, j, symbol):
    entry = backpointers[i][j][symbol]

    if isinstance(entry, str):
        return [symbol, entry]

    k, B, C = entry

    left_subtree = buildTree(backpointers, i, k, B)
    right_subtree = buildTree(backpointers, k, j, C)

    return [symbol, left_subtree, right_subtree]

def weightedCKY(sentence, terminals, rules):
    # A. Score Table: A 2D grid where chart[i][j][NonTerminal] = max prob for symbol spanning from index i to j
    # B. Backpointer Table: A parallel 2D grid that stores how got that max prob
        # "I made this VP using a V from [1, 2] and an NP from [2, 3]
    # C. When find a rule A -> B C that fits:
        # Take the prob of the left child: P(B).
        # Take the porb of the right child: P(C)
        # Take the prob of the rule itself: P(A) -> B C
        # NewProb = P(A) -> B C * P(B) * P(C)
        # If NewProb is higher than what is currently stored for A in that cell
            # update it and save the new backpointer
    # D. Once the table is full, start at chart[0][n]['S'] and follow backpointers down to the words
    # This recursive process builds the "Most Probable Parse Tree."
    n = len(sentence)
    chart = [[{} for _ in range(n + 1)] for _ in range(n + 1)]
    backpointers = [[{} for _ in range(n + 1)] for _ in range(n + 1)]
    inside_chart = [[{} for _ in range(n + 1)] for _ in range(n + 1)]

    for i in range(n):
        word = sentence[i]
        if word in terminals:
            for node, prob in terminals[word]:
                chart[i][i+1][node] = prob
                backpointers[i][i+1][node] = word
                inside_chart[i][i+1][node] = prob

    for length in range(2, n + 1): # Length of span
        for i in range(n - length + 1): # Start of span
            j = i + length # End of span

            for k in range(i + 1, j): # Split
                for B, prob_B in chart[i][k].items():
                    for C, prob_C in chart[k][j].items():
                        if (B, C) in rules:
                            for A, prob_A_BC in rules[(B, C)]:
                                marginal_contribution = prob_A_BC * inside_chart[i][k][B] * inside_chart[k][j][C]
                                new_prob = prob_A_BC * prob_B * prob_C
                                inside_chart[i][j][A] = inside_chart[i][j].get(A, 0) + marginal_contribution

                                if A not in chart[i][j] or new_prob > chart[i][j][A]:
                                    chart[i][j][A] = new_prob
                                    backpointers[i][j][A] = (k, B, C)

    return chart, backpointers, inside_chart

def print_chart(sentence, chart):
    n = len(sentence)
    table = []
    
    for i in range(n):
        row = [sentence[i]]
        for j in range(1, n + 1):
            if j <= i:
                row.append("")
            else:
                cell_content = "\n".join([f"{k}: {v:.4e}" for k, v in chart[i][j].items()])
                row.append(cell_content if cell_content else "∅")
        table.append(row)
    
    headers = [""] + [f"j={j}" for j in range(1, n + 1)]
    print(tabulate.tabulate(table, headers=headers, tablefmt="grid"))

def test_cky():
    sentence = ["British", "left", "waffles", "on", "Falklands"]
    terminals = {
        "British": ["NP", "JJ"],
        "left": ["NP", "VP"],
        "waffles": ["NP", "VP"],
        "on": ["P"],
        "Falklands": ["NP"]
    }
    rules = {
        ("NP", "VP"): ["S"],
        ("JJ", "NP"): ["NP"],
        ("VP", "NP"): ["VP"],
        ("VP", "PP"): ["VP"],
        ("P", "NP"): ["PP"]
    }

    weighted_terminals = {
        "British": [("NP", 0.5), ("JJ", 0.5)],
        "left": [("NP", 0.3), ("VP", 0.7)],
        "waffles": [("NP", 0.2), ("VP", 0.8)],
        "on": [("P", 1.0)],
        "Falklands": [("NP", 1.0)]
    }
    weighted_rules = {
        ("NP", "VP"): [("S", 1.0)],
        ("JJ", "NP"): [("NP", 1.0)],
        ("VP", "NP"): [("VP", 0.6)],
        ("VP", "PP"): [("VP", 0.4)],
        ("P", "NP"): [("PP", 1.0)]
    }

    print(f"Parsing: {' '.join(sentence)}")
    chart = CKYParse(sentence, terminals, rules)
    
    final_cell = chart[0][len(sentence)]
    if "S" in final_cell:
        print(f"Sentence is valid. Top cell contains: {final_cell}")
    else:
        print("Sentence could not be parsed as S.")

    chart, backpointers, inside_chart = weightedCKY(sentence, weighted_terminals, weighted_rules)
    n = len(sentence)
    
    print("\n--- Final Parse Table (Inside Probabilities) ---")
    print_chart(sentence, inside_chart)

    if "S" in chart[0][n]:
        max_prob = chart[0][n]["S"]
        marginal_prob = inside_chart[0][n]["S"]
        tree = buildTree(backpointers, 0, n, "S")
        
        print(f"\nMost Probable Parse Tree:\n{tree}")
        print(f"\nViterbi Probability (Best Tree): {max_prob:.4e}")
        print(f"Marginalized Probability (All Trees): {marginal_prob:.4e}")
    else:
        print("\nSentence could not be parsed as S.")


if __name__ == "__main__":
    test_cky()  