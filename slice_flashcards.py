import argparse
import os
import fitz  # PyMuPDF
import genanki

# ==========================================
# CONFIGURATION (Match your template layout)
# ==========================================
RM2_WIDTH = 1404
RM2_HEIGHT = 1872
MARGIN_X = 70
TOP_MARGIN = 80
BOTTOM_MARGIN = 80
NUM_ROWS = 4
INSET = 8
TEMP_IMAGE_DIR = "extracted_cards"


def is_cell_filled(pix, threshold=0.999):
  """Determines if a cell pixmap contains handwriting/ink.

  If the dominant color (white background) ratio drops below 99.9%, it means ink
  is present.
  """
  ratio, _ = pix.color_topusage()
  return ratio < threshold


def slice_pdf_and_create_deck(pdf_path, output_apkg):
  if not os.path.exists(pdf_path):
    print(f"Error: Could not find PDF file at '{pdf_path}'.")
    return

  os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

  # Automatically derive a clean deck name from the PDF filename
  # e.g., "physics_chapter_1.pdf" -> "Physics Chapter 1"
  file_base_name = os.path.splitext(os.path.basename(pdf_path))[0]
  deck_name = file_base_name.replace("_", " ").title()

  model_id = 1607392319
  deck_id = 2059400110

  my_model = genanki.Model(
      model_id,
      "reMarkable Handwritten Model",
      fields=[{"name": "FrontImg"}, {"name": "BackImg"}],
      templates=[
          {
              "name": "Card 1",
              "qfmt": '<div style="text-align: center;">{{FrontImg}}</div>',
              "afmt": (
                  '{{FrontImg}}<hr id="answer"><div style="text-align:'
                  ' center;">{{BackImg}}</div>'
              ),
          }
      ],
  )

  my_deck = genanki.Deck(deck_id, deck_name)
  media_files = []

  doc = fitz.open(pdf_path)
  usable_height = RM2_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN
  row_height = usable_height / NUM_ROWS
  center_x = RM2_WIDTH / 2

  card_counter = 0
  skipped_counter = 0

  print(
      f"Processing '{pdf_path}' ({len(doc)} pages) into deck '{deck_name}'..."
  )

  for page_num in range(len(doc)):
    page = doc[page_num]

    for row in range(NUM_ROWS):
      y0 = TOP_MARGIN + (row * row_height)
      y1 = TOP_MARGIN + ((row + 1) * row_height)

      front_rect = fitz.Rect(
          MARGIN_X + INSET, y0 + INSET, center_x - INSET, y1 - INSET
      )
      back_rect = fitz.Rect(
          center_x + INSET, y0 + INSET, RM2_WIDTH - MARGIN_X - INSET, y1 - INSET
      )

      zoom_matrix = fitz.Matrix(2.0, 2.0)
      front_pix = page.get_pixmap(clip=front_rect, matrix=zoom_matrix)
      back_pix = page.get_pixmap(clip=back_rect, matrix=zoom_matrix)

      front_has_content = is_cell_filled(front_pix)
      back_has_content = is_cell_filled(back_pix)

      if not front_has_content and not back_has_content:
        skipped_counter += 1
        continue

      front_filename = f"p{page_num+1}_r{row+1}_front.png"
      back_filename = f"p{page_num+1}_r{row+1}_back.png"

      front_path = os.path.join(TEMP_IMAGE_DIR, front_filename)
      back_path = os.path.join(TEMP_IMAGE_DIR, back_filename)

      front_pix.save(front_path)
      back_pix.save(back_path)

      media_files.append(front_path)
      media_files.append(back_path)

      my_note = genanki.Note(
          model=my_model,
          fields=[
              f'<img src="{front_filename}">'
              if front_has_content
              else "<i>(Blank Front)</i>",
              f'<img src="{back_filename}">'
              if back_has_content
              else "<i>(Blank Back)</i>",
          ],
      )
      my_deck.add_note(my_note)
      card_counter += 1

  my_package = genanki.Package(my_deck)
  my_package.media_files = media_files
  my_package.write_to_file(output_apkg)

  print(f"\nSuccess!")
  print(f" - Deck Name: {deck_name}")
  print(f" - Created cards: {card_counter}")
  print(f" - Skipped empty rows: {skipped_counter}")
  print(f"Anki package saved to: {output_apkg}")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Slice a reMarkable flashcard PDF into an Anki .apkg deck."
  )
  parser.add_argument(
      "input_pdf", type=str, help="Path to the exported reMarkable PDF file."
  )
  parser.add_argument(
      "-o",
      "--output",
      type=str,
      default=None,
      help=(
          "Filename/path for the output Anki package (.apkg). Defaults to matching"
          " the input filename."
      ),
  )

  args = parser.parse_args()

  output_path = args.output
  if output_path is None:
    base_name = os.path.splitext(args.input_pdf)[0]
    output_path = f"{base_name}.apkg"

  slice_pdf_and_create_deck(args.input_pdf, output_path)