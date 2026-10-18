import os
import fitz  # PyMuPDF

# ==========================================
# CONFIGURATION (Must match your template/slicer)
# ==========================================
TEMPLATE_PATH = "remarkable_flashcard_grid_template.pdf"
OUTPUT_FILLED_PATH = "remarkable_filled.pdf"

RM2_WIDTH = 1404
RM2_HEIGHT = 1872
MARGIN_X = 70
TOP_MARGIN = 80
BOTTOM_MARGIN = 80
NUM_ROWS = 4  # Match your template row count


def add_test_scribbles():
  if not os.path.exists(TEMPLATE_PATH):
    print(f"Error: Could not find template file at '{TEMPLATE_PATH}'.")
    print("Please run the template generator script first.")
    return

  doc = fitz.open(TEMPLATE_PATH)
  usable_height = RM2_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN
  row_height = usable_height / NUM_ROWS
  center_x = RM2_WIDTH / 2

  print(
      f"Adding selective test scribbles to {len(doc)} pages (testing partial"
      " and empty rows)..."
  )

  for page_num, page in enumerate(doc):
    for row in range(NUM_ROWS):
      y0 = TOP_MARGIN + (row * row_height)
      y1 = TOP_MARGIN + ((row + 1) * row_height)

      front_center_x = MARGIN_X + (center_x - MARGIN_X) / 2
      back_center_x = center_x + (RM2_WIDTH - MARGIN_X - center_x) / 2
      row_center_y = y0 + (row_height / 2)

      # Test pattern per row:
      # Row 0 (index 0): Fully filled
      # Row 1 (index 1): Front only
      # Row 2 (index 2): Back only
      # Row 3 (index 3): Completely empty
      pattern_type = row % 4

      fill_front = pattern_type in [0, 1]
      fill_back = pattern_type in [0, 2]

      # If both are false, leave the row completely blank
      if not fill_front and not fill_back:
        continue

      # 1. Insert mock text labels for whatever is filled
      if fill_front:
        page.insert_text(
            fitz.Point(front_center_x - 120, row_center_y - 15),
            f"Question: P{page_num+1} R{row+1}",
            fontsize=18,
            color=(0, 0, 0),
        )
      if fill_back:
        page.insert_text(
            fitz.Point(back_center_x - 120, row_center_y - 15),
            f"Answer: P{page_num+1} R{row+1}",
            fontsize=18,
            color=(0, 0, 0),
        )

      # 2. Draw mock "handwritten" scribble lines using PyMuPDF Shape
      shape = page.new_shape()

      if fill_front:
        shape.draw_line(
            fitz.Point(front_center_x - 100, row_center_y + 20),
            fitz.Point(front_center_x + 100, row_center_y + 25),
        )
        shape.draw_line(
            fitz.Point(front_center_x - 80, row_center_y + 40),
            fitz.Point(front_center_x + 60, row_center_y + 45),
        )

      if fill_back:
        shape.draw_line(
            fitz.Point(back_center_x - 100, row_center_y + 20),
            fitz.Point(back_center_x + 100, row_center_y + 25),
        )
        shape.draw_line(
            fitz.Point(back_center_x - 80, row_center_y + 40),
            fitz.Point(back_center_x + 60, row_center_y + 45),
        )

      shape.finish(color=(0.1, 0.1, 0.1), width=2.0)
      shape.commit()

  doc.save(OUTPUT_FILLED_PATH)
  doc.close()
  print(f"Selective test filled PDF successfully generated: {OUTPUT_FILLED_PATH}")


if __name__ == "__main__":
  add_test_scribbles()