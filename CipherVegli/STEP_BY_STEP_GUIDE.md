# CipherVeil Steganography Toolkit: Step-by-Step Guide

Welcome to the **CipherVeil Steganography Toolkit** user guide. This document provides step-by-step instructions for configuring, using, and troubleshooting each steganography medium supported by the toolkit. 

All payloads hidden by this toolkit are automatically encrypted using robust **AES-256-GCM** encryption before embedding.

---

## Table of Contents
1. [Prerequisites & Installation](#1-prerequisites--installation)
2. [General CLI Usage Syntax](#2-general-cli-usage-syntax)
3. [Format-by-Format Guides](#3-format-by-format-guides)
    - [Image Steganography (PNG / BMP)](#image-steganography-png--bmp)
    - [Audio Steganography (WAV / FLAC)](#audio-steganography-wav--flac)
    - [QR Code Steganography](#qr-code-steganography)
    - [Plaintext Steganography (TXT / MD)](#plaintext-steganography-txt--md)
    - [PDF Steganography (PDF)](#pdf-steganography-pdf)
    - [Git Commit Steganography (Git Repository)](#git-commit-steganography-git-repository)
4. [Batch Processing (Mixed Media)](#4-batch-processing-mixed-media)
5. [Programmatic Usage (Python API)](#5-programmatic-usage-python-api)
6. [Best Practices & Security Considerations](#6-best-practices--security-considerations)

---

## 1. Prerequisites & Installation

### Step 1: Ensure Python is Installed
Make sure you have Python **3.10** or higher installed. You can check your version by running:
```bash
python --version
```

### Step 2: Initialize & Activate Virtual Environment (Recommended)
Navigate to the root directory of the toolkit and create/activate a virtual environment:

**On Windows (Command Prompt / PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
With the virtual environment active, install the toolkit dependencies:
```bash
pip install -r requirements.txt
```

---

## 2. General CLI Usage Syntax

The CLI options follow a specific hierarchy. The **password option** (`-p` or `--password`) belongs to the global group scope and **must be provided before the subcommand**.

* **Encoding Syntax:**
  ```bash
  python -m cipherveil_toolkit.cli [-p PASSWORD] encode [medium] [ARGUMENTS...]
  ```
* **Decoding Syntax:**
  ```bash
  python -m cipherveil_toolkit.cli [-p PASSWORD] decode [PATH_TO_STEGO_FILE_OR_DIR]
  ```
* **Capacity & Detection Syntax:**
  ```bash
  python -m cipherveil_toolkit.cli detect [PATH_TO_FILE]
  ```

---

## 3. Format-by-Format Guides

### Image Steganography (PNG / BMP)
Image steganography uses **Least Significant Bit (LSB)** encoding. It replaces the lowest bit of each color channel (Red, Green, Blue, Alpha) in each pixel with the bits of the encrypted payload.

#### Step 1: Verify Host Image Capacity
Before encoding, verify how much data your host image can hold:
```bash
python -m cipherveil_toolkit.cli detect host.png
```
*Output example:*
```text
Detected format: image
Max Capacity: 307200 bytes
```

#### Step 2: Hide the Message (Encode)
Use an RGB/RGBA PNG or BMP file as your host.
```bash
python -m cipherveil_toolkit.cli -p "YourSecretKey" encode image host.png "This is a hidden secret message." stego_image.png
```

#### Step 3: Extract the Message (Decode)
CipherVeil automatically detects that `stego_image.png` is an image and decodes it:
```bash
python -m cipherveil_toolkit.cli -p "YourSecretKey" decode stego_image.png
```
*Output:*
```text
Detected format: image. Decoding...
Decoded Payload: This is a hidden secret message.
```

---

### Audio Steganography (WAV / FLAC)
Audio steganography replaces the least significant bits of raw 16-bit PCM audio samples. The degradation is audibly imperceptible to the human ear.

#### Step 1: Verify Audio Host Capacity
```bash
python -m cipherveil_toolkit.cli detect host.wav
```

#### Step 2: Hide the Message (Encode)
```bash
python -m cipherveil_toolkit.cli -p "YourSecretKey" encode audio host.wav "Hidden audio message" stego_audio.wav
```

#### Step 3: Extract the Message (Decode)
```bash
python -m cipherveil_toolkit.cli -p "YourSecretKey" decode stego_audio.wav
```

---

### QR Code Steganography
This method generates a fully functioning QR Code containing public-facing text or URL data (readable by any standard QR reader), but embeds an encrypted, hidden payload inside the QR Code image using LSB manipulation. High-level Reed-Solomon error correction (`ERROR_CORRECT_H`) is applied to ensure scanning is unaffected.

#### Step 1: Generate & Hide (Encode)
* The first argument (`"https://github.com"`) is the visible data scanned by QR readers.
* The second argument (`"Secret payload inside QR"`) is the hidden data.
```bash
python -m cipherveil_toolkit.cli -p "YourSecretKey" encode qrcode "https://github.com" "Secret payload inside QR" qrcode_stego.png
```

#### Step 2: Extract the Message (Decode)
Since a QR Code is saved as an image, decode it using the unified decode helper pointing to the image file:
```bash
python -m cipherveil_toolkit.cli -p "YourSecretKey" decode qrcode_stego.png
```

---

### Plaintext Steganography (TXT / MD)
Plaintext steganography inserts zero-width Unicode characters (`\u200B` for bit 0, `\u200C` for bit 1, and `\u200D` as separators) directly after the first character of the cover text. The characters are invisible to human readers in standard text editors but visible to hex editors.

#### Step 1: Hide the Message (Encode)
Provide a standard text file (`cover.txt`) as input:
```bash
python -m cipherveil_toolkit.cli -p "YourSecretKey" encode text cover.txt "Zero-width hidden secrets" stego_text.txt
```

#### Step 2: Extract the Message (Decode)
```bash
python -m cipherveil_toolkit.cli -p "YourSecretKey" decode stego_text.txt
```

---

### PDF Steganography (PDF)
PDF steganography embeds the base64-encoded encrypted payload directly into the standard document metadata `/Keywords` field. 

#### Step 1: Hide the Message (Encode)
```bash
python -m cipherveil_toolkit.cli -p "YourSecretKey" encode pdf document.pdf "Stealthy PDF payload" stego_doc.pdf
```

#### Step 2: Extract the Message (Decode)
```bash
python -m cipherveil_toolkit.cli -p "YourSecretKey" decode stego_doc.pdf
```

---

### Git Commit Steganography (Git Repository)
This command appends a hidden whitespace signature (spaces represent bit 0, tabs represent bit 1) to an empty Git commit message.

> [!IMPORTANT]
> To prevent Git from cleaning up/removing the trailing whitespace when committing, the toolkit forces `--cleanup=verbatim` under the hood.

#### Step 1: Hide the Message (Encode)
Point the command to the root directory of an active Git repository:
```bash
python -m cipherveil_toolkit.cli -p "YourSecretKey" encode git C:\path\to\your\git_repo "Payload hidden in git logs"
```

#### Step 2: Extract the Message (Decode)
Point the unified decode command directly to the repository directory. CipherVeil detects the presence of the `.git` folder and reads the most recent commit message to retrieve the payload:
```bash
python -m cipherveil_toolkit.cli -p "YourSecretKey" decode C:\path\to\your\git_repo
```

---

## 4. Batch Processing (Mixed Media)
You can encode a single payload across an entire folder containing different supported file types (e.g., PNGs, BMPs, WAVs, TXTs, PDFs). The toolkit skips unsupported files.

```bash
python -m cipherveil_toolkit.cli -p "BatchSecret" batch --input-dir C:\my_hosts --output-dir C:\my_stego "Broadcast message to all channels"
```

---

## 5. Programmatic Usage (Python API)

You can also integrate CipherVeil directly into your Python scripts:

```python
from cipherveil_toolkit.modules import image, text
from cipherveil_toolkit import utils

# --- Example 1: Image LSB ---
# Encode
image.encode("input.png", "Secret Message", "output.png", password="SecurePassword")

# Decode
decoded_msg = image.decode("output.png", password="SecurePassword")
print("Decoded Image Payload:", decoded_msg)

# --- Example 2: Zero-Width Text ---
# Encode
text.encode("input.txt", "Invisible Text", "output.txt", password="SecurePassword")

# Decode
decoded_txt = text.decode("output.txt", password="SecurePassword")
print("Decoded Text Payload:", decoded_txt)
```

---

## 6. Best Practices & Security Considerations

* **Use Strong Passwords**: AES-256-GCM encryption is highly secure, but only as strong as the password chosen.
* **Lossy Conversions**: Avoid uploading LSB-encoded PNG images or WAV audio files to messaging platforms (like WhatsApp, Discord, or standard social media platforms) that transcode or compress files. Lossy compression (converting PNG to JPEG, or WAV to MP3) will destroy the payload.
* **Plausible Deniability**: Do not name your files `stego_output.png`. Keep the file names as benign as possible (e.g., `IMG_4829.png`).
* **Text Sanitization**: When sharing zero-width character text online, be aware that some websites strip non-printable Unicode characters before posting.
* **Linter Warnings**: Steganography in Git commits relies on trailing whitespace. Running formatting tools or linters like `git rebase` or automatic whitespace cleaners may strip the payload.
