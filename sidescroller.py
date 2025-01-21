import arcade
import pyglet

pyglet.options["shadow_window"] = False
pyglet.options["vsync"] = True

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Side Scroller"

# Constants for scaling
CHARACTER_SCALING = 2
TILE_SCALING = 0.5
OBJECT_SCALING = 1.5

# Movement constants
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1.5
PLAYER_JUMP_SPEED = 15
ENEMY_SPEED = 2


# Create a class for the game
class SideScroller(arcade.Window):
    def __init__(self):
        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        # Set up a scene object
        self.scene = None

        # Variables that will hold sprite lists
        self.player_list = None
        self.wall_list = None
        self.enemy_list = None
        self.end_list = None

        # Set up the physics engine
        self.physics_engine = None

        # A camera that will be used to scroll the screen
        self.camera = None

        # Set up GUI camera
        self.gui_camera = None

        # Set up character attributes
        self.jumps_left = 0
        self.score = 0
        self.animation_timer = 0
        self.current_frame = 0
        self.current_state = "idle"
        self.facing_right = True

        # Set up enemy patrol area. 
        self.enemy_patrol_area = {}

        # Animation textures
        self.textures = {"idle": [], "run": [], "jump": []}

        # Load sound with pyglet
        self.game_sound = pyglet.media.load("sounds/fantasy_dragon.wav", streaming=False)
        self.sound_player = pyglet.media.Player()


    def setup(self):
        # Set up the camera
        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Set up the scene
        self.scene = arcade.Scene()
        self.score = 0

        # Create sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.end_list = arcade.SpriteList()

        # Load animations and set up the player
        self.load_animations()
        self.player_sprite = arcade.Sprite()
        self.player_sprite.scale = CHARACTER_SCALING
        self.player_sprite.textures = self.textures["idle"]
        self.player_sprite.texture = self.textures["idle"][0]
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 64
        self.scene.add_sprite("Player", self.player_sprite)
        self.jumps_left = 2

        # Create the enemies
        enemy = arcade.Sprite("objects/enemy.png", CHARACTER_SCALING)
        enemy.center_x = 1600
        enemy.center_y = 64
        enemy.change_x = ENEMY_SPEED
        self.scene.add_sprite("Enemy", enemy)
        self.enemy_list.append(enemy)
        self.enemy_patrol_area[enemy] = (1570, 1800)

        # Create the ground
        for x in range(0, 5000, 24):
            wall = arcade.Sprite("objects/ground.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 24
            self.scene.add_sprite("Wall", wall)

            # Create the underground
            underground = arcade.Sprite("objects/underground.png", (TILE_SCALING + 1))
            underground.center_x = x
            underground.center_y = 0
            self.scene.add_sprite("Wall", underground)

        # Create the acorn positions
        for x in range(200, 1650, 210):
            acorn = arcade.Sprite("objects/acorn-1.png", OBJECT_SCALING)
            acorn.center_x = x
            acorn.center_y = 100
            self.scene.add_sprite("Acorns", acorn)

        # Define obstacle positions as a list of (x_start, x_end, step, y_position)
        obstacle_positions = [
            (150, 1650, 200, 50),
            (350, 1650, 200, 75),
            (550, 1650, 200, 100),
            (750, 1650, 200, 125),
            (950, 1650, 200, 150),
            (1150, 1650, 200, 175),
            (1350, 1650, 200, 200),
            (1550, 1650, 200, 225),
            (900, 1650, 200, 50),
            (1100, 1650, 200, 75),
            (1300, 1650, 200, 100),
            (1500, 1650, 200, 125),
            (1450, 1550, 200, 50)
        ]

        # Create obstacles
        for x_start, x_end, step, y_pos in obstacle_positions:
            for x in range(x_start, x_end, step):
                underground = arcade.Sprite("objects/underground.png", OBJECT_SCALING + 0.75)
                underground.center_x = x
                underground.center_y = y_pos
                self.scene.add_sprite("Wall", underground)


        # Create a house. 
        house = arcade.Sprite("objects/wooden-house.png", OBJECT_SCALING)
        house.center_x = 2000
        house.center_y = 100
        self.scene.add_sprite("end", house)

        # Create the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene.get_sprite_list("Wall")
        )

        # Play sound once on game start (non-blocking)
        self.sound_player.queue(self.game_sound)
        self.sound_player.play()

    def load_animations(self):
        # Load the idle animation
        for i in range(1, 5):
            texture = arcade.load_texture(f"player/idle/player_idle_{i}.png")
            self.textures["idle"].append(texture)

        # Load the run animation
        for i in range(1, 7):
            self.textures["run"].append(arcade.load_texture(f"player/run/player-run-{i}.png"))

        # Load the jump animation
        for i in range(1, 3):
            texture = arcade.load_texture(f"player/jump/player-jump-{i}.png")
            self.textures["jump"].append(texture)

    # Render the screen
    def on_draw(self):
        self.clear()

        # Set the camera viewport
        self.camera.use()

        # Draw the sprite lists
        self.scene.draw()

        # Activate the GUI camera
        self.gui_camera.use()

        # Draw the score
        arcade.draw_text(f"Score: {self.score}", 500, 600, arcade.color.BLACK, 14)

    # Handle the player input
    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            if self.jumps_left > 0:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jumps_left -= 1
                self.current_state = "jump"
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
            self.current_state = "idle"
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            self.current_state = "run"
            self.facing_right = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            self.current_state = "run"
            self.facing_right = True

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.RIGHT, arcade.key.A, arcade.key.D]:
            self.player_sprite.change_x = 0
        if self.physics_engine.can_jump() and self.player_sprite.change_x == 0:
            self.current_state = "idle"

    # Center the camera on the player
    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Don't let the camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    # Update the enemy positions
    def update_enemies(self):
        for enemy in self.enemy_list:

            left_bound, right_bound = self.enemy_patrol_area[enemy]

            # Reverse direction if the enemy hits a patrol boundary
            if enemy.center_x <= left_bound or enemy.center_x >= right_bound:
                enemy.change_x *= -1

            # Apply movement
            enemy.center_x += enemy.change_x

    def on_update(self, delta_time):
        # Move the player with the physics engine
        self.physics_engine.update()

        # Position the camera
        self.center_camera_to_player()

        # Update the enemy positions
        self.update_enemies()
        enemies_hit = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)

        # Check for acorn collisions
        acorns_hit = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene.get_sprite_list("Acorns")
        )

        # Loop through each acorn hit and remove it
        for acorn in acorns_hit:
            acorn.remove_from_sprite_lists()
            self.score += 1

        # Reset the jumps if the player is on the ground
        if self.physics_engine.can_jump():
            self.jumps_left = 2
            if self.player_sprite.change_x == 0:
                self.current_state = "idle"
            else:
                self.current_state = "run"
        else:
            self.current_state = "jump"

        # Update the player animation
        self.animation_timer += delta_time
        if self.animation_timer > 0.1:
            self.animation_timer = 0
            frame_count = len(self.textures[self.current_state])
            self.current_frame = (self.current_frame + 1) % frame_count

            # Dynamically flip texture
            if self.current_state == "run" and not self.facing_right:
                self.player_sprite.texture = arcade.load_texture(
                f"player/run/player-run-{self.current_frame + 1}.png", flipped_horizontally=True)
            elif self.current_state == "run" and self.facing_right:
                self.player_sprite.texture = arcade.load_texture(
                f"player/run/player-run-{self.current_frame + 1}.png")
            else:
                # For idle and jump states, no flipping is required
                self.player_sprite.texture = self.textures[self.current_state][self.current_frame]

        # Check for hitting the house. 
        house_hit = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene.get_sprite_list("end")
        )

        # Things that end the game. 
        if enemies_hit:
            arcade.close_window()

        if house_hit:            
            arcade.close_window()
            


# Set up everything and start the game
def main():
    window = SideScroller()
    window.setup()
    arcade.run()


# Execute the main method
if __name__ == "__main__":
    main()
