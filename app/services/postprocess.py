"""
services/postprocess.py — AI post-processing utilities for OCR output.

Functions:
  - clean_text()     : Remove noise/artifacts from raw OCR text
  - summarize()      : Return first 1–2 sentences as summary
  - detect_headings(): Detect uppercase or heading-like lines
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean raw OCR output:
    - Normalize unicode/special characters
    - Collapse multiple spaces
    - Remove stray control characters
    - Normalize line endings
    - Trim leading/trailing whitespace per line
    """
    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove non-printable control characters (except newline and tab)
    text = re.sub(r"[^\S\n\t]+", " ", text)          # collapse whitespace
    text = re.sub(r"[^\x20-\x7E\n\t\u00A0-\uFFFF]", "", text)  # remove control chars

    # Clean each line
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        # Remove lines that are just punctuation/symbols (OCR noise)
        if line and not re.fullmatch(r"[^a-zA-Z0-9\u00C0-\uFFFF]{1,3}", line):
            lines.append(line)

    # Collapse 3+ blank lines into 2
    result = "\n".join(lines)
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result.strip()


def summarize(text: str) -> str:
    """
    Simple extractive summary: return first 1–2 meaningful sentences.
    Splits on sentence-ending punctuation.
    """
    if not text or not text.strip():
        return ""

    # Flatten to single paragraph for sentence splitting
    flat = text.replace("\n", " ")
    flat = re.sub(r"\s+", " ", flat).strip()

    # Split on sentence boundaries
    sentences = re.split(r"(?<=[.!?])\s+", flat)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if not sentences:
        # Fallback: return first 150 characters
        return flat[:150].rstrip() + ("…" if len(flat) > 150 else "")

    # Return up to 2 sentences, but cap at ~200 chars
    summary_parts = []
    char_count = 0
    for sent in sentences[:2]:
        if char_count + len(sent) > 250 and summary_parts:
            break
        summary_parts.append(sent)
        char_count += len(sent)

    return " ".join(summary_parts)


def detect_headings(text: str) -> List[str]:
    """
    Detect heading-like lines from OCR text.

    A line is considered a heading if:
    - It is fully uppercase (and at least 3 characters)
    - OR it is short (≤ 6 words) and ends without terminal punctuation
      and starts with a capital letter
    """
    if not text:
        return []

    headings = []
    seen = set()

    for line in text.split("\n"):
        line = line.strip()
        if not line or len(line) < 3:
            continue

        words = line.split()
        is_heading = False

        # Rule 1: All uppercase line
        if line.isupper() and len(line) >= 3:
            is_heading = True

        # Rule 2: Short title-like line (≤6 words, starts with capital, no terminal punct)
        elif (
            1 <= len(words) <= 6
            and line[0].isupper()
            and not line[-1] in ".,:;!?"
            and not line[-1].isdigit()
        ):
            is_heading = True

        if is_heading:
            key = line.lower()
            if key not in seen:
                headings.append(line)
                seen.add(key)

    return headings
