#!/usr/bin/env python3
"""
Slideshow with bouncing logo overlay
Controls:
- Space: Pause/unpause slideshow
- Left/Right arrows: Navigate photos manually
- Q or ESC: Quit
"""

import pygame
import os
import sys
from pathlib import Path
import time
import colorsys

# Configuration
SLIDESHOW_DELAY = 5  # seconds between photos
LOGO_SIZE = (150, 150)  # Adjust based on your logo
LOGO_SPEED = 2  # pixels per frame
FPS = 60
RAINBOW_SPEED = 0.5  # How fast the rainbow cycles (degrees per frame)

# Feature flags
SHOW_BOUNCING_LOGO = True  # Set to False to hide the bouncing logo
SHOW_PROGRESS_BAR = False   # Set to False to hide the countdown progress bar
RAINBOW_LOGO = True        # Set to False to show logo in original colors

class SlideshowWithLogo:
    def __init__(self, image_folder, logo_path):
        pygame.init()

        # Get display info and set fullscreen
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("Slideshow")
        pygame.mouse.set_visible(False)

        # Load images
        self.images = self.load_images(image_folder)
        if not self.images:
            print(f"No images found in {image_folder}")
            sys.exit(1)

        self.current_index = 0
        self.current_image = None
        self.load_current_image()

        # Load and setup logo (only if enabled)
        if SHOW_BOUNCING_LOGO:
            try:
                self.logo_original = pygame.image.load(logo_path).convert_alpha()
                self.logo_original = pygame.transform.scale(self.logo_original, LOGO_SIZE)
                self.logo = self.logo_original.copy()
            except Exception as e:
                print(f"Error loading logo: {e}")
                # Create a simple placeholder if logo fails to load
                self.logo_original = pygame.Surface(LOGO_SIZE, pygame.SRCALPHA)
                pygame.draw.circle(self.logo_original, (255, 100, 100, 200),
                                 (LOGO_SIZE[0]//2, LOGO_SIZE[1]//2), LOGO_SIZE[0]//2)
                self.logo = self.logo_original.copy()

            # Logo position and velocity
            self.logo_x = self.screen_width // 2
            self.logo_y = self.screen_height // 2
            self.logo_dx = LOGO_SPEED
            self.logo_dy = LOGO_SPEED
            self.logo_hue = 0  # Current hue for rainbow effect (0-360)
        else:
            self.logo = None
            self.logo_original = None

        # Slideshow state
        self.paused = False
        self.last_change_time = time.time()
        self.clock = pygame.time.Clock()

    def load_images(self, folder):
        """Load all image files from the folder"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        images = []

        folder_path = Path(folder)
        if not folder_path.exists():
            return images

        for file in sorted(folder_path.iterdir()):
            if file.suffix.lower() in image_extensions:
                images.append(str(file))

        return images

    def load_current_image(self):
        """Load and scale the current image to fit screen"""
        try:
            img = pygame.image.load(self.images[self.current_index])

            # Scale to fit screen while maintaining aspect ratio
            img_rect = img.get_rect()
            scale_factor = min(self.screen_width / img_rect.width,
                             self.screen_height / img_rect.height)

            new_width = int(img_rect.width * scale_factor)
            new_height = int(img_rect.height * scale_factor)

            self.current_image = pygame.transform.smoothscale(img, (new_width, new_height))
            self.image_rect = self.current_image.get_rect(center=(self.screen_width // 2,
                                                                   self.screen_height // 2))
        except Exception as e:
            print(f"Error loading image {self.images[self.current_index]}: {e}")
            # Create error placeholder
            self.current_image = pygame.Surface((400, 300))
            self.current_image.fill((50, 50, 50))
            self.image_rect = self.current_image.get_rect(center=(self.screen_width // 2,
                                                                   self.screen_height // 2))

    def next_image(self):
        """Go to next image"""
        self.current_index = (self.current_index + 1) % len(self.images)
        self.load_current_image()
        self.last_change_time = time.time()

    def prev_image(self):
        """Go to previous image"""
        self.current_index = (self.current_index - 1) % len(self.images)
        self.load_current_image()
        self.last_change_time = time.time()

    def update_logo_position(self):
        """Update logo position and bounce off edges"""
        if not SHOW_BOUNCING_LOGO:
            return

        self.logo_x += self.logo_dx
        self.logo_y += self.logo_dy

        # Bounce off edges
        if self.logo_x <= 0 or self.logo_x + LOGO_SIZE[0] >= self.screen_width:
            self.logo_dx *= -1
            # Clamp position to prevent getting stuck
            self.logo_x = max(0, min(self.logo_x, self.screen_width - LOGO_SIZE[0]))

        if self.logo_y <= 0 or self.logo_y + LOGO_SIZE[1] >= self.screen_height:
            self.logo_dy *= -1
            # Clamp position to prevent getting stuck
            self.logo_y = max(0, min(self.logo_y, self.screen_height - LOGO_SIZE[1]))

    def update_logo_color(self):
        """Apply rainbow color effect to the logo"""
        if not SHOW_BOUNCING_LOGO or not RAINBOW_LOGO:
            return

        # Update hue
        self.logo_hue = (self.logo_hue + RAINBOW_SPEED) % 360

        # Convert HSV to RGB (hue 0-360, saturation 1.0, value 1.0)
        rgb = colorsys.hsv_to_rgb(self.logo_hue / 360.0, 1.0, 1.0)
        color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

        # Create a new surface with the rainbow color applied
        self.logo = self.logo_original.copy()

        # Create a color overlay
        color_overlay = pygame.Surface(LOGO_SIZE, pygame.SRCALPHA)
        color_overlay.fill((*color, 255))

        # Multiply blend the color with the logo (this colorizes black parts)
        # We need to iterate through pixels for proper colorization
        pixel_array = pygame.surfarray.pixels3d(self.logo)
        alpha_array = pygame.surfarray.pixels_alpha(self.logo)

        # Apply color to non-transparent pixels
        for x in range(LOGO_SIZE[0]):
            for y in range(LOGO_SIZE[1]):
                if alpha_array[x, y] > 0:  # Only affect visible pixels
                    # For black logo on transparent background, replace black with the rainbow color
                    pixel_array[x, y] = color

        del pixel_array  # Unlock the surface
        del alpha_array

    def run(self):
        """Main game loop"""
        running = True

        while running:
            self.clock.tick(FPS)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                        if not self.paused:
                            self.last_change_time = time.time()
                    elif event.key == pygame.K_RIGHT:
                        self.next_image()
                    elif event.key == pygame.K_LEFT:
                        self.prev_image()

            # Auto-advance if not paused
            if not self.paused and time.time() - self.last_change_time >= SLIDESHOW_DELAY:
                self.next_image()

            # Update logo position and color
            self.update_logo_position()
            self.update_logo_color()

            # Draw everything
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.current_image, self.image_rect)

            # Draw bouncing logo (if enabled)
            if SHOW_BOUNCING_LOGO and self.logo:
                self.screen.blit(self.logo, (int(self.logo_x), int(self.logo_y)))

            # Draw progress bar at bottom (only when not paused and if enabled)
            if SHOW_PROGRESS_BAR and not self.paused:
                bar_height = int(self.screen_height * 0.02)  # 2% of screen height
                bar_y = self.screen_height - bar_height

                # Calculate progress (0 to 1, where 1 is full time remaining)
                elapsed = time.time() - self.last_change_time
                progress = 1.0 - (elapsed / SLIDESHOW_DELAY)
                progress = max(0, min(1, progress))  # Clamp between 0 and 1

                # Draw the progress bar
                bar_width = int(self.screen_width * progress)
                if bar_width > 0:
                    pygame.draw.rect(self.screen, (255, 255, 255),
                                   (0, bar_y, bar_width, bar_height))

            # Show pause indicator
            if self.paused:
                font = pygame.font.Font(None, 48)
                text = font.render("PAUSED", True, (255, 255, 255))
                text_rect = text.get_rect(center=(self.screen_width // 2, 50))
                # Draw background for text
                bg_rect = text_rect.inflate(20, 10)
                pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect)
                self.screen.blit(text, text_rect)

            pygame.display.flip()

        pygame.quit()


def main():
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Usage: python slideshow.py <image_folder> <logo_path>")
        print("Example: python slideshow.py /media/pi/USB_STICK /home/pi/logo.png")
        sys.exit(1)

    image_folder = sys.argv[1]
    logo_path = sys.argv[2]

    # Verify paths exist
    if not os.path.exists(image_folder):
        print(f"Error: Image folder '{image_folder}' not found")
        sys.exit(1)

    if not os.path.exists(logo_path):
        print(f"Error: Logo file '{logo_path}' not found")
        sys.exit(1)

    slideshow = SlideshowWithLogo(image_folder, logo_path)
    slideshow.run()


if __name__ == "__main__":
    main()
