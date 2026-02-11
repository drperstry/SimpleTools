# Image Steganography - Hide and extract secret messages in PNG images.
# Based on: https://betterprogramming.pub/image-steganography-using-python-2250896e48b9
# Extended by Abdulrahman Alhuwais for multi-image encoding/decoding.
#
# Note: Only PNG images are supported (not JPG).

import argparse
import sys
import textwrap

from PIL import Image


def _to_binary(data):
    """Convert string data to a list of 8-bit binary strings."""
    return [format(ord(ch), "08b") for ch in data]


def _modify_pixels(pixel_iter, data):
    """Modify pixel LSBs to encode data. Yields modified pixel tuples."""
    binary_data = _to_binary(data)

    for i, bits in enumerate(binary_data):
        # Extract 3 pixels (9 values) for each character (8 bits + 1 stop bit)
        pixels = [
            value
            for value in pixel_iter.__next__()[:3]
            + pixel_iter.__next__()[:3]
            + pixel_iter.__next__()[:3]
        ]

        # Set LSB: even = 0, odd = 1
        for j in range(8):
            if bits[j] == "0" and pixels[j] % 2 != 0:
                pixels[j] -= 1
            elif bits[j] == "1" and pixels[j] % 2 == 0:
                pixels[j] += 1 if pixels[j] == 0 else -1

        # Last pixel LSB: odd = end of message, even = continue
        if i == len(binary_data) - 1:
            if pixels[-1] % 2 == 0:
                pixels[-1] += 1 if pixels[-1] == 0 else -1
        else:
            if pixels[-1] % 2 != 0:
                pixels[-1] -= 1

        pixels = tuple(pixels)
        yield pixels[0:3]
        yield pixels[3:6]
        yield pixels[6:9]


def _split_string(text, n):
    """Split a string into n roughly equal parts."""
    part_size = len(text) // n
    parts = []
    start = 0
    for i in range(n):
        end = start + part_size if i < n - 1 else len(text)
        parts.append(text[start:end])
        start = end
    return parts


def encode(image_paths, secret_file, output_base):
    """Hide secret file data across multiple PNG images."""
    images = []
    for path in image_paths:
        try:
            images.append(Image.open(path, "r"))
        except FileNotFoundError:
            print(f"Error: Image '{path}' not found.", file=sys.stderr)
            return False

    try:
        with open(secret_file, "r") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: Secret file '{secret_file}' not found.", file=sys.stderr)
        return False

    if not data:
        print("Error: Secret file is empty.", file=sys.stderr)
        return False

    new_images = [img.copy() for img in images]
    data_chunks = _split_string(data, len(new_images))

    for i, img in enumerate(new_images):
        w = img.size[0]

        # First pixel stores image ordering index
        img.putpixel((0, 0), (i, 0, 0))

        x, y = 1, 0
        for pixel in _modify_pixels(iter(img.getdata()), data_chunks[i]):
            img.putpixel((x, y), pixel)
            if x == w - 1:
                x = 0
                y += 1
            else:
                x += 1

    # Save output images
    name_base, ext = output_base.rsplit(".", 1)
    for i, img in enumerate(new_images):
        output_path = f"{name_base}{i}.{ext}"
        img.save(output_path, ext.upper())
        print(f"Saved: {output_path}")

    return True


def decode(secret_image_paths, output_file):
    """Extract hidden data from steganographic images."""
    images = []
    for path in secret_image_paths:
        try:
            images.append(Image.open(path, "r"))
        except FileNotFoundError:
            print(f"Error: Image '{path}' not found.", file=sys.stderr)
            return False

    # Read image data iterators and their ordering index
    image_data = []
    for img in images:
        data_iter = iter(img.getdata())
        first_pixel = data_iter.__next__()[:3]
        order_index = first_pixel[0]
        image_data.append((order_index, data_iter))

    # Sort by ordering index
    image_data.sort(key=lambda x: x[0])

    # Extract data from each image in order
    with open(output_file, "w") as f:
        for _, data_iter in image_data:
            chunk = ""
            while True:
                pixels = [
                    value
                    for value in data_iter.__next__()[:3]
                    + data_iter.__next__()[:3]
                    + data_iter.__next__()[:3]
                ]

                binary_str = ""
                for val in pixels[:8]:
                    binary_str += "0" if val % 2 == 0 else "1"

                chunk += chr(int(binary_str, 2))

                if pixels[-1] % 2 != 0:
                    f.write(chunk)
                    break

    print(f"Hidden data extracted to '{output_file}'")
    return True


def main():
    desc = textwrap.dedent("""\
        Image Steganography

        Hide secret text data inside PNG images or extract hidden data.
        Supports distributing data across multiple images.

        Note: Only PNG images are supported.

        Usage:
            python PicSteg.py hide --images img1.png img2.png --secret secret.txt --output output.png
            python PicSteg.py unhide --images secret0.png secret1.png --output hidden.txt
    """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
    )
    subparsers = parser.add_subparsers(dest="command")

    hide_parser = subparsers.add_parser("hide", help="Hide data in images")
    hide_parser.add_argument("--images", "-I", nargs="+", type=str, required=True, help="Input carrier images")
    hide_parser.add_argument("--secret", "-S", type=str, required=True, help="Secret text file to hide")
    hide_parser.add_argument("--output", "-O", type=str, required=True, help="Output image base name (e.g., output.png)")

    unhide_parser = subparsers.add_parser("unhide", help="Extract hidden data from images")
    unhide_parser.add_argument("--images", "-I", nargs="+", type=str, required=True, help="Steganographic images")
    unhide_parser.add_argument("--output", "-O", type=str, required=True, help="Output file for extracted data")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)
    elif args.command == "hide":
        encode(args.images, args.secret, args.output)
    elif args.command == "unhide":
        decode(args.images, args.output)


if __name__ == "__main__":
    main()
