"""
utils/metrics.py — CER and WER computed with pure Python Levenshtein distance.
No external metric libraries required.
"""


def levenshtein_distance(seq1: list, seq2: list) -> int:
    """
    Compute Levenshtein (edit) distance between two sequences.
    Uses dynamic programming — O(n*m) time, O(min(n,m)) space.

    Works for both character lists (CER) and word lists (WER).
    """
    n, m = len(seq1), len(seq2)

    # Optimize: ensure seq1 is the shorter sequence
    if n > m:
        seq1, seq2 = seq2, seq1
        n, m = m, n

    # Only keep two rows at a time
    current_row = list(range(n + 1))

    for j in range(1, m + 1):
        previous_row = current_row
        current_row = [j] + [0] * n

        for i in range(1, n + 1):
            insert_cost = previous_row[i] + 1
            delete_cost = current_row[i - 1] + 1
            replace_cost = previous_row[i - 1] + (0 if seq1[i - 1] == seq2[j - 1] else 1)
            current_row[i] = min(insert_cost, delete_cost, replace_cost)

    return current_row[n]


def compute_cer(reference: str, hypothesis: str) -> float:
    """
    Character Error Rate = edit_distance(ref_chars, hyp_chars) / len(ref_chars)

    Returns 0.0 if reference is empty.
    Capped at 1.0 (100% error).
    """
    if not reference:
        return 0.0

    ref_chars = list(reference)
    hyp_chars = list(hypothesis)

    distance = levenshtein_distance(ref_chars, hyp_chars)
    cer = distance / len(ref_chars)
    return min(cer, 1.0)


def compute_wer(reference: str, hypothesis: str) -> float:
    """
    Word Error Rate = edit_distance(ref_words, hyp_words) / len(ref_words)

    Returns 0.0 if reference is empty.
    Capped at 1.0 (100% error).
    """
    if not reference.strip():
        return 0.0

    ref_words = reference.strip().split()
    hyp_words = hypothesis.strip().split()

    if not ref_words:
        return 0.0

    distance = levenshtein_distance(ref_words, hyp_words)
    wer = distance / len(ref_words)
    return min(wer, 1.0)
