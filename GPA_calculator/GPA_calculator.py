import argparse
import sys
import textwrap

GRADE_SCALE = {
    "A+": 1.0,
    "A":  0.9375,
    "B+": 0.875,
    "B":  0.75,
    "C+": 0.625,
    "C":  0.5,
    "D+": 0.375,
    "D":  0.25,
}


class CourseRecord:
    def __init__(self, course, weight, letter, gpa_scale):
        self.course = course
        self.weight = weight
        self.letter = letter.upper()
        self.gpa_scale = gpa_scale
        self.earned = self.weight * gpa_scale * GRADE_SCALE.get(self.letter, 0)

    def __str__(self):
        if self.earned == 0:
            return f"  {self.course}: not counted (grade: {self.letter})"
        max_points = self.weight * self.gpa_scale
        return f"  {self.course}: {self.earned:.2f} / {max_points:.2f}"


def calculate_gpa(records):
    """Calculate GPA from a list of CourseRecord objects."""
    total_earned = sum(r.earned for r in records)
    quality_hours = sum(r.weight for r in records if r.earned > 0)
    if quality_hours == 0:
        return 0.0
    return total_earned / quality_hours


def load_records(filepath, gpa_scale):
    """Load course records from a text file.

    Expected format per line: COURSE_NAME WEIGHT LETTER_GRADE
    Example: MATH101 4 C+
    """
    records = []
    try:
        with open(filepath, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 3:
                    print(f"Warning: Skipping malformed line {line_num}: '{line}'", file=sys.stderr)
                    continue
                course = parts[0]
                try:
                    weight = float(parts[1])
                except ValueError:
                    print(f"Warning: Invalid weight on line {line_num}: '{parts[1]}'", file=sys.stderr)
                    continue
                letter = parts[2]
                records.append(CourseRecord(course, weight, letter, gpa_scale))
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    return records


def save_report(records, gpa_scale, output_path):
    """Save GPA report to a file."""
    gpa = calculate_gpa(records)
    with open(output_path, "w") as f:
        for record in records:
            f.write(str(record) + "\n")
        f.write(f"\nFinal GPA: {gpa:.4f} / {gpa_scale}\n")
    print(f"Report saved to '{output_path}'")


def main():
    desc = textwrap.dedent("""\
        GPA Calculator

        Calculate GPA from a course records file.

        Input file format (one course per line):
            COURSE_NAME  WEIGHT  LETTER_GRADE
            MATH101      4       C+
            PHYS201      3       B

        Usage:
            python GPA_calculator.py --input courses.txt --output report.txt
            python GPA_calculator.py --input courses.txt --scale 5
    """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
    )
    parser.add_argument("--input", "-I", type=str, required=True, help="Input file with course records")
    parser.add_argument("--output", "-O", type=str, default=None, help="Output file for GPA report (optional)")
    parser.add_argument("--scale", "-S", type=float, default=4.0, help="GPA scale (default: 4.0)")

    args = parser.parse_args()

    records = load_records(args.input, args.scale)
    if not records:
        print("No valid course records found.", file=sys.stderr)
        sys.exit(1)

    gpa = calculate_gpa(records)

    print("Course Records:")
    for record in records:
        print(record)
    print(f"\nFinal GPA: {gpa:.4f} / {args.scale}")

    if args.output:
        save_report(records, args.scale, args.output)


if __name__ == "__main__":
    main()
