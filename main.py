from boardgamegeek import BGGClient
import csv
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

#A3
POSTER_SIZE_X = 3508
POSTER_SIZE_Y = 4961

OUTPUT_PATH = "target/poster.png"

OUTER_MARGINS = 4
INNER_MARGINS = 5

GAMES_COUNT_X = 10
GAMES_COUNT_Y = 10

HEADER_SIZE_Y = POSTER_SIZE_Y - POSTER_SIZE_X - 750
GAME_TEXT_SIZE_Y = 50

games_total_size_x = POSTER_SIZE_X
games_total_size_y = POSTER_SIZE_Y - HEADER_SIZE_Y

single_game_size_x = (games_total_size_x - 2 * OUTER_MARGINS) // GAMES_COUNT_X
single_image_size_x = single_game_size_x - 2 * INNER_MARGINS

single_game_size_y = (games_total_size_y - 2 * OUTER_MARGINS) // GAMES_COUNT_Y
single_image_size_y = single_game_size_y - 2 * INNER_MARGINS - GAME_TEXT_SIZE_Y - INNER_MARGINS

single_image_size_x = min(single_image_size_x, single_image_size_y)
single_image_size_y = single_image_size_x

IMAGE_MASK = Image.new('L', (single_image_size_x, single_image_size_y))
mask_draw = ImageDraw.Draw(IMAGE_MASK)
mask_draw.regular_polygon((single_image_size_x / 2, single_image_size_y / 2, single_image_size_x / 2), 6, fill=255)
# mask_draw.ellipse((0, 0, single_image_size_x, single_image_size_y), fill=255)
# IMAGE_MASK.show()
BACKGROUND_COLOR = (150, 150, 150)
TEXT_COLOR = (0, 0, 0)
OUTLINE_COLOR = (255, 255, 255)

HEADER_FONT = ImageFont.truetype("UbuntuMono-B.ttf", 150)
GAME_FONT = ImageFont.truetype("UbuntuMono-B.ttf", 16)


def write_with_outline(x, y, text, text_color, outline_color, font, align, anchor):
    draw.text((x - 1, y - 1), text, outline_color, font=font, align=align, anchor=anchor)
    draw.text((x - 1, y + 1), text, outline_color, font=font, align=align, anchor=anchor)
    draw.text((x + 1, y - 1), text, outline_color, font=font, align=align, anchor=anchor)
    draw.text((x + 1, y + 1), text, outline_color, font=font, align=align, anchor=anchor)
    draw.text((x, y), text, text_color, font=font, align=align, anchor=anchor)


games = {}
with open("boardgames_ranks.csv", "r") as f:
    lines = csv.reader(f)
    header = next(lines)
    for line in lines:
        games[int(line[3])] = int(line[0])

print(games[1])
bgg = BGGClient()
# game = bgg.game(game_id=games[1])
# r = requests.get(game.thumbnail, stream=True)
# img = Image.open(BytesIO(r.content))
# img = img.resize((single_image_size_x, single_image_size_y))
# img.show()

poster = Image.new("RGBA", (POSTER_SIZE_X, POSTER_SIZE_Y))


for y in range(GAMES_COUNT_Y):
    for x in range(GAMES_COUNT_X):
        rank = y * GAMES_COUNT_X + x + 1
        print(f"Processing rank #{rank}")
        # if y > 2 or x > 2:
        #     print("Skipping")
        #     continue

        game = bgg.game(game_id=games[rank])
        r = requests.get(game.image, stream=True)
        img = Image.open(BytesIO(r.content))
        proportion = min(single_image_size_x / img.width, single_image_size_y / img.height)
        img = img.resize((int(img.width * proportion), int(img.height * proportion)))
        x_0 = (img.width - single_image_size_x) // 2
        x_1 = x_0 + single_image_size_x
        y_0 = (img.height - single_image_size_y) // 2
        y_1 = y_0 + single_image_size_y

        img = img.crop((x_0, y_0, x_1, y_1))
        img.putalpha(IMAGE_MASK)

        x_0 = OUTER_MARGINS + x * single_game_size_x + INNER_MARGINS
        y_0 = OUTER_MARGINS + HEADER_SIZE_Y + y * single_game_size_y + INNER_MARGINS

        poster.paste(img, (x_0, y_0))

        name = game.name
        if len(name) > 40 and ":" in name:
            name = name.replace(": ", ":\n")
        text = f"{rank}.\n{name}\n{game.year}"

        draw = ImageDraw.Draw(poster)
        y_top = (y_0 + single_image_size_y)
        x_middle = x_0 + single_image_size_x / 2
        write_with_outline(x_middle, y_top, text, TEXT_COLOR, OUTLINE_COLOR, GAME_FONT, "center", "ma")

draw = ImageDraw.Draw(poster)
x_middle = POSTER_SIZE_X / 2
y_middle = OUTER_MARGINS + HEADER_SIZE_Y / 2
text = f"BOARDGAMEGEEK TOP {GAMES_COUNT_X * GAMES_COUNT_Y}\n2024"
draw.text((x_middle, y_middle), text, TEXT_COLOR, font=HEADER_FONT, align="center", anchor="mm")

draw = ImageDraw.Draw(poster)
line_width = 2 * INNER_MARGINS // 3
x_0 = OUTER_MARGINS
y_0 = OUTER_MARGINS + HEADER_SIZE_Y
x_1 = x_0 + GAMES_COUNT_X * single_game_size_x
y_1 = y_0 + GAMES_COUNT_Y * single_game_size_y
draw.line((x_0, y_0, x_0, y_1), fill=OUTLINE_COLOR, width=line_width)
draw.line((x_0, y_0, x_1, y_0), fill=OUTLINE_COLOR, width=line_width)
for i in range(GAMES_COUNT_X):
    x = x_0 + single_game_size_x * (i + 1)
    draw.line((x, y_0, x, y_1), fill=OUTLINE_COLOR, width=line_width)
for i in range(GAMES_COUNT_Y):
    y = y_0 + single_game_size_y * (i + 1)
    draw.line((x_0, y, x_1, y), fill=OUTLINE_COLOR, width=line_width)

print(f"{(POSTER_SIZE_X, POSTER_SIZE_Y)=}")
print(f"{(single_game_size_x, single_game_size_y)=}")
print(f"{(single_image_size_x, single_image_size_y)=}")
print(f"{INNER_MARGINS=}, {OUTER_MARGINS=}")


background = Image.new("RGB", poster.size, BACKGROUND_COLOR)
background.paste(poster, poster.split()[-1])
background.save(OUTPUT_PATH)
background.show()
