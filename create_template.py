from fpdf import FPDF

# reMarkable 2 native canvas dimensions (portrait)
RM2_WIDTH = 1404
RM2_HEIGHT = 1872


class FlashcardTemplatePDF(FPDF):

  def __init__(self, num_rows=4):
    # Initialize with custom dimensions in points (pt)
    super().__init__(orientation="P", unit="pt", format=(RM2_WIDTH, RM2_HEIGHT))
    self.num_rows = num_rows

  def build_template(self, num_pages=10):
    for _ in range(num_pages):
      self.add_page()
      self.draw_grid()

  def draw_grid(self):
    # Layout configuration
    margin_x = 70
    top_margin = 80
    bottom_margin = 80

    usable_width = RM2_WIDTH - (2 * margin_x)
    usable_height = RM2_HEIGHT - top_margin - bottom_margin
    row_height = usable_height / self.num_rows

    center_x = RM2_WIDTH / 2
    top_y = top_margin
    bottom_y = top_margin + usable_height

    # Style for the lines (crisp, e-ink friendly dark gray)
    self.set_draw_color(100, 100, 100)
    self.set_line_width(1.2)

    # 1. Draw the vertical line down the middle (separating Front & Back)
    self.line(center_x, top_y, center_x, bottom_y)

    # 2. Draw horizontal lines spread evenly across the page
    for i in range(self.num_rows + 1):
      y = top_y + (i * row_height)
      self.line(margin_x, y, RM2_WIDTH - margin_x, y)


if __name__ == "__main__":
  # Create a notebook with 4 rows per page across 10 pages
  # You can change `num_rows` depending on how much space you need per card.
  pdf = FlashcardTemplatePDF(num_rows=4)
  pdf.build_template(num_pages=10)

  output_file = "remarkable_flashcard_grid_template.pdf"
  pdf.output(output_file)
  print(f"Two-column template successfully generated: {output_file}")