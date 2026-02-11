# SimpleTools

A collection of Python tools for cryptography, network security, steganography, data privacy, and utilities.

## Tools

### Network Scanner (`Detect&PortScanner/network_scanner.py`)

Scan ports on a target host or detect incoming port scans.

```bash
python network_scanner.py scan --host 192.168.1.1 --ports 1-1024
python network_scanner.py detect   # requires root
```

### AES Encryption (`SymmetricKey-AES/AES.py`)

Encrypt/decrypt files using AES-128-CBC with PKCS7 padding.

```bash
python AES.py encrypt --key YOUR16BYTEKEY --plain Plain.txt --cipher Cipher.txt
python AES.py decrypt --key YOUR16BYTEKEY --cipher Cipher.txt --plain Plain.txt
```

### RSA Encryption (`PublicKey-RSA/RSA.py`)

Generate RSA key pairs and encrypt/decrypt files using RSA + AES hybrid encryption.

```bash
python RSA.py generate --output-dir .
python RSA.py encrypt --public-key PublicKey.pem --plaintext Plain.txt
python RSA.py decrypt --private-key PrivateKey.pem --ciphertext EncryptedText.bin
```

### Diffie-Hellman Key Exchange (`diffie-hellman/diffie_hellman.py`)

Share a symmetric key between a client and server using the Diffie-Hellman protocol.

```bash
python diffie_hellman.py server --p 23 --g 5 --b 6
python diffie_hellman.py client --a 4
```

### Frequency Analysis (`FreqAnalysis/FreqAnalysis.py`)

Analyze letter frequency in a text file (useful for cryptanalysis).

```bash
python FreqAnalysis.py --input input.txt
```

### Image Steganography (`PicSteg/PicSteg.py`)

Hide and extract secret text data in PNG images.

```bash
python PicSteg.py hide --images img1.png img2.png --secret secret.txt --output output.png
python PicSteg.py unhide --images secret0.png secret1.png --output hidden.txt
```

### K-Anonymization (`K-Anonymization/K-Anonymization.py`)

Apply k-anonymization to a dataset by recursively partitioning and generalizing quasi-identifiers.

```bash
python K-Anonymization.py --input ipums.txt --k 3
```

### GPA Calculator (`GPA_calculator/GPA_calculator.py`)

Calculate GPA from a course records file.

```bash
python GPA_calculator.py --input courses.txt --output report.txt --scale 4
```

Input file format (one course per line):
```
MATH101 4 C+
PHYS201 3 B
```

### Subtitle Bulk Delay (`bulk-delay Subtitle/BulkDelay.py`)

Add or subtract a time offset from all timestamps in an SRT subtitle file.

```bash
python BulkDelay.py --input movie.srt --output fixed.srt --operation add --offset 00:00:02,500
```

### isPrime (`isPrime.ipynb`)

Jupyter notebook demonstrating optimization techniques for prime number checking.

## Dependencies

```
pycryptodome
python-nmap
scapy
Pillow
```
