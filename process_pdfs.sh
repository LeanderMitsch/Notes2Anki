#!/bin/bash

# Exit immediately if any command fails
set -e

# Configuration
VENV_DIR=".venv"
PYTHON_SCRIPT="slice_flashcards.py"
INPUT_DIR="input"
OUTPUT_DIR="output"
REQ_FILE="requirements.txt"

echo "=============================================="
echo "  reMarkable Flashcard Batch Processor"
echo "=============================================="

# 1. Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Creating virtual environment ($VENV_DIR)..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Activate virtual environment
echo "[*] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 3. Check for requirements.txt and install dependencies
if [ ! -f "$REQ_FILE" ]; then
    echo "[!] Error: '$REQ_FILE' not found in the current directory."
    echo "    -> Please ensure 'requirements.txt' exists."
    exit 1
fi

echo "[*] Installing dependencies from $REQ_FILE..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r "$REQ_FILE" > /dev/null 2>&1

# 4. Verify python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "[!] Error: Python script '$PYTHON_SCRIPT' not found in the current directory."
    exit 1
fi

# 5. Ensure input and output directories exist
if [ ! -d "$INPUT_DIR" ]; then
    mkdir -p "$INPUT_DIR"
    echo "[*] Created folder: '$INPUT_DIR/'"
    echo "    -> Drop your exported reMarkable PDFs into this folder and re-run the script!"
fi

if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
    echo "[*] Created folder: '$OUTPUT_DIR/'"
fi

# 6. Find all PDFs in the input directory
shopt -s nullglob
pdfs=("$INPUT_DIR"/*.pdf)

if [ ${#pdfs[@]} -eq 0 ]; then
    echo "[!] No PDF files found in '$INPUT_DIR/'."
    echo "    -> Drop your exported reMarkable PDFs into '$INPUT_DIR/' and re-run."
    exit 0
fi

echo "[*] Found ${#pdfs[@]} PDF(s) to process."

# 7. Loop and process each PDF, sending outputs to the output directory
for pdf in "${pdfs[@]}"; do
    echo "----------------------------------------------"
    echo "[*] Converting: $pdf"
    
    # Extract just the filename without path or extension (e.g., "math_notes")
    filename=$(basename -- "$pdf")
    basename_no_ext="${filename%.*}"
    
    # Define destination path in the output directory
    output_apkg="$OUTPUT_DIR/$basename_no_ext.apkg"
    
    # Run the Python slicer with the explicit output path
    python "$PYTHON_SCRIPT" "$pdf" -o "$output_apkg"
done

echo "----------------------------------------------"
echo "[+] Batch processing complete!"
echo "[+] All generated Anki decks are waiting in: '$OUTPUT_DIR/'"