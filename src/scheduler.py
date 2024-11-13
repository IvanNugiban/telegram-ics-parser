from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageDraw import ImageDraw as ImageDrawType
from aiohttp.web_routedef import static

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

    def write_text(self, col, start_row, end_row, text, align_x = 'center', align_y='center',
                   font_size = 15, color = 'black', font = "arial.ttf", start_row_multiplier = 1, end_row_multiplier = 1):

        if not self.cells[start_row][col] or not self.cells[end_row][col]:
            return

        coords = self.get_centered_coords(col, start_row, end_row, start_row_multiplier, end_row_multiplier)

        font = ImageFont.truetype(font, font_size)
        text_coords = self.align_text(coords, text, font, align_x, align_y)

        # Get font size & adjust text position
        self.draw.text(xy=text_coords, text=text, fill=color, font=font)

    def draw_block(self, col, start_row,  end_row, color, start_row_multiplier = 1, end_row_multiplier = 1):

        if not self.cells[start_row][col] or not self.cells[end_row][col]:
            return

        self.draw.rectangle(self.get_centered_coords(col, start_row, end_row, start_row_multiplier, end_row_multiplier), outline="black",
                            fill=color)

    def get_cell_dimensions(self, row, col):
        return {
            'width' : self.cells[row][col][2] - self.cells[row][col][0],
            'height' : self.cells[row][col][3] - self.cells[row][col][1]
        }

    def get_centered_coords(self, col, start_row, end_row, start_row_multiplier = 1, end_row_multiplier = 1):

        cell_height = self.get_cell_dimensions(start_row, col)['height']

        if start_row == end_row:
            return self.cells[start_row][col]

        return [self.cells[start_row][col][0] + TABLE_PADDING,
                self.cells[start_row][col][1] + cell_height * start_row_multiplier,
                self.cells[end_row][col][2] - TABLE_PADDING,
                self.cells[end_row][col][3] - cell_height + cell_height * end_row_multiplier]

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
    def align_text(coords, text_string, font, align_x="center", align_y="center"):
        x_center = Scheduler.get_cell_center(coords[0], coords[2])
        y_center = Scheduler.get_cell_center(coords[1], coords[3])

        text_dimensions = Scheduler.get_text_dimensions(text_string, font)

        if align_x == "center":
            x = x_center - text_dimensions[0] / 2
        elif align_x == "left":
            x = coords[0] + TABLE_PADDING
        elif align_x == "right":
            x = coords[2] - text_dimensions[0] - TABLE_PADDING

        if align_y == "center":
            y = y_center - text_dimensions[1] / 2
        elif align_y == "top":
            y = coords[1] + TABLE_PADDING
        elif align_y == "bottom":
            y = coords[3] - text_dimensions[1] - TABLE_PADDING

        return x, y

    # @staticmethod
    # def get_font_size_for_cell(cell_coords, text):
    #     cell_width = cell_coords[2] - cell_coords[0]
    #     cell_height = cell_coords[3] - cell_coords[1]
    #
    #     # Start with a base font size
    #     font_size = 1
    #     font = ImageFont.truetype("arial.ttf", font_size)
    #
    #     # Increase font size until it exceeds cell dimensions
    #     while True:
    #         text_width, text_height = font.getbbox(text)[2:4]
    #         if text_width > cell_width / 2 or text_height > cell_height / 2:
    #             break
    #         font_size += 1
    #         font = ImageFont.truetype("arial.ttf", font_size)
    #
    #     # Return the last fitting font size
    #     return font_size - 1

    def show(self):
        self.image.show()

    def save(self, filepath):
        self.image.save(filepath)