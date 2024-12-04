import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import os
import random
from PIL import ImageDraw

class Tile:
    def __init__(self, image_path, edges, tile_type):
        self.original_image = Image.open(image_path)
        self.edges = edges
        self.rotation = 0
        self.tile_type = tile_type

    def get_rotated_edges(self):
        rotation_steps = self.rotation // 90
        return self.edges[-rotation_steps:] + self.edges[:-rotation_steps]

    def get_rotated_image(self, size):
        return self.original_image.resize((size, size)).rotate(-self.rotation)

class CelticGame:
    def __init__(self):
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.tiles = [[None for _ in range(3)] for _ in range(3)]
        self.base_path = r"C:\Game Development\Celtic!\images"
        self.current_player = 'blue'
        
        # Initialize tile types
        self.tile_types = {
            'center': Tile(
                os.path.join(self.base_path, "centertile.PNG"),
                [True, True, True, True],
                'center'
            ),
            'blue1': Tile(
                os.path.join(self.base_path, "bluetile1.PNG"),
                [False, False, True, True],
                'blue1'
            ),
            'blue2': Tile(
                os.path.join(self.base_path, "bluetile2.PNG"),
                [False, False, True, False],
                'blue2'
            ),
            'red1': Tile(
                os.path.join(self.base_path, "redtile1PNG.PNG"),
                [False, False, True, True],
                'red1'
            ),
            'red2': Tile(
                os.path.join(self.base_path, "redtile2.PNG"),
                [False, False, True, False],
                'red2'
            )
        }

        # Place center tile
        self.place_center_tile()

    def place_center_tile(self):
        center_tile = Tile(
            os.path.join(self.base_path, "centertile.PNG"),
            [True, True, True, True],
            'center'
        )
        self.board[1][1] = 'center'
        self.tiles[1][1] = center_tile
        print("Placed center tile")

    def find_open_edges(self):
        """Find all positions with open edges"""
        open_positions = []
        for i in range(3):
            for j in range(3):
                if self.tiles[i][j]:
                    edges = self.tiles[i][j].get_rotated_edges()
                    # Check each direction
                    if i > 0 and edges[0] and not self.tiles[i-1][j]:  # Top
                        open_positions.append((i-1, j, 'bottom'))
                    if j < 2 and edges[1] and not self.tiles[i][j+1]:  # Right
                        open_positions.append((i, j+1, 'left'))
                    if i < 2 and edges[2] and not self.tiles[i+1][j]:  # Bottom
                        open_positions.append((i+1, j, 'top'))
                    if j > 0 and edges[3] and not self.tiles[i][j-1]:  # Left
                        open_positions.append((i, j-1, 'right'))
        return open_positions

    def can_place_tile(self, x, y, tile, rotation):
        """Check if a tile can be placed at position with given rotation"""
        if self.tiles[x][y]:
            return False
            
        tile.rotation = rotation
        edges = tile.get_rotated_edges()
        
        # Check borders - return False if any open edge touches a border
        if x == 0 and edges[0]:  # Top border
            return False
        if x == 2 and edges[2]:  # Bottom border
            return False
        if y == 0 and edges[3]:  # Left border
            return False
        if y == 2 and edges[1]:  # Right border
            return False
        
        # Check all neighboring tiles
        if x > 0 and self.tiles[x-1][y]:  # Top
            if edges[0] != self.tiles[x-1][y].get_rotated_edges()[2]:
                return False
        if y < 2 and self.tiles[x][y+1]:  # Right
            if edges[1] != self.tiles[x][y+1].get_rotated_edges()[3]:
                return False
        if x < 2 and self.tiles[x+1][y]:  # Bottom
            if edges[2] != self.tiles[x+1][y].get_rotated_edges()[0]:
                return False
        if y > 0 and self.tiles[x][y-1]:  # Left
            if edges[3] != self.tiles[x][y-1].get_rotated_edges()[1]:
                return False
        return True

    def build_from_edges(self):
        while True:
            open_positions = self.find_open_edges()
            if not open_positions:
                break
                
            # Choose random open position
            x, y, required_edge = random.choice(open_positions)
            
            # Get available tiles for current player
            available_tiles = ['blue1', 'blue2'] if self.current_player == 'blue' else ['red1', 'red2']
            
            # Try to place a tile
            placed = False
            for tile_type in available_tiles:
                tile = Tile(
                    self.tile_types[tile_type].original_image.filename,
                    self.tile_types[tile_type].edges,
                    tile_type
                )
                for rotation in [0, 90, 180, 270]:
                    if self.can_place_tile(x, y, tile, rotation):
                        self.tiles[x][y] = tile
                        self.board[x][y] = tile_type
                        placed = True
                        print(f"Placed {tile_type} at ({x}, {y}) with rotation {rotation}")
                        break
                if placed:
                    break
            
            if placed:
                self.current_player = 'red' if self.current_player == 'blue' else 'blue'
            else:
                print(f"Could not place tile at ({x}, {y})")

    def create_board_image(self, tile_size=100):
        img_size = tile_size * 3
        img = Image.new('RGB', (img_size, img_size), 'white')
        
        # Draw grid lines
        draw = ImageDraw.Draw(img)
        
        # Draw vertical lines
        for i in range(1, 3):
            draw.line([(i * tile_size, 0), (i * tile_size, img_size)], fill='black', width=2)
        
        # Draw horizontal lines
        for i in range(1, 3):
            draw.line([(0, i * tile_size), (img_size, i * tile_size)], fill='black', width=2)
        
        # Place tiles
        for i in range(3):
            for j in range(3):
                if self.tiles[i][j]:
                    rotated_img = self.tiles[i][j].get_rotated_image(tile_size)
                    img.paste(rotated_img, (j * tile_size, i * tile_size))
                else:
                    # Draw empty cell with light gray background
                    draw.rectangle([j * tile_size, i * tile_size, 
                                  (j + 1) * tile_size, (i + 1) * tile_size], 
                                  fill='lightgray')
        
        return img

    def is_legal_move(self, x, y, tile, rotation):
        """Check if placing tile at (x,y) with given rotation is legal"""
        if not (0 <= x < 3 and 0 <= y < 3) or self.board[x][y] is not None:
            return False

        # Apply rotation and get edges
        tile.rotation = rotation
        edges = tile.get_rotated_edges()

        # Prevent open edges from touching ANY border or corner
        # Top row checks
        if x == 0:
            if edges[0]:  # No open top edge in top row
                return False
            if y == 0 and edges[3]:  # No open left edge in top-left corner
                return False
            if y == 2 and edges[1]:  # No open right edge in top-right corner
                return False

        # Bottom row checks
        if x == 2:
            if edges[2]:  # No open bottom edge in bottom row
                return False
            if y == 0 and edges[3]:  # No open left edge in bottom-left corner
                return False
            if y == 2 and edges[1]:  # No open right edge in bottom-right corner
                return False

        # Left column checks
        if y == 0 and edges[3]:  # No open left edges in left column
            return False

        # Right column checks
        if y == 2 and edges[1]:  # No open right edges in right column
            return False

        # Check connections with neighboring tiles
        has_valid_connection = False
        
        # Check top
        if x > 0 and self.tiles[x-1][y]:
            if not self.can_connect(edges, self.tiles[x-1][y].get_rotated_edges(), 'top'):
                return False
            has_valid_connection = True

        # Check right
        if y < 2 and self.tiles[x][y+1]:
            if not self.can_connect(edges, self.tiles[x][y+1].get_rotated_edges(), 'right'):
                return False
            has_valid_connection = True

        # Check bottom
        if x < 2 and self.tiles[x+1][y]:
            if not self.can_connect(edges, self.tiles[x+1][y].get_rotated_edges(), 'bottom'):
                return False
            has_valid_connection = True

        # Check left
        if y > 0 and self.tiles[x][y-1]:
            if not self.can_connect(edges, self.tiles[x][y-1].get_rotated_edges(), 'left'):
                return False
            has_valid_connection = True

        return has_valid_connection

def visualize_game_tree_with_responses(game, max_blue_moves=3, max_red_responses=2):
    def create_and_display_tile(ax, game, tile_type, x, y, rotation, title, tile_size):
        tile = Tile(
            game.tile_types[tile_type].original_image.filename,
            game.tile_types[tile_type].edges,
            tile_type
        )
        tile.rotation = rotation
        game.tiles[x][y] = tile
        game.board[x][y] = tile_type
        board_img = game.create_board_image(tile_size=tile_size)
        ax.imshow(np.array(board_img))
        ax.set_title(title, color='white')
        ax.axis('off')
        return ax.get_position()

    def draw_connection_line(start_center, end_center, start_y, end_y):
        plt.plot([start_center[0], end_center[0]], [start_y, end_y], 'w-', alpha=0.3)

    # Create figure with black background
    fig = plt.figure(figsize=(20, 16))
    gs = plt.GridSpec(4, 6)

    # Root board (top center)
    ax_root = fig.add_subplot(gs[0, 2:4])
    root_pos = create_and_display_tile(ax_root, game, 'center', 1, 1, 0, "Initial Board", 100)
    root_center = (root_pos.x0 + root_pos.width / 2, root_pos.y0)

    # Generate blue moves
    open_positions = game.find_open_edges()
    blue_tiles = ['blue1', 'blue2']
    valid_blue_moves = []

    for x, y, required_edge in open_positions:
        for tile_type in blue_tiles:
            tile = Tile(
                game.tile_types[tile_type].original_image.filename,
                game.tile_types[tile_type].edges,
                tile_type
            )
            for rotation in [0, 90, 180, 270]:
                new_game = CelticGame()
                if new_game.can_place_tile(x, y, tile, rotation):
                    valid_blue_moves.append((x, y, tile_type, rotation))

    valid_blue_moves = valid_blue_moves[:max_blue_moves]

    for i, (bx, by, blue_tile_type, blue_rotation) in enumerate(valid_blue_moves):
        col_start = i * 2
        ax_blue = fig.add_subplot(gs[1, col_start:col_start + 2])
        blue_game = CelticGame()
        blue_pos = create_and_display_tile(
            ax_blue, blue_game, blue_tile_type, bx, by, blue_rotation,
            f"Blue: {blue_tile_type}\n({bx},{by}) {blue_rotation}°", 80
        )
        blue_center = (blue_pos.x0 + blue_pos.width / 2, blue_pos.y0 + blue_pos.height)
        draw_connection_line(root_center, blue_center, root_center[1], blue_center[1])

        # Generate red responses for this blue move
        red_game = CelticGame()
        red_game.tiles[bx][by] = blue_game.tiles[bx][by]
        red_game.board[bx][by] = blue_game.board[bx][by]
        red_game.current_player = 'red'

        open_positions = red_game.find_open_edges()
        red_tiles = ['red1', 'red2']
        valid_red_moves = []

        for rx, ry, required_edge in open_positions:
            for red_tile_type in red_tiles:
                tile = Tile(
                    game.tile_types[red_tile_type].original_image.filename,
                    game.tile_types[red_tile_type].edges,
                    red_tile_type
                )
                for rotation in [0, 90, 180, 270]:
                    if red_game.can_place_tile(rx, ry, tile, rotation):
                        valid_red_moves.append((rx, ry, red_tile_type, rotation))

        valid_red_moves = valid_red_moves[:max_red_responses]

        for j, (rx, ry, red_tile_type, red_rotation) in enumerate(valid_red_moves):
            ax_red = fig.add_subplot(gs[2 + j, col_start:col_start + 2])
            response_game = CelticGame()
            response_game.tiles[bx][by] = blue_game.tiles[bx][by]
            response_game.board[bx][by] = blue_game.board[bx][by]
            red_pos = create_and_display_tile(
                ax_red, response_game, red_tile_type, rx, ry, red_rotation,
                f"Red: {red_tile_type}\n({rx},{ry}) {red_rotation}°", 60
            )
            red_center = (red_pos.x0 + red_pos.width / 2, red_pos.y0 + red_pos.height)
            draw_connection_line(blue_center, red_center, blue_pos.y0, red_center[1])

    plt.tight_layout()
    plt.show()

# Generate and display game tree
game = CelticGame()
visualize_game_tree_with_responses(game, max_blue_moves=3, max_red_responses=2)
