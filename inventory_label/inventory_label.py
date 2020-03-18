import argparse
import sys
from textwrap import wrap
from PIL import Image, ImageDraw, ImageFont
from pylibdmtx.pylibdmtx import encode


class InventoryLabel:

    DPI = 300
    # 62mm x 19mm labels
    LABEL_WIDTH = int(2.440945 * DPI)
    MIN_LABEL_HEIGHT = int(0.7480315 * DPI)
    LABEL_MARGIN = 0  # int(0.05 * DPI)
    DEFAULT_FONT = "DejaVuSansMono.ttf"
    MIN_FONT_SIZE = 33

    def __init__(self, font_name=None):
        # Customize label width, height, etc here
        if font_name:
            self.font_name = font_name
        else:
            self.font_name = self.DEFAULT_FONT
        pass

    # Find font size that maximizes text size
    def get_font_size(self, text, font_name, text_max_width, text_max_height):
        font_size = 1
        # TODO - Binary search for speed?

        while font_size < 1000:
            try:
                text_font = ImageFont.truetype(font_name, font_size)
            except OSError:
                print("Unable to open font file {}".format(font_name))
                sys.exit(1)

            current_width, current_height = self.draw.textsize(text, font=text_font)
            if current_width >= text_max_width or current_height >= text_max_height:
                font_size -= 1
                break

            font_size += 1

        return font_size

    # Draw text as big as possible within the bounds provided
    def draw_text(
        self,
        text,
        start_x,
        stop_x,
        start_y,
        stop_y,
        font,
        align="center",
        multiline=False,
    ):
        # use a truetype font
        font_size = self.get_font_size(
            text, font, (stop_x - start_x), (stop_y - start_y)
        )

        # If multiline is allowed, check to see if the text needs to be wrapped
        if multiline == True:
            split_text = text.split(" ")
            index = 1

            while font_size <= self.MIN_FONT_SIZE and index < len(split_text):
                line = " ".join(split_text[:-index])
                font_size = self.get_font_size(
                    line, font, (stop_x - start_x), (stop_y - start_y)
                )

                index += 1
            text = "\n".join(wrap(text, len(" ".join(split_text[:-index])) + 1))

        try:
            font = ImageFont.truetype(font, font_size)
        except OSError:
            print("Unable to open font file {}".format(font_name))
            sys.exit(1)
        text_width, text_height = self.draw.textsize(text, font=font)

        if align == "center":
            text_x = int(stop_x - start_x - text_width / 2.0)
        elif align == "left":
            text_x = start_x
        elif align == "right":
            text_x = int(stop_x - text_width)
        else:
            raise ValueError("Invalid align value")

        self.draw.text((text_x, start_y), text, font=font, align=align)

    def create_label(
        self, part_no, part_description, barcode_data, outfile, debug=False
    ):
        dm_code = encode(barcode_data, scheme="ascii")
        dm_image = Image.frombytes(
            "RGB", (dm_code.width, dm_code.height), dm_code.pixels
        )

        if dm_image.height > (self.MIN_LABEL_HEIGHT - self.LABEL_MARGIN):
            self.LABEL_HEIGHT = dm_image.height + self.LABEL_MARGIN
        else:
            self.LABEL_HEIGHT = self.MIN_LABEL_HEIGHT

        image = Image.new(
            mode="L", size=(self.LABEL_WIDTH, self.LABEL_HEIGHT), color=255
        )

        if dm_image.height > image.height:
            print("Error")

        box_center_x = int(dm_code.width / 2 + self.LABEL_MARGIN)
        box_center_y = int(self.LABEL_HEIGHT / 2)

        text_start = int(box_center_x + dm_code.width / 2 + self.LABEL_MARGIN)
        text_end = image.width - self.LABEL_MARGIN
        text_max_width = text_end - text_start

        # Insert datamatrix code into image
        image.paste(
            dm_image,
            (
                int(box_center_x - dm_code.width / 2),
                int(box_center_y - dm_code.height / 2),
                int(box_center_x + dm_code.width / 2),
                int(box_center_y + dm_code.height / 2),
            ),
        )

        self.draw = ImageDraw.Draw(image)

        self.draw_text(
            part_no,
            text_start,
            text_end,
            self.LABEL_MARGIN,
            int((image.height - 2 * self.LABEL_MARGIN) / 3.0 + self.LABEL_MARGIN),
            self.font_name,
            align="right",
        )

        self.draw_text(
            part_description,
            text_start,
            text_end,
            int((image.height - 2 * self.LABEL_MARGIN) / 3.0 + self.LABEL_MARGIN),
            image.height - self.LABEL_MARGIN,
            self.font_name,
            align="right",
            multiline=True,
        )

        if debug:
            image.show()

        if outfile:
            image.save(outfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("part_no", help="Part number")
    parser.add_argument("description", help="Description")
    parser.add_argument("barcode", help="Barcode data")
    parser.add_argument("--outfile", help="output file")
    parser.add_argument("--font", help="Font file to use")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    args = parser.parse_args()
    label = InventoryLabel(font_name=args.font)
    label.create_label(
        args.part_no,
        args.description,
        args.barcode.encode("ascii"),
        args.outfile,
        debug=args.debug,
    )
