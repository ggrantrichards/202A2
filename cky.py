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


def weightedCKY(sentence, terminals, rules):
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

    print(f"Parsing: {' '.join(sentence)}")
    chart = CKYParse(sentence, terminals, rules)
    
    final_cell = chart[0][len(sentence)]
    if "S" in final_cell:
        print(f"Sentence is valid. Top cell contains: {final_cell}")
    else:
        print("Sentence could not be parsed as S.")

if __name__ == "__main__":
    test_cky()  