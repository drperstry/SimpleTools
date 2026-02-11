import argparse
import random
import sys
import textwrap

DIMENSIONS = ["Age", "Gender", "Marital", "Race_Status", "Birthplace", "Language", "Occupation", "Income"]


class Record:
    """Represents a single data record with quasi-identifier attributes."""

    def __init__(self, age, gender, marital, race_status, birthplace, language, occupation, income):
        self.Age = age
        self.Gender = gender
        self.Marital = marital
        self.Race_Status = race_status
        self.Birthplace = birthplace
        self.Language = language
        self.Occupation = occupation
        self.Income = income

    def dim(self, k):
        """Access attribute by dimension index."""
        return getattr(self, DIMENSIONS[k])

    def __str__(self):
        return (
            f"Age: {self.Age}, Gender: {self.Gender}, Marital: {self.Marital}, "
            f"Race_Status: {self.Race_Status}, Birthplace: {self.Birthplace}, "
            f"Language: {self.Language}, Occupation: {self.Occupation}, Income: {self.Income}"
        )


def load_records(filepath):
    """Load records from a space-separated text file."""
    records = []
    try:
        with open(filepath, "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) < 8:
                    continue
                records.append(Record(*[int(x) for x in parts[:8]]))
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    return records


def get_dimension_values(records, dim):
    """Extract and sort values for a given dimension from a list of records."""
    return sorted(r.dim(dim) for r in records)


def find_freq_set(values):
    """Build a frequency set: [[unique_values], [counts]]."""
    unique = []
    counts = []
    for v in values:
        if v in unique:
            counts[unique.index(v)] += 1
        else:
            unique.append(v)
            counts.append(1)
    return [unique, counts]


def find_cumulative_freq(freq_set):
    """Add cumulative frequency column to a frequency set."""
    result = [freq_set[0], freq_set[1], []]
    cumulative = 0
    for count in freq_set[1]:
        cumulative += count
        result[2].append(cumulative)
    return result


def find_median_index(cum_freq_set):
    """Find the median split index from a cumulative frequency set."""
    total = cum_freq_set[2][-1]
    if total % 2 == 0:
        target = total // 2 - random.randint(0, 1)
    else:
        target = total // 2
    return target


def generalize(records):
    """Generalize quasi-identifiers by replacing values with [min-max] ranges."""
    num_quasi = len(DIMENSIONS) - 1  # Exclude Income (sensitive attribute)
    for dim_idx in range(num_quasi):
        values = get_dimension_values(records, dim_idx)
        min_val = min(values)
        max_val = max(values)
        attr_name = DIMENSIONS[dim_idx]
        if min_val == max_val:
            generalized = f"[{min_val}]"
        else:
            generalized = f"[{min_val}-{max_val}]"
        for record in records:
            setattr(record, attr_name, generalized)
    return records


def anonymize(records, k):
    """Recursively partition and generalize records to achieve k-anonymity."""
    if len(records) // 2 < k:
        return generalize(records)

    dim = random.randint(0, len(DIMENSIONS) - 2)  # Random quasi-identifier dimension
    dim_values = get_dimension_values(records, dim)
    freq_set = find_freq_set(dim_values)
    cum_freq = find_cumulative_freq(freq_set)
    split_index = find_median_index(cum_freq)

    records.sort(key=lambda r: r.dim(dim))

    left = records[:split_index]
    right = records[split_index:]

    return anonymize(left, k) + anonymize(right, k)


def main():
    desc = textwrap.dedent("""\
        K-Anonymization

        Apply k-anonymization to a dataset by recursively partitioning
        and generalizing quasi-identifiers.

        Input file: space-separated values with 8 columns per row
        (Age, Gender, Marital, Race_Status, Birthplace, Language, Occupation, Income)

        Usage:
            python K-Anonymization.py --input ipums.txt --k 3
    """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
    )
    parser.add_argument("--input", "-I", type=str, default="ipums.txt", help="Input dataset file (default: ipums.txt)")
    parser.add_argument("--k", "-K", type=int, default=3, help="K-anonymity parameter (default: 3)")

    args = parser.parse_args()

    records = load_records(args.input)
    if not records:
        print("No records loaded.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(records)} records. Applying {args.k}-anonymization...")
    result = anonymize(records, args.k)

    for record in result:
        print(record)

    print(f"\nAnonymized {len(result)} records with k={args.k}")


if __name__ == "__main__":
    main()
