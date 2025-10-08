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
        self.separator_counter = 0  # Counter for unique separator tags

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
            
            # Handle separators with unique tags
            if label == "---" or label.startswith("---"):
                self.separator_counter += 1
                item_tag = f"{parent_tag}_separator_{self.separator_counter}"
                label_key = f"---_{self.separator_counter}"  # Unique key for storage
            else:
                item_tag = f"{parent_tag}_{label.replace(' ', '_')}"  # Replace spaces for better tags
                label_key = label
            
            if dpg.does_item_exist(parent_tag):
                dpg.add_menu_item(label=label, tag=item_tag, parent=parent_tag, callback=callback)
            self.menu_items[parent]["children"][label_key] = {"tag": item_tag, "callback": callback}
            return item_tag
        return ""


class PanelWrapper:
    """Panel management wrapper for all types of panels."""

    def __init__(self, panel_tag: str, parent_tag: str = ""):
        self.panel_tag = panel_tag
        self.parent_tag = parent_tag
        self.visible = True
        self.content_items = []
        self.trader_data = None
        self.x_data = None
        self.y_data = {}
        self.title = ""
        self.height_ratio = 1
        self.legend_text = None

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
            # Get panel dimensions for dynamic sizing
            panel_width = dpg.get_item_width(self.panel_tag)
            panel_height = dpg.get_item_height(self.panel_tag)
            
            # Use panel dimensions if available, otherwise use defaults/options
            if panel_width > 0:
                width = panel_width - 20  # Leave some margin
            else:
                width = options.get("width", -1)
                
            if panel_height > 0:
                height = panel_height - 40  # Leave margin for title and padding
            else:
                height = options.get("height", 300)

            dpg.add_plot(tag=plot_tag, parent=self.panel_tag, height=height, width=width,
                        label=options.get("title", "Plot"), no_title=True,
                        callback=self._on_plot_interaction)
            
            # Add plot legend to enable click interaction
            dpg.add_plot_legend(parent=plot_tag)

            x_axis_tag = f"{plot_tag}_x_axis"
            y_axis_tag = f"{plot_tag}_y_axis"

            dpg.add_plot_axis(dpg.mvXAxis, tag=x_axis_tag, parent=plot_tag, label="Time")
            dpg.add_plot_axis(dpg.mvYAxis, tag=y_axis_tag, parent=plot_tag, label="Value")

            # Store axis info in plot for callback access
            self._store_plot_axis_info(plot_tag, x_axis_tag, y_axis_tag)

            # Register axes with MainPanel for synchronization
            self._register_axes_with_main_panel(x_axis_tag, y_axis_tag)

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
        elif plot_type == "combined":
            self._add_combined_series(series_data, x_axis_tag, y_axis_tag, options)

    def _add_candlestick_series(self, series_data: Dict[str, Any],
                               x_axis_tag: str, y_axis_tag: str, options: Dict[str, Any]) -> None:
        """Add candlestick series (OHLC)."""
        timestamps = series_data.get("timestamps", [])
        open_data = series_data.get("open", [])
        high_data = series_data.get("high", [])
        low_data = series_data.get("low", [])
        close_data = series_data.get("close", [])

        # Check if all data exists and has length > 0
        if (timestamps is not None and len(timestamps) > 0 and 
            open_data is not None and len(open_data) > 0 and 
            high_data is not None and len(high_data) > 0 and 
            low_data is not None and len(low_data) > 0 and 
            close_data is not None and len(close_data) > 0):
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

    def _add_combined_series(self, series_data: Dict[str, Any],
                           x_axis_tag: str, y_axis_tag: str, options: Dict[str, Any]) -> None:
        """Add combined OHLC and line series to the same plot."""
        # First, add OHLC data if available
        ohlc_keys = ["timestamps", "open", "high", "low", "close"]
        has_ohlc = all(key in series_data for key in ohlc_keys)
        
        if has_ohlc:
            # Extract OHLC data
            ohlc_data = {key: series_data[key] for key in ohlc_keys}
            # Add candlestick series with legend
            self._add_candlestick_series_with_legend(ohlc_data, x_axis_tag, y_axis_tag, options)
        
        # Add line data (indicators, MA, etc.)
        line_data = {}
        for name, data in series_data.items():
            # Skip OHLC data keys and only process line data
            if name not in ohlc_keys and isinstance(data, (list, np.ndarray)) and len(data) > 0:
                line_data[name] = data
        
        if line_data:
            # Add line series for indicators
            self._add_line_series(line_data, x_axis_tag, y_axis_tag, options)
    
    def _add_candlestick_series_with_legend(self, series_data: Dict[str, Any],
                                          x_axis_tag: str, y_axis_tag: str, options: Dict[str, Any]) -> None:
        """Add candlestick series with legend support."""
        timestamps = series_data.get("timestamps", [])
        open_data = series_data.get("open", [])
        high_data = series_data.get("high", [])
        low_data = series_data.get("low", [])
        close_data = series_data.get("close", [])

        # Check if all data exists and has length > 0
        if (timestamps is not None and len(timestamps) > 0 and 
            open_data is not None and len(open_data) > 0 and 
            high_data is not None and len(high_data) > 0 and 
            low_data is not None and len(low_data) > 0 and 
            close_data is not None and len(close_data) > 0):
            
            x_data = list(range(len(timestamps)))
            
            # Use legend text if available, otherwise use default
            legend_label = self.legend_text if self.legend_text else "OHLC"
            
            # Store candlestick series tags for toggling
            candlestick_tags = []
            
            # Create candlestick using multiple series
            for i in range(len(x_data)):
                if i < len(open_data) and i < len(high_data) and i < len(low_data) and i < len(close_data):
                    o, h, l, c = open_data[i], high_data[i], low_data[i], close_data[i]
                    color = [0, 255, 0, 255] if c >= o else [255, 0, 0, 255]

                    # High-Low line
                    hl_tag = f"{y_axis_tag}_hl_{i}"
                    dpg.add_line_series([x_data[i], x_data[i]], [l, h],
                                       parent=y_axis_tag, tag=hl_tag)
                    candlestick_tags.append(hl_tag)

                    # Body rectangle (simulated with thick line)
                    body_top = max(o, c)
                    body_bottom = min(o, c)
                    if body_top != body_bottom:
                        body_tag = f"{y_axis_tag}_body_{i}"
                        dpg.add_line_series([x_data[i], x_data[i]], [body_bottom, body_top],
                                           parent=y_axis_tag, tag=body_tag)
                        candlestick_tags.append(body_tag)
            
            # Create a representative line for OHLC legend (use Close data)
            ohlc_legend_tag = f"{y_axis_tag}_ohlc_legend"
            dpg.add_line_series(x_data, list(close_data), tag=ohlc_legend_tag, 
                              parent=y_axis_tag, label=legend_label)
            
            # Make the legend line invisible by default (only for legend display)
            dpg.configure_item(ohlc_legend_tag, show=False)
            
            # Store candlestick tags for potential future toggle functionality
            # Note: DearPyGui doesn't support callbacks on line series
            # Future: Could add button controls or keyboard shortcuts for toggling

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

    def SetPriceData(self, trader) -> 'PanelWrapper':
        """Set price data for the panel (trader with OHLC data)."""
        self.trader_data = trader
        return self

    def _setup_price_chart_content2(self, chart_type_name: str) -> None:
        """Setup price chart content based on chart type."""
        print(f"DEBUG: _setup_price_chart_content2 called with chart_type: {chart_type_name}")
        # This method should be implemented to handle different chart types
        # For now, it's a placeholder
        pass

    def AddXData(self, timestamps) -> None:
        """Add X-axis data (timestamps) to the panel."""
        self.x_data = timestamps
        try:
            if timestamps is not None and hasattr(timestamps, '__len__'):
                print(f"DEBUG: AddXData called with {len(timestamps)} timestamps")
            else:
                print("DEBUG: AddXData called with None or invalid timestamps")
        except Exception as e:
            print(f"DEBUG: AddXData called but error getting length: {e}")

    def AddYData(self, data, label: str) -> None:
        """Add Y-axis data with label to the panel."""
        if data is not None:
            self.y_data[label] = data
            # print(f"DEBUG: AddYData called - {label}: {len(data) if hasattr(data, '__len__') else 'scalar'} points")

    def SetTitle(self, title: str) -> None:
        """Set panel title."""
        self.title = title
        print(f"DEBUG: SetTitle called with title: {title}")

    def SetHeightRatio(self, ratio: float) -> None:
        """Set panel height ratio."""
        self.height_ratio = ratio
        print(f"DEBUG: SetHeightRatio called with ratio: {ratio}")

    def SetLegend(self, legend_text: str) -> None:
        """Set legend text for the panel."""
        self.legend_text = legend_text
        print(f"DEBUG: SetLegend called with text: {legend_text}")

    def PlotSignals(self) -> None:
        """Plot trading signals on the panel."""
        print("DEBUG: PlotSignals called")
        # Create plots based on collected data
        self._create_plots()

    def _create_plots(self) -> None:
        """Create actual plots from the collected data with control buttons."""
        try:
            # Prepare combined data for single plot
            combined_data = {}
            
            # Add OHLC data if trader data is available
            if self.trader_data and hasattr(self.trader_data, 'Open'):
                # Safe timestamp handling for numpy arrays
                if self.x_data is not None and hasattr(self.x_data, '__len__') and len(self.x_data) > 0:
                    combined_data["timestamps"] = self.x_data
                else:
                    combined_data["timestamps"] = list(range(len(self.trader_data.Close)))
                    
                combined_data["open"] = list(self.trader_data.Open) if hasattr(self.trader_data.Open, '__iter__') else [self.trader_data.Open] * len(self.trader_data.Close)
                combined_data["high"] = list(self.trader_data.High) if hasattr(self.trader_data.High, '__iter__') else [self.trader_data.High] * len(self.trader_data.Close)
                combined_data["low"] = list(self.trader_data.Low) if hasattr(self.trader_data.Low, '__iter__') else [self.trader_data.Low] * len(self.trader_data.Close)
                combined_data["close"] = list(self.trader_data.Close)

            # Add line data (indicators) to the same data structure
            if self.y_data:
                for label, data in self.y_data.items():
                    if data is not None and hasattr(data, '__len__') and len(data) > 0:
                        combined_data[label] = list(data)

            # Create layout with buttons and plot side by side
            if combined_data and dpg.does_item_exist(self.panel_tag):
                # Create horizontal group for buttons + plot
                horizontal_group = dpg.add_group(horizontal=True, parent=self.panel_tag)
                
                # Left side: Control buttons
                self._create_control_buttons(horizontal_group)
                
                # Right side: Plot
                self._create_plot_with_data(combined_data, horizontal_group)

            print(f"DEBUG: _create_plots completed for panel: {self.title}")
            
        except Exception as e:
            print(f"DEBUG: Error in _create_plots: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_control_buttons(self, parent_group) -> None:
        """Create control buttons for zoom and pan operations."""
        button_width = 80
        
        with dpg.group(parent=parent_group):
            # Sync buttons
            dpg.add_text("Sync Controls:")
            dpg.add_button(label="ButtonZoom", width=button_width,
                          callback=self._on_button_sync_zoom,
                          user_data={"panel_id": id(self)})
            dpg.add_button(label="ButtonPan", width=button_width,
                          callback=self._on_button_sync_pan,
                          user_data={"panel_id": id(self)})
            
            dpg.add_separator()
            
            # X-axis controls
            dpg.add_text("X-Axis Controls:")
            dpg.add_button(label="X Zoom+", width=button_width,
                          callback=self._on_x_zoom_plus,
                          user_data={"panel_id": id(self)})
            dpg.add_button(label="X Zoom-", width=button_width,
                          callback=self._on_x_zoom_minus,
                          user_data={"panel_id": id(self)})
            
            dpg.add_separator()
            
            # Y-axis controls
            dpg.add_text("Y-Axis Controls:")
            dpg.add_button(label="Y Zoom+", width=button_width,
                          callback=self._on_y_zoom_plus,
                          user_data={"panel_id": id(self)})
            dpg.add_button(label="Y Zoom-", width=button_width,
                          callback=self._on_y_zoom_minus,
                          user_data={"panel_id": id(self)})

    def _create_plot_with_data(self, combined_data: Dict[str, Any], horizontal_group) -> None:
        """Create the actual plot with the provided data."""
        plot_tag = f"{self.panel_tag}_plot_{len(self.content_items)}"
        options = {"title": f"{self.title} - Trading Chart", "height": 400}
        
        if dpg.does_item_exist(self.panel_tag):
            # Get panel dimensions for dynamic sizing
            panel_width = dpg.get_item_width(self.panel_tag)
            panel_height = dpg.get_item_height(self.panel_tag)
            
            # Adjust width to account for buttons (reduce by button area)
            if panel_width > 0:
                width = max(panel_width - 120, 400)  # Leave space for buttons
            else:
                width = options.get("width", 600)
                
            if panel_height > 0:
                height = panel_height - 40  # Leave margin for title and padding
            else:
                height = options.get("height", 300)

            dpg.add_plot(tag=plot_tag, parent=horizontal_group, height=height, width=width,
                        label=options.get("title", "Plot"), no_title=True,
                        callback=self._on_plot_interaction)
            
            # Add plot legend to enable click interaction
            dpg.add_plot_legend(parent=plot_tag)

            x_axis_tag = f"{plot_tag}_x_axis"
            y_axis_tag = f"{plot_tag}_y_axis"

            dpg.add_plot_axis(dpg.mvXAxis, tag=x_axis_tag, parent=plot_tag, label="Time")
            dpg.add_plot_axis(dpg.mvYAxis, tag=y_axis_tag, parent=plot_tag, label="Value")

            # Store axis info in plot for callback access
            self._store_plot_axis_info(plot_tag, x_axis_tag, y_axis_tag)

            # Register axes with MainPanel for synchronization
            self._register_axes_with_main_panel(x_axis_tag, y_axis_tag)

            self._add_series_to_plot("combined", combined_data, x_axis_tag, y_axis_tag, options)

        self.content_items.append({"type": "plot", "tag": plot_tag, "plot_type": "combined",
                                 "series_data": combined_data, "options": options})

    def _register_axes_with_main_panel(self, x_axis_tag: str, y_axis_tag: str) -> None:
        """Register plot axes with the MainPanel for synchronization."""
        try:
            # Find the MainPanel by looking at parent hierarchy
            # This is a bit of a hack, but necessary to link PanelWrapper to MainPanel
            main_panel_tag = self.parent_tag  # This should be the main_panel_tag from MainPanel
            
            # We need access to the main DataPlotterDearPyGui2 instance
            # For now, we'll use a simple approach - store axes info locally and 
            # let MainPanel discover them when needed
            if not hasattr(self, '_plot_axes'):
                self._plot_axes = {"x_axes": [], "y_axes": []}
                
            if x_axis_tag not in self._plot_axes["x_axes"]:
                self._plot_axes["x_axes"].append(x_axis_tag)
            if y_axis_tag not in self._plot_axes["y_axes"]:
                self._plot_axes["y_axes"].append(y_axis_tag)
                
            print(f"DEBUG: PanelWrapper registered axes - X: {x_axis_tag}, Y: {y_axis_tag}")
            
            # Try to find and register with MainPanel if possible
            # This is a temporary solution - in real usage, you would pass the MainPanel reference
            
        except Exception as e:
            print(f"DEBUG: Error registering axes: {e}")

    def _store_plot_axis_info(self, plot_tag: str, x_axis_tag: str, y_axis_tag: str) -> None:
        """Store plot axis information for callback access."""
        if not hasattr(self, '_plot_axis_info'):
            self._plot_axis_info = {}
        self._plot_axis_info[plot_tag] = {
            'x_axis': x_axis_tag,
            'y_axis': y_axis_tag
        }
        print(f"DEBUG: Stored axis info for plot {plot_tag}")

    def _on_plot_interaction(self, sender, app_data, user_data) -> None:
        """Handle plot interaction events (mouse zoom/pan)."""
        try:
            plot_tag = sender
            if hasattr(self, '_plot_axis_info') and plot_tag in self._plot_axis_info:
                axis_info = self._plot_axis_info[plot_tag]
                x_axis_tag = axis_info['x_axis']
                y_axis_tag = axis_info['y_axis']
                
                print(f"DEBUG: Plot interaction detected on {plot_tag}")
                print(f"DEBUG: Axes - X: {x_axis_tag}, Y: {y_axis_tag}")
                
                # Try to find and trigger MainPanel synchronization
                # This is a simplified approach - in real usage you'd need better coupling
                self._trigger_sync_from_main_panel(x_axis_tag, y_axis_tag)
                
        except Exception as e:
            print(f"DEBUG: Error in plot interaction callback: {e}")

    def _trigger_sync_from_main_panel(self, source_x_axis: str, source_y_axis: str) -> None:
        """Try to trigger synchronization from MainPanel."""
        try:
            # This is a workaround - we need to find a way to access MainPanel
            # For now, we'll use a global approach or signal system
            if hasattr(self, '_main_panel_ref'):
                main_panel = self._main_panel_ref
                if main_panel and hasattr(main_panel, 'SyncAxesLimits'):
                    main_panel.SyncAxesLimits(source_x_axis, source_y_axis)
                    print(f"DEBUG: Triggered sync from MainPanel")
            else:
                print("DEBUG: No MainPanel reference found for synchronization")
        except Exception as e:
            print(f"DEBUG: Error triggering sync: {e}")

    def SetMainPanelRef(self, main_panel) -> None:
        """Set reference to MainPanel for synchronization."""
        self._main_panel_ref = main_panel
        print("DEBUG: MainPanel reference set for synchronization")

    # Button callback functions
    def _on_button_sync_zoom(self, sender, app_data, user_data) -> None:
        """ButtonZoom: Apply this panel's zoom level to all other charts."""
        try:
            print("ButtonZoom pressed - syncing zoom to other charts")
            
            # Get current panel's plot axis info
            current_plot_axis = self._get_current_plot_axis()
            if current_plot_axis and self._main_panel_ref:
                x_axis_tag = current_plot_axis['x_axis']
                y_axis_tag = current_plot_axis['y_axis']
                
                # Get current zoom limits
                if dpg.does_item_exist(x_axis_tag):
                    x_min, x_max = dpg.get_axis_limits(x_axis_tag)
                    
                    # Apply to all other charts via MainPanel
                    main_panel = self._main_panel_ref
                    main_panel.CollectAllPlotAxes()
                    
                    # Apply current zoom to all other axes
                    for other_x_axis in main_panel.plot_axes["x_axes"]:
                        if other_x_axis != x_axis_tag and dpg.does_item_exist(other_x_axis):
                            dpg.set_axis_limits(other_x_axis, x_min, x_max)
                    
                    print(f"Applied zoom level ({x_min:.2f}, {x_max:.2f}) to all charts")
                    
        except Exception as e:
            print(f"Error in ButtonZoom: {e}")

    def _on_button_sync_pan(self, sender, app_data, user_data) -> None:
        """ButtonPan: Apply this panel's pan level to all other charts."""
        try:
            print("ButtonPan pressed - syncing pan to other charts")
            
            # Get current panel's plot axis info
            current_plot_axis = self._get_current_plot_axis()
            if current_plot_axis and self._main_panel_ref:
                x_axis_tag = current_plot_axis['x_axis']
                y_axis_tag = current_plot_axis['y_axis']
                
                # Get current pan limits
                if dpg.does_item_exist(x_axis_tag):
                    x_min, x_max = dpg.get_axis_limits(x_axis_tag)
                    
                    # Apply to all other charts via MainPanel
                    main_panel = self._main_panel_ref
                    main_panel.CollectAllPlotAxes()
                    
                    # Apply current pan to all other axes
                    for other_x_axis in main_panel.plot_axes["x_axes"]:
                        if other_x_axis != x_axis_tag and dpg.does_item_exist(other_x_axis):
                            dpg.set_axis_limits(other_x_axis, x_min, x_max)
                    
                    print(f"Applied pan level ({x_min:.2f}, {x_max:.2f}) to all charts")
                    
        except Exception as e:
            print(f"Error in ButtonPan: {e}")

    def _on_x_zoom_plus(self, sender, app_data, user_data) -> None:
        """X Zoom+: Zoom in on X-axis of this chart."""
        try:
            print("X Zoom+ pressed")
            current_plot_axis = self._get_current_plot_axis()
            if current_plot_axis:
                x_axis_tag = current_plot_axis['x_axis']
                if dpg.does_item_exist(x_axis_tag):
                    x_min, x_max = dpg.get_axis_limits(x_axis_tag)
                    x_range = x_max - x_min
                    new_range = x_range / 1.5  # Zoom in
                    center = (x_min + x_max) / 2
                    new_x_min = center - new_range / 2
                    new_x_max = center + new_range / 2
                    dpg.set_axis_limits(x_axis_tag, new_x_min, new_x_max)
                    print(f"X-axis zoomed in: ({new_x_min:.2f}, {new_x_max:.2f})")
        except Exception as e:
            print(f"Error in X Zoom+: {e}")

    def _on_x_zoom_minus(self, sender, app_data, user_data) -> None:
        """X Zoom-: Zoom out on X-axis of this chart."""
        try:
            print("X Zoom- pressed")
            current_plot_axis = self._get_current_plot_axis()
            if current_plot_axis:
                x_axis_tag = current_plot_axis['x_axis']
                if dpg.does_item_exist(x_axis_tag):
                    x_min, x_max = dpg.get_axis_limits(x_axis_tag)
                    x_range = x_max - x_min
                    new_range = x_range * 1.5  # Zoom out
                    center = (x_min + x_max) / 2
                    new_x_min = center - new_range / 2
                    new_x_max = center + new_range / 2
                    dpg.set_axis_limits(x_axis_tag, new_x_min, new_x_max)
                    print(f"X-axis zoomed out: ({new_x_min:.2f}, {new_x_max:.2f})")
        except Exception as e:
            print(f"Error in X Zoom-: {e}")

    def _on_y_zoom_plus(self, sender, app_data, user_data) -> None:
        """Y Zoom+: Zoom in on Y-axis of this chart."""
        try:
            print("Y Zoom+ pressed")
            current_plot_axis = self._get_current_plot_axis()
            if current_plot_axis:
                y_axis_tag = current_plot_axis['y_axis']
                if dpg.does_item_exist(y_axis_tag):
                    y_min, y_max = dpg.get_axis_limits(y_axis_tag)
                    y_range = y_max - y_min
                    new_range = y_range / 1.5  # Zoom in
                    center = (y_min + y_max) / 2
                    new_y_min = center - new_range / 2
                    new_y_max = center + new_range / 2
                    dpg.set_axis_limits(y_axis_tag, new_y_min, new_y_max)
                    print(f"Y-axis zoomed in: ({new_y_min:.2f}, {new_y_max:.2f})")
        except Exception as e:
            print(f"Error in Y Zoom+: {e}")

    def _on_y_zoom_minus(self, sender, app_data, user_data) -> None:
        """Y Zoom-: Zoom out on Y-axis of this chart."""
        try:
            print("Y Zoom- pressed")
            current_plot_axis = self._get_current_plot_axis()
            if current_plot_axis:
                y_axis_tag = current_plot_axis['y_axis']
                if dpg.does_item_exist(y_axis_tag):
                    y_min, y_max = dpg.get_axis_limits(y_axis_tag)
                    y_range = y_max - y_min
                    new_range = y_range * 1.5  # Zoom out
                    center = (y_min + y_max) / 2
                    new_y_min = center - new_range / 2
                    new_y_max = center + new_range / 2
                    dpg.set_axis_limits(y_axis_tag, new_y_min, new_y_max)
                    print(f"Y-axis zoomed out: ({new_y_min:.2f}, {new_y_max:.2f})")
        except Exception as e:
            print(f"Error in Y Zoom-: {e}")

    def _get_current_plot_axis(self):
        """Get the current plot's axis information."""
        if hasattr(self, '_plot_axis_info') and self._plot_axis_info:
            # Return the first (and likely only) plot's axis info
            for plot_tag, axis_info in self._plot_axis_info.items():
                return axis_info
        return None


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
        
        # Synchronized zoom and pan system
        self.sync_enabled = True
        self.plot_axes = {"x_axes": [], "y_axes": []}
        self._updating_axes = False  # Prevent recursive updates

    def AddPanel(self, index: int, title: str, height_ratio: float = 1.0) -> PanelWrapper:
        """Add sub-panel to main panel."""
        panel_tag = f"{self.main_panel_tag}_panel_{index}"

        # First add panel to data structure  
        panel_wrapper = PanelWrapper(panel_tag, self.main_panel_tag)
        
        # Set MainPanel reference in wrapper for synchronization
        panel_wrapper.SetMainPanelRef(self)
        
        self.panels[index] = {
            "wrapper": panel_wrapper,
            "title": title,
            "height_ratio": height_ratio,
            "tag": panel_tag
        }

        if index not in self.panel_order:
            self.panel_order.append(index)
            self.panel_order.sort()

        # Now create/resize all panels with equal heights
        if dpg.does_item_exist(self.main_panel_tag):
            self._resize_all_panels_equal()

        return panel_wrapper
    
    def _resize_all_panels_equal(self) -> None:
        """Resize all panels to equal heights while preserving content."""
        if not dpg.does_item_exist(self.main_panel_tag):
            return
            
        if len(self.panels) == 0:
            return
            
        # Calculate equal height for all panels
        available_height = 2000  # Increased height for bigger panels
        equal_height = int(available_height / len(self.panels))
        equal_height = max(equal_height, 200)  # Increased minimum height
        
        # Store content for each panel before deletion
        stored_contents = {}
        for index in self.panel_order:
            if index in self.panels:
                panel_info = self.panels[index]
                wrapper = panel_info["wrapper"]
                if wrapper and hasattr(wrapper, 'content_items'):
                    stored_contents[index] = wrapper.content_items.copy()
        
        # Delete and recreate all panels with equal sizes
        for index in self.panel_order:
            if index in self.panels:
                panel_info = self.panels[index]
                panel_tag = panel_info["tag"]
                title = panel_info["title"]
                
                # Delete existing panel if it exists
                if dpg.does_item_exist(panel_tag):
                    dpg.delete_item(panel_tag)
                
                # Recreate with equal height
                dpg.add_child_window(tag=panel_tag, parent=self.main_panel_tag,
                                   height=equal_height, border=True, label=title)
                
                # Restore content items
                wrapper = panel_info["wrapper"]
                if index in stored_contents and wrapper:
                    wrapper.content_items = stored_contents[index]
                    self._recreate_panel_content(wrapper)
                
        print(f"DEBUG: Created {len(self.panels)} panels with equal height: {equal_height}px")

    def _recreate_panel_content(self, wrapper: 'PanelWrapper') -> None:
        """Recreate content items in a panel wrapper after resize."""
        if not wrapper or not hasattr(wrapper, 'content_items'):
            return
            
        for item in wrapper.content_items:
            try:
                item_type = item.get("type")
                if item_type == "plot":
                    # Recreate plot with stored data
                    plot_type = item.get("plot_type")
                    series_data = item.get("series_data")
                    options = item.get("options", {})
                    if plot_type and series_data:
                        # Clear the old content_items entry to avoid duplication
                        temp_items = wrapper.content_items
                        wrapper.content_items = []
                        wrapper.AddPlot(plot_type, series_data, options)
                        # Restore other items
                        wrapper.content_items.extend([i for i in temp_items if i != item])
                elif item_type == "text":
                    # Recreate text
                    value = item.get("value", "")
                    if not dpg.does_item_exist(item.get("tag", "")):
                        wrapper.AddText(value)
                elif item_type == "button":
                    # Recreate button
                    label = item.get("label", "Button")
                    if not dpg.does_item_exist(item.get("tag", "")):
                        wrapper.AddButton(label)
            except Exception as e:
                print(f"DEBUG: Error recreating content item {item_type}: {e}")

    def RemovePanel(self, index: int) -> None:
        """Remove panel by index and resize remaining panels equally."""
        if index in self.panels:
            panel_tag = self.panels[index]["tag"]
            if dpg.does_item_exist(panel_tag):
                dpg.delete_item(panel_tag)
            del self.panels[index]
            if index in self.panel_order:
                self.panel_order.remove(index)
            
            # Resize remaining panels to equal heights
            self._resize_all_panels_equal()

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
        """Set main panel visibility and all child panels."""
        self.visible = visible
        if dpg.does_item_exist(self.main_panel_tag):
            dpg.configure_item(self.main_panel_tag, show=visible)
        
        # Also set visibility for all child panels
        for panel_info in self.panels.values():
            panel_wrapper = panel_info["wrapper"]
            panel_tag = panel_info["tag"]
            
            # Update wrapper visibility state
            panel_wrapper.visible = visible
            
            # Update actual panel visibility
            if dpg.does_item_exist(panel_tag):
                dpg.configure_item(panel_tag, show=visible)

    def AddText(self, value: str, **kwargs) -> str:
        """Add text directly to main panel."""
        text_tag = f"{self.main_panel_tag}_text_{len([p for p in self.panels.values() if p.get('type') == 'text'])}"
        if dpg.does_item_exist(self.main_panel_tag):
            dpg.add_text(value, tag=text_tag, parent=self.main_panel_tag, **kwargs)
        return text_tag

    def RegisterPlotAxes(self, x_axis_tag: str, y_axis_tag: str) -> None:
        """Register plot axes for synchronized operations."""
        if x_axis_tag not in self.plot_axes["x_axes"]:
            self.plot_axes["x_axes"].append(x_axis_tag)
        if y_axis_tag not in self.plot_axes["y_axes"]:
            self.plot_axes["y_axes"].append(y_axis_tag)
        print(f"DEBUG: Registered axes - X: {x_axis_tag}, Y: {y_axis_tag}")

    def SetSyncZoom(self, enabled: bool) -> None:
        """Enable or disable synchronized zoom."""
        self.sync_enabled = enabled
        print(f"DEBUG: Sync zoom {'enabled' if enabled else 'disabled'}")

    def SyncAxesLimits(self, source_x_axis: str, source_y_axis: str = None) -> None:
        """Synchronize all axes limits to match source axis."""
        if not self.sync_enabled or self._updating_axes:
            return
            
        self._updating_axes = True
        try:
            # Get source axis limits
            if dpg.does_item_exist(source_x_axis):
                x_min, x_max = dpg.get_axis_limits(source_x_axis)
                
                # Apply to all other X axes
                for x_axis in self.plot_axes["x_axes"]:
                    if x_axis != source_x_axis and dpg.does_item_exist(x_axis):
                        dpg.set_axis_limits(x_axis, x_min, x_max)
                        
            if source_y_axis and dpg.does_item_exist(source_y_axis):
                y_min, y_max = dpg.get_axis_limits(source_y_axis)
                
                # Apply to all other Y axes
                for y_axis in self.plot_axes["y_axes"]:
                    if y_axis != source_y_axis and dpg.does_item_exist(y_axis):
                        dpg.set_axis_limits(y_axis, y_min, y_max)
                        
            print(f"DEBUG: Synchronized axes limits from {source_x_axis}")
        finally:
            self._updating_axes = False

    def ZoomAll(self, zoom_factor: float = 1.5, center_x: float = None) -> None:
        """Zoom all registered axes synchronously."""
        if not self.sync_enabled:
            return
            
        for x_axis in self.plot_axes["x_axes"]:
            if dpg.does_item_exist(x_axis):
                x_min, x_max = dpg.get_axis_limits(x_axis)
                x_range = x_max - x_min
                new_range = x_range / zoom_factor
                
                if center_x is None:
                    center_x = (x_min + x_max) / 2
                    
                new_x_min = center_x - new_range / 2
                new_x_max = center_x + new_range / 2
                dpg.set_axis_limits(x_axis, new_x_min, new_x_max)
                
        print(f"DEBUG: Zoom applied to all axes with factor: {zoom_factor}")

    def ZoomOut(self, zoom_factor: float = 0.7) -> None:
        """Zoom out on all registered axes."""
        self.ZoomAll(zoom_factor)

    def PanAll(self, dx: float, dy: float = 0) -> None:
        """Pan all registered axes synchronously."""
        if not self.sync_enabled:
            return
            
        for x_axis in self.plot_axes["x_axes"]:
            if dpg.does_item_exist(x_axis):
                x_min, x_max = dpg.get_axis_limits(x_axis)
                dpg.set_axis_limits(x_axis, x_min + dx, x_max + dx)
                
        if dy != 0:
            for y_axis in self.plot_axes["y_axes"]:
                if dpg.does_item_exist(y_axis):
                    y_min, y_max = dpg.get_axis_limits(y_axis)
                    dpg.set_axis_limits(y_axis, y_min + dy, y_max + dy)
                    
        print(f"DEBUG: Pan applied to all axes - dx: {dx}, dy: {dy}")

    def ResetZoom(self) -> None:
        """Reset zoom on all registered axes."""
        if not self.sync_enabled:
            return
            
        for x_axis in self.plot_axes["x_axes"]:
            if dpg.does_item_exist(x_axis):
                dpg.fit_axis_data(x_axis)
                
        for y_axis in self.plot_axes["y_axes"]:
            if dpg.does_item_exist(y_axis):
                dpg.fit_axis_data(y_axis)
                
        print("DEBUG: Reset zoom on all axes")

    def CollectAllPlotAxes(self) -> None:
        """Collect all plot axes from all panels automatically."""
        self.plot_axes = {"x_axes": [], "y_axes": []}
        
        for panel_info in self.panels.values():
            wrapper = panel_info["wrapper"]
            if wrapper and hasattr(wrapper, 'content_items'):
                for item in wrapper.content_items:
                    if item.get("type") == "plot":
                        plot_tag = item.get("tag")
                        if plot_tag and dpg.does_item_exist(plot_tag):
                            # Find all axes in this plot
                            x_axis_tag = f"{plot_tag}_x_axis"
                            y_axis_tag = f"{plot_tag}_y_axis"
                            
                            if dpg.does_item_exist(x_axis_tag) and x_axis_tag not in self.plot_axes["x_axes"]:
                                self.plot_axes["x_axes"].append(x_axis_tag)
                            if dpg.does_item_exist(y_axis_tag) and y_axis_tag not in self.plot_axes["y_axes"]:
                                self.plot_axes["y_axes"].append(y_axis_tag)
        
        print(f"DEBUG: Collected {len(self.plot_axes['x_axes'])} X axes and {len(self.plot_axes['y_axes'])} Y axes")
        
    def ZoomAllWithCollection(self, zoom_factor: float = 1.5, center_x: float = None) -> None:
        """Zoom all axes after collecting them automatically."""
        self.CollectAllPlotAxes()  # First collect all axes
        self.ZoomAll(zoom_factor, center_x)
        
    def ZoomOutWithCollection(self, zoom_factor: float = 0.7) -> None:
        """Zoom out all axes after collecting them automatically."""
        self.CollectAllPlotAxes()  # First collect all axes
        self.ZoomOut(zoom_factor)
        
    def PanAllWithCollection(self, dx: float, dy: float = 0) -> None:
        """Pan all axes after collecting them automatically."""
        self.CollectAllPlotAxes()  # First collect all axes
        self.PanAll(dx, dy)
        
    def ResetZoomWithCollection(self) -> None:
        """Reset zoom on all axes after collecting them automatically."""
        self.CollectAllPlotAxes()  # First collect all axes
        self.ResetZoom()


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

        # Component visibility - Default: only menu and main panel visible
        self.show_menu = True
        self.show_status_bar = False
        self.show_left_panel = False
        self.show_right_panel = False
        self.show_upper_panel = False
        self.show_bottom_panel = False
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

    def ResetZoomWithCollection(self) -> None:
        """Reset zoom on all charts by delegating to main panel."""
        try:
            if self.main_panel and hasattr(self.main_panel, 'ResetZoomWithCollection'):
                self.main_panel.ResetZoomWithCollection()
                print("Reset zoom completed on all charts via main panel")
            else:
                print("Main panel not available or doesn't support ResetZoomWithCollection")
        except Exception as e:
            print(f"Error in ResetZoomWithCollection: {e}")

    def SetLayoutRatios(self, **ratios) -> None:
        """Set layout ratios for panels."""
        self.layout_ratios.update(ratios)

    def SetPanelVisibility(self, panel_name: str, visible: bool) -> None:
        """Set panel visibility."""
        setattr(self, f"show_{panel_name}", visible)
        
        # For main_panel, don't do layout refresh - just toggle visibility
        if panel_name == "main_panel":
            if self.main_panel:
                self.main_panel.SetVisibility(visible)
            return
        
        # For other panels, do layout refresh
        self.RefreshLayout()

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
        # Store MainPanel state and content
        if self.main_panel and hasattr(self.main_panel, 'panels'):
            self.stored_main_panel_state = {
                'panels': self.main_panel.panels.copy(),
                'panel_order': self.main_panel.panel_order.copy(),
                'visible': self.main_panel.visible
            }
            print(f"DEBUG: Stored {len(self.main_panel.panels)} panels before layout refresh")
        else:
            self.stored_main_panel_state = None

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
            # Recreate MainPanel
            self.main_panel = MainPanel(self.window_tag)
            
            # Restore from stored state if available
            if hasattr(self, 'stored_main_panel_state') and self.stored_main_panel_state:
                stored_state = self.stored_main_panel_state
                self.main_panel.panels = stored_state['panels'].copy()
                self.main_panel.panel_order = stored_state['panel_order'].copy()
                self.main_panel.visible = stored_state['visible']
                
                # Recreate the actual DearPyGui panel windows
                for index, panel_info in self.main_panel.panels.items():
                    panel_tag = panel_info["tag"]
                    title = panel_info["title"]
                    height_ratio = panel_info["height_ratio"]
                    
                    # Recreate the DearPyGui child window
                    if dpg.does_item_exist(self.main_panel.main_panel_tag):
                        available_height = 600  # Should match original calculation
                        total_ratio = sum(p.get("height_ratio", 1) for p in self.main_panel.panels.values())
                        if total_ratio == 0:
                            total_ratio = height_ratio
                        panel_height = int(available_height * height_ratio / total_ratio)
                        panel_height = max(panel_height, 150)
                        
                        dpg.add_child_window(tag=panel_tag, parent=self.main_panel.main_panel_tag,
                                           height=panel_height, border=True, label=title)
                
                print(f"DEBUG: Restored {len(self.main_panel.panels)} panels to MainPanel with DearPyGui windows")
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