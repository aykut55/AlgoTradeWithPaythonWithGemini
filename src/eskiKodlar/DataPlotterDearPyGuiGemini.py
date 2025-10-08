import dearpygui.dearpygui as dpg
from typing import Tuple

class DataPlotterDearPyGuiGemini:
    """
    A modular Dear PyGui plotter class with configurable panels and a main menu.
    This class provides a structured way to create a complex UI with multiple
    dockable and resizable panels.
    """
    def __init__(self, width: int = 1280, height: int = 800, title: str = "Data Plotter Gemini"):
        """
        Initializes the DataPlotterDearPyGuiGemini class.

        Args:
            width (int): The initial width of the main window.
            height (int): The initial height of the main window.
            title (str): The title of the main window.
        """
        self.width = width
        self.height = height
        self.title = title
        self._primary_window_tag = "primary_window"
        self._dpg_is_running = False

        # Tags for UI components
        self.panel_tags = {
            "upper": "upper_panel",
            "left": "left_panel",
            "right": "right_panel",
            "main": "main_panel",
            "bottom": "bottom_panel",
            "status": "status_bar"
        }

    def _create_main_menu(self):
        """Creates the main menu bar."""
        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Open")
                dpg.add_menu_item(label="Save")
                dpg.add_separator()
                dpg.add_menu_item(label="Exit", callback=lambda: dpg.stop_dearpygui())

            with dpg.menu(label="View"):
                dpg.add_menu_item(label="Toggle Upper Panel", callback=lambda: self.toggle_panel_visibility("upper"))
                dpg.add_menu_item(label="Toggle Left Panel", callback=lambda: self.toggle_panel_visibility("left"))
                dpg.add_menu_item(label="Toggle Right Panel", callback=lambda: self.toggle_panel_visibility("right"))
                dpg.add_menu_item(label="Toggle Main Panel", callback=lambda: self.toggle_panel_visibility("main"))
                dpg.add_menu_item(label="Toggle Bottom Panel", callback=lambda: self.toggle_panel_visibility("bottom"))

    def create_upper_panel(self, parent):
        """Creates the upper panel."""
        with dpg.child_window(tag=self.panel_tags["upper"], parent=parent, height=80, border=True, menubar=True):
            with dpg.menu_bar():
                dpg.add_text("Upper Panel")

    def create_left_panel(self, parent):
        """Creates the left panel."""
        with dpg.child_window(tag=self.panel_tags["left"], parent=parent, width=200, border=True, menubar=True):
            with dpg.menu_bar():
                dpg.add_text("Left Panel")

    def create_right_panel(self, parent):
        """Creates the right panel."""
        with dpg.child_window(tag=self.panel_tags["right"], parent=parent, width=200, border=True, menubar=True):
            with dpg.menu_bar():
                dpg.add_text("Right Panel")

    def create_main_panel(self, parent):
        """Creates the main content panel."""
        with dpg.child_window(tag=self.panel_tags["main"], parent=parent, border=True, menubar=True):
            with dpg.menu_bar():
                dpg.add_text("Main Panel")

    def create_bottom_panel(self, parent):
        """Creates the bottom panel."""
        with dpg.child_window(tag=self.panel_tags["bottom"], parent=parent, height=100, border=True, menubar=True):
            with dpg.menu_bar():
                dpg.add_text("Bottom Panel")

    def create_status_bar(self, parent):
        """Creates the status bar at the bottom."""
        with dpg.group(tag=self.panel_tags["status"], parent=parent, horizontal=True):
            dpg.add_text("Status: Ready")

    # --- Visibility Control Methods ---

    def show_panel(self, panel_name: str):
        """Shows a specific panel."""
        if panel_name in self.panel_tags:
            dpg.configure_item(self.panel_tags[panel_name], show=True)
        else:
            print(f"Warning: Panel '{panel_name}' not found.")

    def hide_panel(self, panel_name: str):
        """Hides a specific panel."""
        if panel_name in self.panel_tags:
            dpg.configure_item(self.panel_tags[panel_name], show=False)
        else:
            print(f"Warning: Panel '{panel_name}' not found.")

    def toggle_panel_visibility(self, panel_name: str):
        """Toggles the visibility of a specific panel."""
        if panel_name in self.panel_tags:
            tag = self.panel_tags[panel_name]
            if dpg.does_item_exist(tag):
                is_visible = dpg.is_item_shown(tag)
                dpg.configure_item(tag, show=not is_visible)
        else:
            print(f"Warning: Panel '{panel_name}' not found.")

    def run(self):
        """
        Sets up and runs the Dear PyGui application.
        This method creates the viewport, the primary window, all panels,
        and starts the render loop.
        """
        if self._dpg_is_running:
            print("DPG is already running.")
            return

        dpg.create_context()

        with dpg.window(tag=self._primary_window_tag, no_title_bar=True, no_resize=True, no_move=True):
            self._create_main_menu()

            with dpg.group():
                self.create_upper_panel(parent=dpg.last_item())
                
                # Middle section with Left, Main, Right panels
                with dpg.group(horizontal=True):
                    self.create_left_panel(parent=dpg.last_item())
                    self.create_main_panel(parent=dpg.last_item())
                    self.create_right_panel(parent=dpg.last_item())

                self.create_bottom_panel(parent=dpg.last_item())
                self.create_status_bar(parent=dpg.last_item())

        dpg.create_viewport(title=self.title, width=self.width, height=self.height)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window(self._primary_window_tag, True)
        self._dpg_is_running = True
        
        # Main loop
        while dpg.is_dearpygui_running():
            # Update window size to match viewport
            dpg.set_item_width(self._primary_window_tag, dpg.get_viewport_width())
            dpg.set_item_height(self._primary_window_tag, dpg.get_viewport_height())
            dpg.render_dearpygui_frame()

        dpg.destroy_context()
        self._dpg_is_running = False

if __name__ == '__main__':
    # Example usage:
    plotter = DataPlotterDearPyGuiGemini()
    plotter.run()
