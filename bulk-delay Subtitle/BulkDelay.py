import argparse
import re
import sys
import textwrap

SRT_TIME_PATTERN = re.compile(
    r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})"
)


def time_to_ms(time_str):
    """Convert SRT time format (HH:MM:SS,mmm) to milliseconds."""
    h = int(time_str[0:2])
    m = int(time_str[3:5])
    s = int(time_str[6:8])
    ms = int(time_str[9:12])
    return h * 3600000 + m * 60000 + s * 1000 + ms


def ms_to_time(ms):
    """Convert milliseconds to SRT time format (HH:MM:SS,mmm)."""
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def adjust_time(start, end, offset_str, operation):
    """Adjust a subtitle time range by adding or subtracting an offset."""
    offset_ms = time_to_ms(offset_str)
    start_ms = time_to_ms(start)
    end_ms = time_to_ms(end)

    if operation == "add":
        start_ms += offset_ms
        end_ms += offset_ms
    elif operation == "sub":
        if start_ms < offset_ms:
            print(f"Warning: Cannot subtract {offset_str} from {start}, skipping.", file=sys.stderr)
            return None
        start_ms -= offset_ms
        end_ms -= offset_ms

    return f"{ms_to_time(start_ms)} --> {ms_to_time(end_ms)}"


def bulk_delay(input_srt, output_srt, operation, offset):
    """Apply a time offset to all subtitles in an SRT file."""
    try:
        with open(input_srt, "r") as fr:
            lines = fr.readlines()
    except FileNotFoundError:
        print(f"Error: File '{input_srt}' not found.", file=sys.stderr)
        return False

    with open(output_srt, "w") as fw:
        for line in lines:
            match = SRT_TIME_PATTERN.search(line)
            if match:
                result = adjust_time(match.group(1), match.group(2), offset, operation)
                if result is not None:
                    fw.write(result + "\n")
            else:
                fw.write(line)

    print(f"Adjusted subtitles: '{input_srt}' -> '{output_srt}' ({operation} {offset})")
    return True


def main():
    desc = textwrap.dedent("""\
        SRT Subtitle Bulk Delay

        Add or subtract a time offset from all timestamps in an SRT subtitle file.

        Usage:
            python BulkDelay.py --input movie.srt --output fixed.srt --operation add --offset 00:00:02,500
            python BulkDelay.py --input movie.srt --output fixed.srt --operation sub --offset 00:00:01,000
    """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
    )
    parser.add_argument("--input", "-I", type=str, required=True, help="Input SRT file")
    parser.add_argument("--output", "-O", type=str, required=True, help="Output SRT file")
    parser.add_argument(
        "--operation", "-op", type=str, required=True, choices=["add", "sub"],
        help="Operation: 'add' or 'sub'"
    )
    parser.add_argument("--offset", "-T", type=str, required=True, help="Time offset (HH:MM:SS,mmm)")

    args = parser.parse_args()
    bulk_delay(args.input, args.output, args.operation, args.offset)


if __name__ == "__main__":
    main()
