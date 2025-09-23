"""
DataPlotterDearPyGui2 - Financial data visualization framework using Dear PyGui.

This module implements a comprehensive financial data visualization framework
with modular wrapper classes for menu, panels, and status bar management.
"""

try:
    import dearpygui.dearpygui as dpg
    DEARPYGUI_AVAILABLE = True
except ImportError:
    DEARPYGUI_AVAILABLE = False
    print("Dear PyGui not available. Install with: pip install dearpygui")

import numpy as np
from typing import Optional, List, Dict, Any, Tuple, Callable
from datetime import datetime
import math


class MenuWrapper:
    """Menu bar management wrapper."""

    def __init__(self, parent_tag: str):
        self.parent_tag = parent_tag
        self.menu_bar_tag = f"{parent_tag}_menu_bar"
        self.visible = True
        self.menu_items = {}

    def SetVisibility(self, visible: bool) -> None:
        """Set menu visibility."""
        self.visible = visible
        if dpg.does_item_exist(self.menu_bar_tag):
            dpg.configure_item(self.menu_bar_tag, show=visible)

    def AddItem(self, label: str, callback: Optional[Callable] = None) -> str:
        """Add top-level menu item."""
        menu_tag = f"{self.menu_bar_tag}_{label}"
        if dpg.does_item_exist(self.menu_bar_tag):
            with dpg.menu(label=label, tag=menu_tag, parent=self.menu_bar_tag):
                pass
        self.menu_items[label] = {"tag": menu_tag, "children": {}}
        return menu_tag

    def AddSubItem(self, parent: str, label: str, callback: Optional[Callable] = None) -> str:
        """Add sub menu item."""
        if parent in self.menu_items:
            parent_tag = self.menu_items[parent]["tag"]
            item_tag = f"{parent_tag}_{label}"
            if dpg.does_item_exist(parent_tag):
                dpg.add_menu_item(label=label, tag=item_tag, parent=parent_tag, callback=callback)
            self.menu_items[parent]["children"][label] = {"tag": item_tag, "callback": callback}
            return item_tag
        return ""


class PanelWrapper:
    """Panel management wrapper for all types of panels."""

    def __init__(self, panel_tag: str, parent_tag: str = ""):
        self.panel_tag = panel_tag
        self.parent_tag = parent_tag
        self.visible = True
        self.content_items = []

    def SetVisibility(self, visible: bool) -> None:
        """Set panel visibility."""
        self.visible = visible
        if dpg.does_item_exist(self.panel_tag):
            dpg.configure_item(self.panel_tag, show=visible)

    def AddButton(self, label: str, callback: Optional[Callable] = None, **kwargs) -> str:
        """Add button to panel."""
        button_tag = f"{self.panel_tag}_btn_{len(self.content_items)}"
        if dpg.does_item_exist(self.panel_tag):
            dpg.add_button(label=label, tag=button_tag, parent=self.panel_tag,
                          callback=callback, **kwargs)
        self.content_items.append({"type": "button", "tag": button_tag, "label": label})
        return button_tag

    def AddText(self, value: str, **kwargs) -> str:
        """Add text to panel."""
        text_tag = f"{self.panel_tag}_text_{len(self.content_items)}"
        if dpg.does_item_exist(self.panel_tag):
            dpg.add_text(value, tag=text_tag, parent=self.panel_tag, **kwargs)
        self.content_items.append({"type": "text", "tag": text_tag, "value": value})
        return text_tag

    def AddIndicator(self, indicator_type: str, state: Any, **kwargs) -> str:
        """Add indicator to panel."""
        indicator_tag = f"{self.panel_tag}_indicator_{len(self.content_items)}"
        if dpg.does_item_exist(self.panel_tag):
            if indicator_type == "led":
                # LED style indicator using colored button
                color = [0, 255, 0, 255] if state else [255, 0, 0, 255]
                dpg.add_button(label="●", tag=indicator_tag, parent=self.panel_tag,
                              width=20, height=20, **kwargs)
            elif indicator_type == "progress":
                dpg.add_progress_bar(tag=indicator_tag, parent=self.panel_tag,
                                   default_value=float(state), **kwargs)
        self.content_items.append({"type": "indicator", "tag": indicator_tag,
                                 "indicator_type": indicator_type, "state": state})
        return indicator_tag

    def AddMemo(self, initial_text: str = "", **kwargs) -> str:
        """Add memo/text input to panel."""
        memo_tag = f"{self.panel_tag}_memo_{len(self.content_items)}"
        if dpg.does_item_exist(self.panel_tag):
            dpg.add_input_text(tag=memo_tag, parent=self.panel_tag,
                              default_value=initial_text, multiline=True, **kwargs)
        self.content_items.append({"type": "memo", "tag": memo_tag, "text": initial_text})
        return memo_tag

    def AddPlot(self, plot_type: str, series_data: Dict[str, Any], options: Dict[str, Any] = None) -> str:
        """Add plot to panel."""
        plot_tag = f"{self.panel_tag}_plot_{len(self.content_items)}"
        if options is None:
            options = {}

        if dpg.does_item_exist(self.panel_tag):
            height = options.get("height", 300)
            width = options.get("width", -1)

            dpg.add_plot(tag=plot_tag, parent=self.panel_tag, height=height, width=width,
                        label=options.get("title", "Plot"))

            x_axis_tag = f"{plot_tag}_x_axis"
            y_axis_tag = f"{plot_tag}_y_axis"

            dpg.add_plot_axis(dpg.mvXAxis, tag=x_axis_tag, parent=plot_tag, label="Time")
            dpg.add_plot_axis(dpg.mvYAxis, tag=y_axis_tag, parent=plot_tag, label="Value")

            self._add_series_to_plot(plot_type, series_data, x_axis_tag, y_axis_tag, options)

        self.content_items.append({"type": "plot", "tag": plot_tag, "plot_type": plot_type,
                                 "series_data": series_data, "options": options})
        return plot_tag

    def _add_series_to_plot(self, plot_type: str, series_data: Dict[str, Any],
                          x_axis_tag: str, y_axis_tag: str, options: Dict[str, Any]) -> None:
        """Add series data to plot based on type."""
        if plot_type == "candlestick":
            self._add_candlestick_series(series_data, x_axis_tag, y_axis_tag, options)
        elif plot_type == "line":
            self._add_line_series(series_data, x_axis_tag, y_axis_tag, options)
        elif plot_type == "bar":
            self._add_bar_series(series_data, x_axis_tag, y_axis_tag, options)

    def _add_candlestick_series(self, series_data: Dict[str, Any],
                               x_axis_tag: str, y_axis_tag: str, options: Dict[str, Any]) -> None:
        """Add candlestick series (OHLC)."""
        timestamps = series_data.get("timestamps", [])
        open_data = series_data.get("open", [])
        high_data = series_data.get("high", [])
        low_data = series_data.get("low", [])
        close_data = series_data.get("close", [])

        if timestamps and open_data and high_data and low_data and close_data:
            x_data = list(range(len(timestamps)))

            # Create candlestick using multiple series
            for i in range(len(x_data)):
                if i < len(open_data) and i < len(high_data) and i < len(low_data) and i < len(close_data):
                    o, h, l, c = open_data[i], high_data[i], low_data[i], close_data[i]
                    color = [0, 255, 0, 255] if c >= o else [255, 0, 0, 255]

                    # High-Low line
                    dpg.add_line_series([x_data[i], x_data[i]], [l, h],
                                       parent=y_axis_tag, tag=f"{y_axis_tag}_hl_{i}")

                    # Body rectangle (simulated with thick line)
                    body_top = max(o, c)
                    body_bottom = min(o, c)
                    if body_top != body_bottom:
                        dpg.add_line_series([x_data[i], x_data[i]], [body_bottom, body_top],
                                           parent=y_axis_tag, tag=f"{y_axis_tag}_body_{i}")

    def _add_line_series(self, series_data: Dict[str, Any],
                        x_axis_tag: str, y_axis_tag: str, options: Dict[str, Any]) -> None:
        """Add line series."""
        for name, data in series_data.items():
            if isinstance(data, (list, np.ndarray)) and len(data) > 0:
                x_data = list(range(len(data)))
                y_data = list(data)
                series_tag = f"{y_axis_tag}_{name}"
                dpg.add_line_series(x_data, y_data, tag=series_tag, parent=y_axis_tag, label=name)

    def _add_bar_series(self, series_data: Dict[str, Any],
                       x_axis_tag: str, y_axis_tag: str, options: Dict[str, Any]) -> None:
        """Add bar series."""
        for name, data in series_data.items():
            if isinstance(data, (list, np.ndarray)) and len(data) > 0:
                x_data = list(range(len(data)))
                y_data = list(data)
                series_tag = f"{y_axis_tag}_{name}_bar"
                # Use line series for bars (DearPyGui doesn't have native bar charts)
                dpg.add_stem_series(x_data, y_data, tag=series_tag, parent=y_axis_tag, label=name)

    def AddTable(self, columns: List[str], data: List[List[Any]], **kwargs) -> str:
        """Add table to panel."""
        table_tag = f"{self.panel_tag}_table_{len(self.content_items)}"
        if dpg.does_item_exist(self.panel_tag):
            with dpg.table(tag=table_tag, parent=self.panel_tag, **kwargs):
                # Add columns
                for col in columns:
                    dpg.add_table_column(label=col)

                # Add rows
                for row_data in data:
                    with dpg.table_row():
                        for cell_data in row_data:
                            dpg.add_text(str(cell_data))

        self.content_items.append({"type": "table", "tag": table_tag,
                                 "columns": columns, "data": data})
        return table_tag


class StatusBarWrapper:
    """Status bar management wrapper."""

    def __init__(self, parent_tag: str):
        self.parent_tag = parent_tag
        self.status_bar_tag = f"{parent_tag}_status_bar"
        self.visible = True
        self.status_text = "Ready"
        self.status_items = []

    def SetVisibility(self, visible: bool) -> None:
        """Set status bar visibility."""
        self.visible = visible
        if dpg.does_item_exist(self.status_bar_tag):
            dpg.configure_item(self.status_bar_tag, show=visible)

    def SetText(self, value: str) -> None:
        """Set status text."""
        self.status_text = value
        status_text_tag = f"{self.status_bar_tag}_text"
        if dpg.does_item_exist(status_text_tag):
            dpg.set_value(status_text_tag, value)

    def AddIndicator(self, indicator_type: str, state: Any, **kwargs) -> str:
        """Add indicator to status bar."""
        indicator_tag = f"{self.status_bar_tag}_indicator_{len(self.status_items)}"
        if dpg.does_item_exist(self.status_bar_tag):
            if indicator_type == "progress":
                dpg.add_progress_bar(tag=indicator_tag, parent=self.status_bar_tag,
                                   default_value=float(state), width=150, **kwargs)
        self.status_items.append({"type": "indicator", "tag": indicator_tag,
                                "indicator_type": indicator_type, "state": state})
        return indicator_tag


class MainPanel:
    """Main panel container for sub-panels."""

    def __init__(self, parent_tag: str):
        self.parent_tag = parent_tag
        self.main_panel_tag = f"{parent_tag}_main_panel"
        self.panels = {}
        self.panel_order = []
        self.visible = True

    def AddPanel(self, index: int, title: str, height_ratio: float = 1.0) -> PanelWrapper:
        """Add sub-panel to main panel."""
        panel_tag = f"{self.main_panel_tag}_panel_{index}"

        if dpg.does_item_exist(self.main_panel_tag):
            # Calculate height based on ratio
            available_height = 600  # Default, should be calculated from parent

            # Calculate total ratio - include current panel being added
            total_ratio = sum(p.get("height_ratio", 1) for p in self.panels.values()) + height_ratio
            if total_ratio == 0:  # Safety check to prevent division by zero
                total_ratio = height_ratio

            panel_height = int(available_height * height_ratio / total_ratio)
            panel_height = max(panel_height, 150)  # Minimum height

            dpg.add_child_window(tag=panel_tag, parent=self.main_panel_tag,
                               height=panel_height, border=True, label=title)

        panel_wrapper = PanelWrapper(panel_tag, self.main_panel_tag)
        self.panels[index] = {
            "wrapper": panel_wrapper,
            "title": title,
            "height_ratio": height_ratio,
            "tag": panel_tag
        }

        if index not in self.panel_order:
            self.panel_order.append(index)
            self.panel_order.sort()

        return panel_wrapper

    def RemovePanel(self, index: int) -> None:
        """Remove panel by index."""
        if index in self.panels:
            panel_tag = self.panels[index]["tag"]
            if dpg.does_item_exist(panel_tag):
                dpg.delete_item(panel_tag)
            del self.panels[index]
            if index in self.panel_order:
                self.panel_order.remove(index)

    def ClearPanels(self) -> None:
        """Clear all panels."""
        for index in list(self.panels.keys()):
            self.RemovePanel(index)

    def GetPanel(self, index: int) -> Optional[PanelWrapper]:
        """Get panel wrapper by index."""
        if index in self.panels:
            return self.panels[index]["wrapper"]
        return None

    def SetVisibility(self, visible: bool) -> None:
        """Set main panel visibility."""
        self.visible = visible
        if dpg.does_item_exist(self.main_panel_tag):
            dpg.configure_item(self.main_panel_tag, show=visible)

    def AddText(self, value: str, **kwargs) -> str:
        """Add text directly to main panel."""
        text_tag = f"{self.main_panel_tag}_text_{len([p for p in self.panels.values() if p.get('type') == 'text'])}"
        if dpg.does_item_exist(self.main_panel_tag):
            dpg.add_text(value, tag=text_tag, parent=self.main_panel_tag, **kwargs)
        return text_tag


class DataPlotterDearPyGui2:
    """
    Main root class for financial data visualization framework.

    Features:
    - Modular wrapper-based architecture
    - Dynamic layout management
    - Multi-panel support with synchronized operations
    - Event/callback system
    - Financial chart types (candlestick, line, bar)
    - Table support for trading data
    """

    def __init__(self, figsize: Tuple[int, int] = (1400, 900), title: str = "Financial Data Analyzer"):
        self.figsize = figsize
        self.title = title
        self.context_created = False
        self.window_tag = "root_window"

        # Layout configuration
        self.layout_ratios = {
            "left_panel": 0.2,
            "main_panel": 0.6,
            "right_panel": 0.2,
            "upper_panel": 0.1,
            "bottom_panel": 0.2
        }

        # Initialize wrapper components
        self.menu_wrapper = None
        self.main_panel = None
        self.status_bar_wrapper = None
        self.left_panel = None
        self.right_panel = None
        self.upper_panel = None
        self.bottom_panel = None

        # Component visibility
        self.show_menu = True
        self.show_status_bar = True
        self.show_left_panel = True
        self.show_right_panel = True
        self.show_upper_panel = True
        self.show_bottom_panel = True
        self.show_main_panel = True
        
        # Menu recreation callback
        self.menu_setup_callback = None
        
        # Content restoration callback
        self.content_setup_callback = None

    def Initialize(self) -> None:
        """Initialize the framework and create UI structure."""
        if not DEARPYGUI_AVAILABLE:
            raise RuntimeError("Dear PyGui not available. Install with: pip install dearpygui")

        if not self.context_created:
            dpg.create_context()
            self.context_created = True

        self._create_main_window()
        self._initialize_wrappers()

    def _create_main_window(self) -> None:
        """Create main window with layout structure."""
        with dpg.window(tag=self.window_tag, label=self.title,
                       width=self.figsize[0], height=self.figsize[1],
                       no_close=False):

            # 1. Menu bar (fixed height)
            if self.show_menu:
                with dpg.menu_bar(tag=f"{self.window_tag}_menu_bar"):
                    pass

            # 2. Upper panel (fixed height)
            if self.show_upper_panel:
                dpg.add_child_window(tag=f"{self.window_tag}_upper_panel",
                                   height=int(self.figsize[1] * self.layout_ratios["upper_panel"]),
                                   border=True)

            # 3. Main content area (dynamic height - fills remaining space)
            # Use table layout for proper right-alignment
            with dpg.table(tag=f"{self.window_tag}_main_content", header_row=False,
                          borders_innerH=False, borders_innerV=False, borders_outerH=False, borders_outerV=False):

                # Define columns
                if self.show_left_panel and self.show_right_panel:
                    dpg.add_table_column(init_width_or_weight=self.layout_ratios["left_panel"], width_fixed=False)  # Left
                    dpg.add_table_column(init_width_or_weight=self.layout_ratios["main_panel"], width_fixed=False)  # Main (dynamic)
                    dpg.add_table_column(init_width_or_weight=self.layout_ratios["right_panel"], width_fixed=False)  # Right
                elif self.show_left_panel and not self.show_right_panel:
                    dpg.add_table_column(init_width_or_weight=self.layout_ratios["left_panel"], width_fixed=False)  # Left
                    dpg.add_table_column(init_width_or_weight=1-self.layout_ratios["left_panel"], width_fixed=False)  # Main
                elif not self.show_left_panel and self.show_right_panel:
                    dpg.add_table_column(init_width_or_weight=1-self.layout_ratios["right_panel"], width_fixed=False)  # Main
                    dpg.add_table_column(init_width_or_weight=self.layout_ratios["right_panel"], width_fixed=False)  # Right
                else:
                    dpg.add_table_column(init_width_or_weight=1.0, width_fixed=False)  # Main only

                # Add the row with panels
                with dpg.table_row():
                    # Left panel cell
                    if self.show_left_panel:
                        with dpg.table_cell():
                            dpg.add_child_window(tag=f"{self.window_tag}_left_panel",
                                               width=-1, height=-1, border=True)

                    # Main panel cell (always present, takes remaining space)
                    with dpg.table_cell():
                        dpg.add_child_window(tag=f"{self.window_tag}_main_panel",
                                           width=-1, height=-1, border=True)

                    # Right panel cell
                    if self.show_right_panel:
                        with dpg.table_cell():
                            dpg.add_child_window(tag=f"{self.window_tag}_right_panel",
                                               width=-1, height=-1, border=True)

            # 4. Bottom panel (fixed height)
            if self.show_bottom_panel:
                dpg.add_child_window(tag=f"{self.window_tag}_bottom_panel",
                                   height=int(self.figsize[1] * self.layout_ratios["bottom_panel"]),
                                   border=True)

            # 5. Status bar (fixed height)
            if self.show_status_bar:
                with dpg.child_window(tag=f"{self.window_tag}_status_bar", height=30, border=True):
                    with dpg.group(horizontal=True):
                        dpg.add_text("Ready", tag=f"{self.window_tag}_status_bar_text")

            # Debug output
            print(f"DEBUG: Window size: {self.figsize}")
            print(f"DEBUG: Panel visibility - Left: {self.show_left_panel}, Right: {self.show_right_panel}, Upper: {self.show_upper_panel}, Bottom: {self.show_bottom_panel}")
            print(f"DEBUG: Layout ratios: {self.layout_ratios}")

    def _initialize_wrappers(self) -> None:
        """Initialize all wrapper components."""
        # Menu wrapper
        if self.show_menu:
            self.menu_wrapper = MenuWrapper(self.window_tag)

        # Panel wrappers
        self.main_panel = MainPanel(self.window_tag)

        if self.show_left_panel:
            self.left_panel = PanelWrapper(f"{self.window_tag}_left_panel", self.window_tag)

        if self.show_right_panel:
            self.right_panel = PanelWrapper(f"{self.window_tag}_right_panel", self.window_tag)

        if self.show_upper_panel:
            self.upper_panel = PanelWrapper(f"{self.window_tag}_upper_panel", self.window_tag)

        if self.show_bottom_panel:
            self.bottom_panel = PanelWrapper(f"{self.window_tag}_bottom_panel", self.window_tag)

        # Status bar wrapper
        if self.show_status_bar:
            self.status_bar_wrapper = StatusBarWrapper(self.window_tag)

    def GetMainMenu(self) -> Optional[MenuWrapper]:
        """Get main menu wrapper."""
        return self.menu_wrapper

    def GetMainPanel(self) -> MainPanel:
        """Get main panel container."""
        return self.main_panel

    def GetStatusBar(self) -> Optional[StatusBarWrapper]:
        """Get status bar wrapper."""
        return self.status_bar_wrapper

    def GetLeftPanel(self) -> Optional[PanelWrapper]:
        """Get left panel wrapper."""
        return self.left_panel

    def GetRightPanel(self) -> Optional[PanelWrapper]:
        """Get right panel wrapper."""
        return self.right_panel

    def GetUpperPanel(self) -> Optional[PanelWrapper]:
        """Get upper panel wrapper."""
        return self.upper_panel

    def GetBottomPanel(self) -> Optional[PanelWrapper]:
        """Get bottom panel wrapper."""
        return self.bottom_panel

    def Show(self, interactive: bool = True) -> None:
        """Display the application."""
        if not self.context_created:
            self.Initialize()

        try:
            dpg.create_viewport(title=self.title, width=self.figsize[0], height=self.figsize[1])
            dpg.setup_dearpygui()
            dpg.show_viewport()
            dpg.set_primary_window(self.window_tag, True)
            dpg.start_dearpygui()
        except Exception as e:
            print(f"Error displaying application: {e}")
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self.context_created:
                dpg.destroy_context()
                self.context_created = False
        except:
            pass

    def SetLayoutRatios(self, **ratios) -> None:
        """Set layout ratios for panels."""
        self.layout_ratios.update(ratios)

    def SetPanelVisibility(self, panel_name: str, visible: bool) -> None:
        """Set panel visibility."""
        setattr(self, f"show_{panel_name}", visible)

    def RefreshLayout(self) -> None:
        """Refresh the entire window layout by recreating all panels in correct order."""
        if not dpg.does_item_exist(self.window_tag):
            return
        
        # Store current content before recreating
        self._store_current_content()
            
        # Delete all window content except the window itself
        self._clear_window_content()
        
        # Recreate the entire window layout in correct order
        self._recreate_window_layout()
        
        # Re-initialize all wrappers
        self._reinitialize_all_wrappers()
        
        # Restore content to panels
        self._restore_content()
        
        print(f"Layout refreshed - Upper: {self.show_upper_panel}, Left: {self.show_left_panel}, Main: {self.show_main_panel}, Right: {self.show_right_panel}, Bottom: {self.show_bottom_panel}")

    def _store_current_content(self) -> None:
        """Store current panel content before layout refresh."""
        # This is a placeholder - in a real implementation, you might want to store panel content
        pass

    def _clear_window_content(self) -> None:
        """Clear all content from the main window."""
        # Get all children of the main window and delete them
        if dpg.does_item_exist(self.window_tag):
            children = dpg.get_item_children(self.window_tag, slot=1)  # slot=1 for child items
            if children:
                for child in children:
                    if dpg.does_item_exist(child):
                        dpg.delete_item(child)

    def _recreate_window_layout(self) -> None:
        """Recreate the entire window layout in correct order."""
        # 1. Menu bar (if enabled)
        if self.show_menu:
            with dpg.menu_bar(tag=f"{self.window_tag}_menu_bar", parent=self.window_tag):
                pass

        # 2. Upper panel (if enabled)
        if self.show_upper_panel:
            dpg.add_child_window(tag=f"{self.window_tag}_upper_panel",
                               height=int(self.figsize[1] * self.layout_ratios["upper_panel"]),
                               border=True, parent=self.window_tag)

        # 3. Main content area (Left, Main, Right panels in table layout)
        with dpg.table(tag=f"{self.window_tag}_main_content", header_row=False,
                      borders_innerH=False, borders_innerV=False, 
                      borders_outerH=False, borders_outerV=False, parent=self.window_tag):

            # Define columns based on current panel visibility
            if self.show_left_panel and self.show_main_panel and self.show_right_panel:
                dpg.add_table_column(init_width_or_weight=self.layout_ratios["left_panel"], width_fixed=False)
                dpg.add_table_column(init_width_or_weight=self.layout_ratios["main_panel"], width_fixed=False)
                dpg.add_table_column(init_width_or_weight=self.layout_ratios["right_panel"], width_fixed=False)
            elif self.show_left_panel and self.show_main_panel and not self.show_right_panel:
                dpg.add_table_column(init_width_or_weight=self.layout_ratios["left_panel"], width_fixed=False)
                dpg.add_table_column(init_width_or_weight=1-self.layout_ratios["left_panel"], width_fixed=False)
            elif not self.show_left_panel and self.show_main_panel and self.show_right_panel:
                dpg.add_table_column(init_width_or_weight=1-self.layout_ratios["right_panel"], width_fixed=False)
                dpg.add_table_column(init_width_or_weight=self.layout_ratios["right_panel"], width_fixed=False)
            elif self.show_left_panel and not self.show_main_panel and self.show_right_panel:
                dpg.add_table_column(init_width_or_weight=self.layout_ratios["left_panel"], width_fixed=False)
                dpg.add_table_column(init_width_or_weight=self.layout_ratios["right_panel"], width_fixed=False)
            elif self.show_left_panel and not self.show_main_panel and not self.show_right_panel:
                dpg.add_table_column(init_width_or_weight=1.0, width_fixed=False)
            elif not self.show_left_panel and not self.show_main_panel and self.show_right_panel:
                dpg.add_table_column(init_width_or_weight=1.0, width_fixed=False)
            elif not self.show_left_panel and self.show_main_panel and not self.show_right_panel:
                dpg.add_table_column(init_width_or_weight=1.0, width_fixed=False)
            else:
                # All panels hidden case - show at least something
                dpg.add_table_column(init_width_or_weight=1.0, width_fixed=False)

            # Add the row with panels
            with dpg.table_row():
                # Left panel cell (only if visible)
                if self.show_left_panel:
                    with dpg.table_cell():
                        dpg.add_child_window(tag=f"{self.window_tag}_left_panel",
                                           width=-1, height=-1, border=True)

                # Main panel cell (only if visible)
                if self.show_main_panel:
                    with dpg.table_cell():
                        dpg.add_child_window(tag=f"{self.window_tag}_main_panel",
                                           width=-1, height=-1, border=True)

                # Right panel cell (only if visible)
                if self.show_right_panel:
                    with dpg.table_cell():
                        dpg.add_child_window(tag=f"{self.window_tag}_right_panel",
                                           width=-1, height=-1, border=True)

        # 4. Bottom panel (if enabled)
        if self.show_bottom_panel:
            dpg.add_child_window(tag=f"{self.window_tag}_bottom_panel",
                               height=int(self.figsize[1] * self.layout_ratios["bottom_panel"]),
                               border=True, parent=self.window_tag)

        # 5. Status bar (if enabled)
        if self.show_status_bar:
            with dpg.child_window(tag=f"{self.window_tag}_status_bar", height=30, border=True, parent=self.window_tag):
                with dpg.group(horizontal=True):
                    dpg.add_text("Ready", tag=f"{self.window_tag}_status_bar_text")

    def _reinitialize_all_wrappers(self) -> None:
        """Reinitialize all panel wrappers."""
        # Menu wrapper
        if self.show_menu:
            self.menu_wrapper = MenuWrapper(self.window_tag)
            # Trigger menu recreation callback if available
            self._recreate_menu_items()

        # Panel wrappers - recreate based on visibility
        if self.show_main_panel:
            self.main_panel = MainPanel(self.window_tag)
        else:
            self.main_panel = None

        if self.show_left_panel:
            self.left_panel = PanelWrapper(f"{self.window_tag}_left_panel", self.window_tag)
        else:
            self.left_panel = None

        if self.show_right_panel:
            self.right_panel = PanelWrapper(f"{self.window_tag}_right_panel", self.window_tag)
        else:
            self.right_panel = None

        if self.show_upper_panel:
            self.upper_panel = PanelWrapper(f"{self.window_tag}_upper_panel", self.window_tag)
        else:
            self.upper_panel = None

        if self.show_bottom_panel:
            self.bottom_panel = PanelWrapper(f"{self.window_tag}_bottom_panel", self.window_tag)
        else:
            self.bottom_panel = None

        # Status bar wrapper
        if self.show_status_bar:
            self.status_bar_wrapper = StatusBarWrapper(self.window_tag)
        else:
            self.status_bar_wrapper = None

    def _restore_content(self) -> None:
        """Restore content to panels after layout refresh."""
        if self.content_setup_callback and callable(self.content_setup_callback):
            try:
                self.content_setup_callback()
            except Exception as e:
                print(f"Error restoring panel content: {e}")

    def _recreate_menu_items(self) -> None:
        """Recreate menu items using the callback if available."""
        if self.menu_setup_callback and callable(self.menu_setup_callback):
            try:
                self.menu_setup_callback(self.menu_wrapper)
            except Exception as e:
                print(f"Error recreating menu items: {e}")

    def SetMenuSetupCallback(self, callback) -> None:
        """Set the callback function for recreating menu items."""
        self.menu_setup_callback = callback

    def SetContentSetupCallback(self, callback) -> None:
        """Set the callback function for restoring panel content."""
        self.content_setup_callback = callback