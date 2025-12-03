import os
import platform

# Graphics fix for Linux systems running a Wayland desktop environment
if platform.system() == "Linux":
    wayland_session = (
        os.environ.get("WAYLAND_DISPLAY") is not None
        or os.environ.get("XDG_SESSION_TYPE") == "wayland"
    )

    if wayland_session:
        print("Wayland detected — forcing SDL to use X11 for Pygame.")
        os.environ["SDL_VIDEODRIVER"] = "x11"

        try:
            import pygame

            pygame.display.init()
            pygame.display.quit()
        except Exception:
            print("X11 unavailable — falling back to Wayland.")
            os.environ.pop("SDL_VIDEODRIVER", None)

from antcode_ui import AntSimulation


# Entry point
if __name__ == "__main__":
    # Set up the application
    app = AntSimulation()

    # Run the application
    app.run()
