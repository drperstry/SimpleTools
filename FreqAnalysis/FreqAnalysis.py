import argparse
import string
import sys
import textwrap


def frequency_analysis(filepath):
    """Count the frequency of each letter in a text file.

    Returns a dictionary of letter frequencies sorted by count (ascending).
    """
    frequency = {ch: 0 for ch in string.ascii_lowercase}

    try:
        with open(filepath, "r") as f:
            for line in f:
                for ch in line.lower():
                    if ch in frequency:
                        frequency[ch] += 1
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        return None

    return dict(sorted(frequency.items(), key=lambda item: item[1]))


def main():
    desc = textwrap.dedent("""\
        Letter Frequency Analysis

        Analyze the frequency of each letter (a-z) in a text file.
        Useful for cryptanalysis of substitution ciphers.

        Usage:
            python FreqAnalysis.py --input input.txt
    """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
    )
    parser.add_argument("--input", "-I", type=str, required=True, help="Input text file to analyze")

    args = parser.parse_args()
    result = frequency_analysis(args.input)
    if result is not None:
        for letter, count in result.items():
            print(f"  {letter}: {count}")


if __name__ == "__main__":
    main()
