from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageDraw import ImageDraw as ImageDrawType
from src.constants import FIRST_COL_WIDTH, TABLE_PADDING

class Scheduler:
    def __init__(self, width, height, rows, cols):
        # Init values
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        # Variables for drawing
        self.draw : Optional[ImageDrawType] = None
        self.image : Optional[Image.Image] = None
        # Cells coordinates
        self.cells = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        # Create table
        self.create()


    def create(self):

        # Create a blank image and draw object
        self.image = Image.new("RGB", (self.width, self.height), "white")
        self.draw = ImageDraw.Draw(self.image)

        cell_width, cell_height = (self.width - TABLE_PADDING - FIRST_COL_WIDTH) // (self.cols - 1), (self.height - TABLE_PADDING) // self.rows

        for row in range(self.rows):
            for col in range(self.cols):

                # Leave first row and column empty
                if col == 0 and row == 0:
                    continue

                x1 = col * cell_width + TABLE_PADDING
                y1 = row * cell_height + TABLE_PADDING

                if col != 0:
                    x1 -= cell_width - FIRST_COL_WIDTH + TABLE_PADDING

                x2 = x1 + cell_width
                y2 = y1 + cell_height

                if col == 0:
                    x2 = FIRST_COL_WIDTH

                self.cells[row][col] = [x1, y1, x2, y2]
                self.draw.rectangle([x1, y1, x2, y2], outline="black")

    def write_text(self, row, col, text):

        if not self.cells[row][col]:
            return

        font = ImageFont.truetype("arial.ttf", 15)
        text_coords = self.align_text(self.cells[row][col][0], self.cells[row][col][2], self.cells[row][col][1], self.cells[row][col][3], text, font)


        # Get font size & adjust text position
        self.draw.text(xy=text_coords, text=text, fill="black", font=font)


    @staticmethod
    def get_cell_center(x1, x2):
        center = (x1 + x2) / 2
        return center

    @staticmethod
    def get_text_dimensions(text_string, font):

        ascent, descent = font.getmetrics()

        text_width = font.getmask(text_string).getbbox()[2]
        text_height = font.getmask(text_string).getbbox()[3] + descent

        return text_width, text_height

    @staticmethod
    def align_text(x1, x2, y1, y2, text_string, font):
        x_center = Scheduler.get_cell_center(x1, x2)
        y_center = Scheduler.get_cell_center(y1, y2)

        text_center = Scheduler.get_text_dimensions(text_string, font)

        x_center -= text_center[0] / 2
        y_center -= text_center[1] / 2

        return x_center, y_center

    def show(self):
        self.image.show()