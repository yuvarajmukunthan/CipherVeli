# CipherVeil Steganography Toolkit

CipherVeil is a unified, open-source steganography toolkit designed for advanced payload concealment across multiple digital mediums. It supports hiding AES-256-GCM encrypted data in Images, Audio files, QR Codes, Text, PDFs, and Git repository metadata.

## Features & Supported Formats

- **Universal Encryption**: All payloads are encrypted using AES-256-GCM before embedding, ensuring both confidentiality and integrity.
- **Unified CLI Interface**: Automatically detect formats when decoding and perform batch operations easily.
- **Capacity Calculation**: Built-in capacity detection ensures you never corrupt a host file by overwriting its structural limits.

| Format | Method | Capacity | Detection Risk |
|---|---|---|---|
| Image (PNG/BMP) | LSB Encoding | High (Depends on pixels) | Low to Medium (Statistical analysis) |
| Audio (WAV/FLAC) | Sample LSB Manipulation | Very High | Low (Audibly imperceptible) |
| QR Code | LSB on rendered QR | Medium | Medium |
| Text | Zero-width Unicode characters | Infinite (scales with payload) | Medium (Visible in hex editors) |
| PDF | Metadata Manipulation (`/Keywords`) | High | High (Metadata is easily scrubbed) |
| Git | Whitespace encoding in commits | Low/Medium | Low (Appears as trailing spaces) |

## Installation

Ensure you have Python 3.10+ installed.

```bash
pip install -r requirements.txt
```

## Usage

### Hiding Data (Encoding)

**Image**
```bash
python -m cipherveil_toolkit.cli -p "hunter2" encode image host.png "Top secret message" output.png
```

**Audio**
```bash
python -m cipherveil_toolkit.cli -p "hunter2" encode audio host.wav "Top secret message" output.wav
```

**Text**
```bash
python -m cipherveil_toolkit.cli -p "hunter2" encode text host.txt "Top secret message" output.txt
```

**Git Commit**
```bash
python -m cipherveil_toolkit.cli -p "hunter2" encode git /path/to/repo "Top secret message"
```

### Extracting Data (Decoding)

You don't need to specify the format; CipherVeil will auto-detect it for both files and Git repository directories.

```bash
python -m cipherveil_toolkit.cli -p "hunter2" decode output.png
```

To extract a hidden message from a Git repository:
```bash
python -m cipherveil_toolkit.cli -p "hunter2" decode /path/to/repo
```

### Batch Processing

Encode a payload across an entire directory of mixed files:
```bash
python -m cipherveil_toolkit.cli -p "hunter2" batch --input-dir ./host_files --output-dir ./stego_files "Secret payload"
```

## Theory of Operation & Applications

### Real-world Espionage & Whistleblowing Applications
Steganography provides plausible deniability. While encryption hides *what* is being said, steganography hides the *fact* that communication is occurring. Whistleblowers operating in highly surveilled environments (e.g., oppressive regimes or heavily monitored corporate networks) can use CipherVeil to exfiltrate data by uploading seemingly innocent photos to public forums or committing benign code updates to open-source repositories. 

### Detection Risks & Limitations
- **Image/Audio LSB**: Susceptible to statistical analysis (e.g., Chi-square attacks on LSBs). Any lossy compression (like uploading to social media platforms that transcode to JPEG or MP3) will destroy the payload.
- **Text Zero-Width Characters**: Invisible in most standard text editors and browsers, but immediately apparent when viewed in a hex editor or when the text is sanitized by web platforms.
- **PDF Metadata**: The easiest to manipulate but also the easiest to detect. Standard document sanitization procedures will strip custom metadata fields.
- **Git Commits**: Very stealthy as developers frequently leave trailing whitespace, but strict linting rules or `git rebase` operations will destroy the payload.

## Contributing
Contributions are welcome! Please ensure all code adheres to PEP-8 standards. When adding new modules, include corresponding unit tests in the `tests/` directory and update the format detection in `cipherveil/utils.py`.

## License
MIT License
