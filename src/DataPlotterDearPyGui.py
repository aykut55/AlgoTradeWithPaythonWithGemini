"""
Data Plotter for algorithmic trading system visualization using Dear PyGui.

This module contains the DataPlotterDearPyGui class which provides comprehensive
data visualization capabilities for OHLCV data, technical indicators, and trading signals
using Dear PyGui for GPU-accelerated rendering.
"""
try:
    import dearpygui.dearpygui as dpg
    DEARPYGUI_AVAILABLE = True
except ImportError:
    DEARPYGUI_AVAILABLE = False
    print("Dear PyGui not available. Install with: pip install dearpygui")

import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import math


class DataPlotterDearPyGui:
    """
    Data visualization class for trading system analysis using Dear PyGui.
    
    Features:
    - Multi-panel plotting with synchronized zoom
    - Technical indicator overlays
    - Trading signal markers
    - GPU-accelerated rendering
    - Interactive crosshair and zoom controls
    - Dark/light theme support
    """
    
    def __init__(self, figsize: Tuple[int, int] = (1200, 800), style: str = 'dark'):
        """
        Initialize the Dear PyGui data plotter.
        
        Args:
            figsize: Window size as (width, height)
            style: Plot style ('dark', 'light', 'classic')
        """
        self.figsize = figsize
        self.style = style
        self.window_tag = None
        self.plots = []
        self.crosshair_lines = {}
        self.synchronized_zoom = True
        self.context_created = False
        self.panel_heights = []
        self.resize_callback_registered = False
        self.header_height = 60
        self.footer_height = 80
        self.status_text = "Ready"
        self.show_header = True
        self.show_footer = True
        self.header_collapsed = False
        self.footer_collapsed = False
        
        # Color schemes
        self.color_schemes = {
            'dark': {
                'bg_color': [30, 30, 30, 255],
                'text_color': [255, 255, 255, 255],
                'grid_color': [80, 80, 80, 255],
                'candle_up': [0, 255, 136, 255],
                'candle_down': [255, 68, 68, 255],
                'volume_color': [102, 102, 102, 255],
                'ma_colors': [
                    [255, 170, 0, 255],    # Orange
                    [0, 170, 255, 255],    # Blue  
                    [255, 0, 170, 255],    # Pink
                    [170, 0, 255, 255]     # Purple
                ],
                'signal_buy': [0, 255, 0, 255],
                'signal_sell': [255, 0, 0, 255],
                'line_colors': [
                    [255, 255, 0, 255],    # Yellow
                    [0, 255, 255, 255],    # Cyan
                    [255, 128, 0, 255],    # Orange
                    [128, 255, 0, 255],    # Light green
                    [255, 0, 128, 255],    # Pink
                    [128, 0, 255, 255],    # Purple
                    [0, 128, 255, 255],    # Light blue
                    [255, 255, 128, 255]   # Light yellow
                ]
            },
            'light': {
                'bg_color': [255, 255, 255, 255],
                'text_color': [0, 0, 0, 255],
                'grid_color': [204, 204, 204, 255],
                'candle_up': [38, 166, 154, 255],
                'candle_down': [239, 83, 80, 255],
                'volume_color': [144, 164, 174, 255],
                'ma_colors': [
                    [255, 152, 0, 255],    # Orange
                    [33, 150, 243, 255],   # Blue
                    [233, 30, 99, 255],    # Pink
                    [156, 39, 176, 255]    # Purple
                ],
                'signal_buy': [76, 175, 80, 255],
                'signal_sell': [244, 67, 54, 255],
                'line_colors': [
                    [255, 193, 7, 255],    # Amber
                    [0, 188, 212, 255],    # Cyan
                    [255, 87, 34, 255],    # Deep orange
                    [139, 195, 74, 255],   # Light green
                    [233, 30, 99, 255],    # Pink
                    [103, 58, 183, 255],   # Deep purple
                    [3, 169, 244, 255],    # Light blue
                    [255, 235, 59, 255]    # Yellow
                ]
            }
        }
        
        # Get color scheme or default to dark
        self.colors = self.color_schemes.get(style, self.color_schemes['dark'])
        
        # Store data for plotting
        self.timestamps = None
        self.panels_data = []
        
    def _normalize_color(self, color):
        """Convert color to normalized RGBA format for Dear PyGui."""
        if isinstance(color, list) and len(color) >= 3:
            if all(c <= 1.0 for c in color[:3]):
                # Already normalized
                return color[:4] if len(color) >= 4 else color + [1.0]
            else:
                # Convert from 0-255 to 0-1
                normalized = [c/255.0 for c in color[:3]]
                if len(color) >= 4:
                    normalized.append(color[3]/255.0 if color[3] > 1.0 else color[3])
                else:
                    normalized.append(1.0)
                return normalized
        return [1.0, 1.0, 1.0, 1.0]  # Default white
    
    def _create_window(self):
        """Create the main window for plotting."""
        if self.window_tag is not None:
            try:
                dpg.delete_item(self.window_tag)
            except:
                pass
        
        self.window_tag = "main_plot_window"
        
        with dpg.window(tag=self.window_tag, label="Trading Analysis", 
                       width=self.figsize[0], height=self.figsize[1],
                       no_close=False):
            # Create header if enabled
            if self.show_header:
                self._create_header()
            
            # Create content area (plots will be added here)
            dpg.add_child_window(tag="content_area", height=-self.footer_height if self.show_footer else -1)
            
            # Create footer if enabled
            if self.show_footer:
                self._create_footer()
    
    def _setup_crosshair(self, plot_tag):
        """Setup crosshair functionality for a plot."""
        def crosshair_callback(sender, app_data, user_data):
            # Get mouse position in plot coordinates
            mouse_x, mouse_y = dpg.get_plot_mouse_pos()
            plot_tag = user_data
            
            # Remove existing crosshair lines
            if plot_tag in self.crosshair_lines:
                for line_tag in self.crosshair_lines[plot_tag]:
                    try:
                        dpg.delete_item(line_tag)
                    except:
                        pass
                self.crosshair_lines[plot_tag] = []
            else:
                self.crosshair_lines[plot_tag] = []
            
            if mouse_x is not None and mouse_y is not None:
                # Add vertical line
                vline_tag = f"{plot_tag}_crosshair_v"
                hline_tag = f"{plot_tag}_crosshair_h"
                
                try:
                    # Get plot limits to draw full crosshair
                    x_min = dpg.get_axis_limits("x_axis")[0] 
                    x_max = dpg.get_axis_limits("x_axis")[1]
                    y_min = dpg.get_axis_limits("y_axis")[0]
                    y_max = dpg.get_axis_limits("y_axis")[1]
                    
                    # Vertical line
                    dpg.add_line_series([mouse_x, mouse_x], [y_min, y_max], 
                                       tag=vline_tag, parent=plot_tag)
                    dpg.set_item_theme(vline_tag, "crosshair_theme")
                    
                    # Horizontal line  
                    dpg.add_line_series([x_min, x_max], [mouse_y, mouse_y],
                                       tag=hline_tag, parent=plot_tag)
                    dpg.set_item_theme(hline_tag, "crosshair_theme")
                    
                    self.crosshair_lines[plot_tag] = [vline_tag, hline_tag]
                except:
                    pass
        
        # Register mouse move callback
        with dpg.item_handler_registry(tag=f"{plot_tag}_handler"):
            dpg.add_item_hover_handler(callback=crosshair_callback, user_data=plot_tag)
        
        dpg.bind_item_handler_registry(plot_tag, f"{plot_tag}_handler")
    
    def _create_themes(self):
        """Create themes for different UI elements."""
        # Crosshair theme
        with dpg.theme(tag="crosshair_theme"):
            with dpg.theme_component(dpg.mvLineSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, [128, 128, 128, 128])
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 1)
    
    def plot_multi_panel(self,
                        timestamps: np.ndarray,
                        panels: List[Dict[str, Any]],
                        synchronized_zoom: bool = True,
                        figsize: Optional[Tuple[int, int]] = None) -> None:
        """
        Plot multi-panel chart with N panels and synchronized zoom functionality.
        
        Args:
            timestamps: Unix timestamps or index array
            panels: List of panel configs, each panel should have:
                   - 'series_data': Dict of series name -> data
                   - 'title': Panel title
                   - 'height_ratio': Optional height ratio (default: 1)
                   - 'yon_list': Optional direction list for support/resistance
                   - 'seviye_list': Optional level list for support/resistance
            synchronized_zoom: Enable synchronized zoom between panels
            figsize: Figure size override
        """
        if not panels:
            raise ValueError("At least one panel must be provided")
        
        # Check if Dear PyGui is available
        if not DEARPYGUI_AVAILABLE:
            print("Dear PyGui not available. Please install with: pip install dearpygui")
            return
        
        try:
            # Create context if not exists
            if not self.context_created:
                dpg.create_context()
                self.context_created = True
            
            # Store data
            self.timestamps = timestamps
            self.panels_data = panels
            self.synchronized_zoom = synchronized_zoom
            
            # Update figsize if provided
            if figsize:
                self.figsize = figsize
            
            # Create themes
            self._create_themes()
            
            # Create main window
            self._create_window()
            
            # Calculate heights based on ratios
            total_ratio = sum(panel.get('height_ratio', 1) for panel in panels)
            available_height = self.figsize[1] - 100  # Leave space for window decorations
            
            self.panel_heights = []
            for panel in panels:
                ratio = panel.get('height_ratio', 1)
                height = int((ratio / total_ratio) * available_height)
                self.panel_heights.append(max(height, 150))  # Minimum height
            
            # Clear existing plots
            self.plots.clear()
            
            # Create plots for each panel directly in the main window
            for i, (panel, height) in enumerate(zip(panels, self.panel_heights)):
                plot_tag = f"plot_{i}"
                x_axis_tag = f"x_axis_{i}"
                y_axis_tag = f"y_axis_{i}"
                
                panel_title = panel.get('title', f'Panel {i}')
                
                # Create plot as child of the content area
                dpg.add_plot(tag=plot_tag, label=panel_title, 
                           height=height, width=-1, parent="content_area")
                
                # Add axes to the plot
                dpg.add_plot_axis(dpg.mvXAxis, tag=x_axis_tag, label="Time", parent=plot_tag)
                dpg.add_plot_axis(dpg.mvYAxis, tag=y_axis_tag, label="Value", parent=plot_tag)
                
                # Plot series data
                self._plot_panel_data(panel, plot_tag, x_axis_tag, y_axis_tag, i)
                
                # Setup synchronized zoom/pan callback
                if self.synchronized_zoom:
                    self._setup_sync_callback(plot_tag, x_axis_tag, i)
                
                # Setup crosshair (simplified to avoid crashes)
                # self._setup_crosshair(plot_tag)
                
                self.plots.append({
                    'plot_tag': plot_tag,
                    'x_axis_tag': x_axis_tag, 
                    'y_axis_tag': y_axis_tag,
                    'panel_data': panel
                })
            
            # Setup resize callback for this window
            self._setup_resize_callback()
            
            # Update header info after creating plots
            self.update_header_info()
            
            print(f"Multi-panel chart created with {len(panels)} panels using Dear PyGui")
            if synchronized_zoom:
                print("- Synchronized zoom enabled")
            print("- Interactive crosshair enabled")
            print("- Dynamic panel resizing enabled")
            print("- Header/Footer UI enabled")
            
        except Exception as e:
            print(f"Error creating Dear PyGui chart: {e}")
            print("Please check your Dear PyGui installation and data")
    
    def _plot_panel_data(self, panel, plot_tag, x_axis_tag, y_axis_tag, panel_index):
        """Plot data for a single panel."""
        panel_data = panel.get('series_data', {})
        
        # Convert timestamps to x-axis data
        if self.timestamps is not None:
            if len(self.timestamps) > 0 and isinstance(self.timestamps[0], (int, float)):
                # Check if timestamps look like unix timestamps
                if self.timestamps[0] > 1000000000:  # Rough check for unix timestamp
                    try:
                        # Try to use as index for now - Dear PyGui works better with simple indices
                        x_data = list(range(len(self.timestamps)))
                    except:
                        x_data = list(range(len(self.timestamps)))
                else:
                    x_data = list(self.timestamps)
            else:
                x_data = list(range(len(self.timestamps)))
        else:
            # Determine max length from series data
            max_length = 0
            for name, data in panel_data.items():
                if isinstance(data, (np.ndarray, list)) and len(data) > 0:
                    max_length = max(max_length, len(data))
            x_data = list(range(max_length))
        
        # Color index for automatic coloring
        color_index = 0
        
        # Plot each series
        for name, data in panel_data.items():
            try:
                if isinstance(data, dict):
                    # Advanced configuration
                    plot_data = data.get('data', [])
                    color = data.get('color', self.colors['line_colors'][color_index % len(self.colors['line_colors'])])
                    
                    if isinstance(plot_data, (int, float)):
                        # Horizontal line
                        self._add_horizontal_line(plot_data, name, color, y_axis_tag)
                    elif isinstance(plot_data, (np.ndarray, list)) and len(plot_data) > 0:
                        # Series data
                        self._add_line_series(x_data, plot_data, name, color, y_axis_tag)
                
                elif isinstance(data, (int, float)):
                    # Single value - horizontal level
                    color = self.colors['line_colors'][color_index % len(self.colors['line_colors'])]
                    self._add_horizontal_line(data, name, color, y_axis_tag)
                
                elif isinstance(data, (np.ndarray, list)) and len(data) > 0:
                    # Array data - line plot
                    color = self.colors['line_colors'][color_index % len(self.colors['line_colors'])]
                    self._add_line_series(x_data, data, name, color, y_axis_tag)
                
                color_index += 1
                
            except Exception as e:
                print(f"Warning: Could not plot panel {panel_index} series '{name}': {e}")
                continue
        
        # Plot direction-based support/resistance lines
        yon_list = panel.get('yon_list', None)
        seviye_list = panel.get('seviye_list', None)
        
        if yon_list is not None and seviye_list is not None:
            try:
                self._plot_direction_levels(x_data, yon_list, seviye_list, y_axis_tag)
                print(f"Panel {panel_index}: Direction levels plotted")
            except Exception as e:
                print(f"Warning: Could not plot direction levels for panel {panel_index}: {e}")
    
    def _add_line_series(self, x_data, y_data, name, color, y_axis_tag):
        """Add a line series to the plot."""
        # Ensure data lengths match
        min_length = min(len(x_data), len(y_data))
        x_plot = x_data[:min_length]
        y_plot = y_data[:min_length] if hasattr(y_data, '__getitem__') else [y_data] * min_length
        
        # Handle NaN values
        if isinstance(y_plot, np.ndarray):
            valid_mask = ~np.isnan(y_plot)
            if not np.any(valid_mask):
                return  # All NaN values
            x_plot = [x_plot[i] for i in range(len(valid_mask)) if valid_mask[i]]
            y_plot = y_plot[valid_mask].tolist()
        
        # Convert to lists if needed
        if not isinstance(x_plot, list):
            x_plot = list(x_plot)
        if not isinstance(y_plot, list):
            y_plot = list(y_plot)
        
        # Add line series
        series_tag = f"{y_axis_tag}_{name}"
        normalized_color = self._normalize_color(color)
        
        dpg.add_line_series(x_plot, y_plot, tag=series_tag, parent=y_axis_tag, label=name)
        
        # Create theme for this series
        theme_tag = f"{series_tag}_theme"
        with dpg.theme(tag=theme_tag):
            with dpg.theme_component(dpg.mvLineSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, 
                                   [int(c*255) for c in normalized_color])
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2)
        
        dpg.set_item_theme(series_tag, theme_tag)
    
    def _add_horizontal_line(self, y_value, name, color, y_axis_tag):
        """Add a horizontal line to the plot."""
        # Create a horizontal line across the plot
        # We'll use a large x range that will be clipped to the actual plot area
        x_range = [-1000000, 1000000]  # Large range
        y_range = [y_value, y_value]
        
        series_tag = f"{y_axis_tag}_{name}_hline"
        normalized_color = self._normalize_color(color)
        
        dpg.add_line_series(x_range, y_range, tag=series_tag, parent=y_axis_tag, label=name)
        
        # Create theme for this series
        theme_tag = f"{series_tag}_theme"
        with dpg.theme(tag=theme_tag):
            with dpg.theme_component(dpg.mvLineSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, 
                                   [int(c*255) for c in normalized_color])
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2)
        
        dpg.set_item_theme(series_tag, theme_tag)
    
    def _plot_direction_levels(self, x_data, yon_list, seviye_list, y_axis_tag):
        """
        Plot dynamic support/resistance lines based on direction and level lists.
        
        Args:
            x_data: X-axis data (index-based)
            yon_list: Direction list ('A', 'S', 'F')
            seviye_list: Level list (price levels)
            y_axis_tag: Y-axis tag for the plot
        """
        if not yon_list or not seviye_list or len(yon_list) != len(seviye_list):
            return
        
        # Find all signal changes
        signal_changes = []
        current_signal = None
        
        for i, direction in enumerate(yon_list):
            if direction != current_signal and direction in ['A', 'S']:
                signal_changes.append({
                    'index': i,
                    'direction': direction,
                    'level': seviye_list[i],
                    'x_pos': x_data[i] if i < len(x_data) else x_data[-1]
                })
                current_signal = direction
            elif direction == 'F':
                current_signal = None
        
        # Draw lines between signal changes
        for i, signal in enumerate(signal_changes):
            # Find the end point (next signal or end of data)
            if i + 1 < len(signal_changes):
                x_end = signal_changes[i + 1]['x_pos']
                end_index = signal_changes[i + 1]['index']
            else:
                x_end = x_data[-1] if x_data else signal['x_pos']
                end_index = len(x_data) - 1
            
            # Only draw if line has meaningful length
            if abs(end_index - signal['index']) > 1:
                if signal['direction'] == 'A':  # Long position
                    line_y = signal['level'] * 0.999
                    color = self._normalize_color(self.colors['candle_up'])
                elif signal['direction'] == 'S':  # Short position
                    line_y = signal['level'] * 1.001
                    color = self._normalize_color(self.colors['candle_down'])
                
                # Create line series for support/resistance
                x_line = [signal['x_pos'], x_end]
                y_line = [line_y, line_y]
                
                series_tag = f"direction_line_{i}_{signal['direction']}"
                dpg.add_line_series(x_line, y_line, tag=series_tag, parent=y_axis_tag)
                
                # Set line style
                theme_tag = f"{series_tag}_theme"
                with dpg.theme(tag=theme_tag):
                    with dpg.theme_component(dpg.mvLineSeries):
                        dpg.add_theme_color(dpg.mvPlotCol_Line, 
                                           [int(c*255) for c in color[:3]] + [160])  # Semi-transparent
                        dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2)
                
                dpg.set_item_theme(series_tag, theme_tag)
    
    def _setup_resize_callback(self):
        """Setup window resize callback to dynamically adjust panel heights."""
        if self.resize_callback_registered or not self.window_tag:
            return
            
        try:
            def window_resize_callback(sender, app_data, user_data):
                """Callback function for window resize events."""
                try:
                    # Get new window size
                    new_width = dpg.get_item_width(self.window_tag)
                    new_height = dpg.get_item_height(self.window_tag)
                    
                    if new_height > 100:  # Minimum reasonable height
                        self._update_panel_heights(new_height)
                except Exception as e:
                    print(f"Resize callback error: {e}")
            
            # Register resize handler for the window
            with dpg.item_handler_registry(tag=f"{self.window_tag}_resize_handler"):
                dpg.add_item_resize_handler(callback=window_resize_callback)
            
            dpg.bind_item_handler_registry(self.window_tag, f"{self.window_tag}_resize_handler")
            self.resize_callback_registered = True
            
        except Exception as e:
            print(f"Warning: Could not setup resize callback: {e}")
    
    def _update_panel_heights(self, new_window_height):
        """Update panel heights based on new window size."""
        if not self.plots or not self.panels_data:
            return
            
        try:
            # Calculate new heights based on ratios
            total_ratio = sum(panel.get('height_ratio', 1) for panel in self.panels_data)
            available_height = new_window_height - 100  # Leave space for decorations
            
            # Update stored panel heights
            self.panel_heights = []
            for panel in self.panels_data:
                ratio = panel.get('height_ratio', 1)
                height = int((ratio / total_ratio) * available_height)
                self.panel_heights.append(max(height, 150))  # Minimum height
            
            # Apply new heights to existing plots
            for i, plot_info in enumerate(self.plots):
                if i < len(self.panel_heights):
                    plot_tag = plot_info['plot_tag']
                    new_height = self.panel_heights[i]
                    
                    try:
                        dpg.configure_item(plot_tag, height=new_height)
                    except:
                        pass  # Ignore if plot no longer exists
                        
        except Exception as e:
            print(f"Warning: Could not update panel heights: {e}")
    
    def _setup_sync_callback(self, plot_tag, x_axis_tag, panel_index):
        """Setup synchronized zoom and pan callback for a plot."""
        if not self.synchronized_zoom:
            return
            
        try:
            def sync_callback(sender, app_data, user_data):
                """Callback function for synchronized zoom/pan operations."""
                try:
                    # Skip if sync is disabled
                    if not self.synchronized_zoom:
                        return
                    
                    # Get current x-axis limits from the changed plot
                    current_limits = dpg.get_axis_limits(x_axis_tag)
                    if current_limits is None or len(current_limits) != 2:
                        return
                    
                    x_min, x_max = current_limits
                    
                    # Apply the same x-axis limits to all other plots
                    for plot_info in self.plots:
                        other_x_axis_tag = plot_info['x_axis_tag']
                        # Skip the current plot that triggered the callback
                        if other_x_axis_tag != x_axis_tag:
                            try:
                                dpg.set_axis_limits(other_x_axis_tag, x_min, x_max)
                            except:
                                pass  # Ignore if axis doesn't exist
                    
                    # Update status to show synchronization is active
                    self.update_status(f"Synchronized zoom: {x_min:.2f} - {x_max:.2f}")
                    
                except Exception as e:
                    pass  # Silently ignore sync errors to prevent crash loops
            
            # Register callback for zoom and pan events on the plot
            with dpg.item_handler_registry(tag=f"{plot_tag}_sync_handler"):
                dpg.add_item_clicked_handler(callback=sync_callback, button=dpg.mvMouseButton_Left)
                dpg.add_item_hover_handler(callback=sync_callback)
            
            dpg.bind_item_handler_registry(plot_tag, f"{plot_tag}_sync_handler")
            
        except Exception as e:
            print(f"Warning: Could not setup sync callback for panel {panel_index}: {e}")
    
    def _create_header(self):
        """Create header with menu, buttons, and labels."""
        # Calculate dynamic height based on collapsed state
        current_height = 25 if self.header_collapsed else self.header_height
        
        with dpg.child_window(tag="header_area", height=current_height, border=True):
            # Collapsible header title bar
            with dpg.group(horizontal=True):
                collapse_icon = "▼" if not self.header_collapsed else "▶"
                dpg.add_button(label=f"{collapse_icon} Header", tag="header_collapse_btn", callback=self._toggle_header_collapse, width=80)
                dpg.add_separator()
                dpg.add_text("Trading Controls & Status")
            
            # Only show content if not collapsed
            if not self.header_collapsed:
                # Header top row - Menu bar
                with dpg.menu_bar():
                    with dpg.menu(label="File"):
                        dpg.add_menu_item(label="Open Data", callback=self._on_open_data)
                        dpg.add_menu_item(label="Save Chart", callback=self._on_save_chart)
                        dpg.add_separator()
                        dpg.add_menu_item(label="Export PNG", callback=self._on_export_png)
                        dpg.add_menu_item(label="Export CSV", callback=self._on_export_csv)
                
                    with dpg.menu(label="View"):
                        dpg.add_menu_item(label="Reset Zoom", callback=self._on_reset_zoom)
                        dpg.add_menu_item(label="Fit to Window", callback=self._on_fit_window)
                        dpg.add_separator()
                        dpg.add_checkbox(label="Show Crosshair", default_value=True, callback=self._on_toggle_crosshair)
                        dpg.add_checkbox(label="Synchronized Zoom", default_value=self.synchronized_zoom, callback=self._on_toggle_sync_zoom, tag="sync_zoom_checkbox")
                
                    with dpg.menu(label="Tools"):
                        dpg.add_menu_item(label="Analysis Tools", callback=self._on_analysis_tools)
                        dpg.add_menu_item(label="Indicator Panel", callback=self._on_indicator_panel)
                        dpg.add_separator()
                        dpg.add_menu_item(label="Settings", callback=self._on_settings)
            
                # Header bottom row - Control buttons and info
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Refresh", tag="btn_refresh", callback=self._on_refresh)
                    dpg.add_button(label="Pause", tag="btn_pause", callback=self._on_pause)
                    dpg.add_separator()
                    
                    # Theme selector
                    dpg.add_text("Theme:")
                    dpg.add_combo(["dark", "light"], default_value=self.style, tag="theme_combo", 
                                 callback=self._on_theme_change, width=80)
                    
                    dpg.add_separator()
                    
                    # Status indicators
                    dpg.add_text("Panels:")
                    dpg.add_text("0", tag="panel_count")
                    
                    dpg.add_separator()
                    dpg.add_text("Mode:")
                    dpg.add_text("Real-time", tag="mode_status")
                    
                    # Spacer to push time to the right
                    dpg.add_spacer(width=50)
                    
                    # Current time display
                    dpg.add_text("Time:")
                    dpg.add_text(datetime.now().strftime("%H:%M:%S"), tag="current_time")
    
    def _create_footer(self):
        """Create footer with status bar."""
        # Calculate dynamic height based on collapsed state
        current_height = 25 if self.footer_collapsed else self.footer_height
        
        with dpg.child_window(tag="footer_area", height=current_height, border=True):
            # Collapsible footer title bar
            with dpg.group(horizontal=True):
                collapse_icon = "▲" if not self.footer_collapsed else "▼"
                dpg.add_button(label=f"{collapse_icon} Footer", tag="footer_collapse_btn", callback=self._toggle_footer_collapse, width=80)
                dpg.add_separator()
                dpg.add_text("Status & Statistics")
            
            # Only show content if not collapsed
            if not self.footer_collapsed:
                with dpg.group(horizontal=True):
                    # Status text
                    dpg.add_text(self.status_text, tag="status_text")
                    
                    # Spacer to push other elements to the right
                    dpg.add_spacer(width=200)
                    
                    # Progress bar for operations
                    dpg.add_progress_bar(tag="progress_bar", width=150, default_value=0.0, overlay="Ready")
                    
                    # Separator
                    dpg.add_separator()
                    
                    # Chart info
                    dpg.add_text("Charts: 0", tag="chart_count")
                    dpg.add_text(" | ")
                    dpg.add_text("Points: 0", tag="point_count")
                    dpg.add_text(" | ")
                    dpg.add_text("FPS: --", tag="fps_counter")
    
    # Header callback methods
    def _on_open_data(self):
        """Handle open data menu item."""
        self.update_status("Opening data file...")
        print("Open data file dialog would appear here")
    
    def _on_save_chart(self):
        """Handle save chart menu item."""
        self.update_status("Saving chart...")
        print("Save chart dialog would appear here")
    
    def _on_export_png(self):
        """Handle export PNG menu item."""
        self.update_status("Exporting to PNG...")
        print("Export PNG functionality")
    
    def _on_export_csv(self):
        """Handle export CSV menu item."""
        self.update_status("Exporting to CSV...")
        print("Export CSV functionality")
    
    def _on_reset_zoom(self):
        """Handle reset zoom menu item."""
        self.update_status("Resetting zoom...")
        for plot_info in self.plots:
            try:
                dpg.fit_axis_data(plot_info['x_axis_tag'])
                dpg.fit_axis_data(plot_info['y_axis_tag'])
            except:
                pass
    
    def _on_fit_window(self):
        """Handle fit to window menu item."""
        self.update_status("Fitting to window...")
        self._on_reset_zoom()
    
    def _on_toggle_crosshair(self, sender, app_data):
        """Handle toggle crosshair checkbox."""
        if app_data:
            self.update_status("Crosshair enabled")
        else:
            self.update_status("Crosshair disabled")
    
    def _on_toggle_sync_zoom(self, sender, app_data):
        """Handle toggle synchronized zoom checkbox."""
        self.synchronized_zoom = app_data
        if app_data:
            self.update_status("Synchronized zoom enabled")
        else:
            self.update_status("Synchronized zoom disabled")
    
    def _on_analysis_tools(self):
        """Handle analysis tools menu item."""
        self.update_status("Opening analysis tools...")
        print("Analysis tools panel would open here")
    
    def _on_indicator_panel(self):
        """Handle indicator panel menu item."""
        self.update_status("Opening indicator panel...")
        print("Indicator panel would open here")
    
    def _on_settings(self):
        """Handle settings menu item."""
        self.update_status("Opening settings...")
        print("Settings dialog would open here")
    
    def _on_refresh(self):
        """Handle refresh button."""
        self.update_status("Refreshing data...")
        print("Refreshing chart data")
    
    def _on_pause(self):
        """Handle pause button."""
        current_text = dpg.get_item_label("btn_pause")
        if current_text == "Pause":
            dpg.set_item_label("btn_pause", "Resume")
            self.update_status("Paused")
        else:
            dpg.set_item_label("btn_pause", "Pause")
            self.update_status("Resumed")
    
    def _on_theme_change(self, sender, app_data):
        """Handle theme change combo."""
        self.style = app_data
        self.colors = self.color_schemes.get(app_data, self.color_schemes['dark'])
        self.update_status(f"Theme changed to {app_data}")
    
    def _toggle_header_collapse(self):
        """Toggle header collapse state."""
        self.header_collapsed = not self.header_collapsed
        
        # Update header area height
        new_height = 25 if self.header_collapsed else self.header_height
        try:
            dpg.configure_item("header_area", height=new_height)
            
            # Update button label with new icon
            collapse_icon = "▼" if not self.header_collapsed else "▶"
            if dpg.does_item_exist("header_collapse_btn"):
                dpg.set_item_label("header_collapse_btn", f"{collapse_icon} Header")
            
            status = "collapsed" if self.header_collapsed else "expanded"
            self.update_status(f"Header {status}")
            
        except Exception as e:
            print(f"Error toggling header: {e}")
    
    def _toggle_footer_collapse(self):
        """Toggle footer collapse state."""
        self.footer_collapsed = not self.footer_collapsed
        
        # Update footer area height
        new_height = 25 if self.footer_collapsed else self.footer_height
        try:
            dpg.configure_item("footer_area", height=new_height)
            
            # Update button label with new icon
            collapse_icon = "▲" if not self.footer_collapsed else "▼"
            if dpg.does_item_exist("footer_collapse_btn"):
                dpg.set_item_label("footer_collapse_btn", f"{collapse_icon} Footer")
            
            status = "collapsed" if self.footer_collapsed else "expanded"
            self.update_status(f"Footer {status}")
            
        except Exception as e:
            print(f"Error toggling footer: {e}")
    
    def update_status(self, message: str):
        """Update status bar message."""
        self.status_text = message
        try:
            dpg.set_value("status_text", message)
        except:
            pass
    
    def update_header_info(self):
        """Update header information displays."""
        try:
            # Update panel count
            dpg.set_value("panel_count", str(len(self.plots)))
            
            # Update current time
            dpg.set_value("current_time", datetime.now().strftime("%H:%M:%S"))
            
            # Update chart count in footer
            dpg.set_value("chart_count", f"Charts: {len(self.plots)}")
            
            # Update point count if data is available
            total_points = 0
            if self.panels_data:
                for panel in self.panels_data:
                    series_data = panel.get('series_data', {})
                    for name, data in series_data.items():
                        if isinstance(data, (list, np.ndarray)):
                            total_points += len(data)
            
            dpg.set_value("point_count", f"Points: {total_points}")
            
        except Exception as e:
            pass  # Ignore errors if UI elements don't exist yet
    
    def show(self, interactive: bool = True) -> None:
        """
        Display the chart.
        
        Args:
            interactive: Enable interactive features (always True for Dear PyGui)
        """
        if self.window_tag is None:
            raise ValueError("No chart created. Call plot_multi_panel() first.")
        
        try:
            # Create context if not exists
            if not self.context_created:
                dpg.create_context()
                self.context_created = True
            
            # Setup Dear PyGui viewport
            dpg.create_viewport(title="Trading Analysis", width=self.figsize[0], height=self.figsize[1])
            dpg.setup_dearpygui()
            dpg.show_viewport()
            dpg.set_primary_window(self.window_tag, True)
            
            print("Dear PyGui interactive features:")
            print("- Mouse wheel: Zoom in/out")
            print("- Mouse drag: Pan around the chart")
            print("- Right-click: Context menu")
            print("- Mouse hover: Interactive crosshair")
            
            # Start Dear PyGui
            dpg.start_dearpygui()
            
        except Exception as e:
            print(f"Error displaying chart with Dear PyGui: {e}")
            print("Please check your Dear PyGui installation and data")
        
        finally:
            # Clean up
            try:
                if self.context_created:
                    dpg.destroy_context()
                    self.context_created = False
            except:
                pass
    
    def close(self) -> None:
        """Close the current chart."""
        if self.window_tag is not None:
            try:
                dpg.delete_item(self.window_tag)
            except:
                pass
            self.window_tag = None
            self.plots.clear()
    
    def save_chart(self, filename: str) -> None:
        """
        Save the chart to file (placeholder - Dear PyGui doesn't have built-in save).
        
        Args:
            filename: Output filename
        """
        print(f"Chart save to {filename} not implemented for Dear PyGui version")
        print("Use screenshot functionality or export data instead")
    
    def _fallback_to_matplotlib(self) -> None:
        """
        Fallback to matplotlib when Dear PyGui fails.
        """
        try:
            # Import DataPlotter as fallback
            from src.DataPlotter import DataPlotter
            fallback_plotter = DataPlotter(figsize=(self.figsize[0]/100, self.figsize[1]/100), style=self.style)
            
            if self.timestamps is not None and self.panels_data:
                print("Using matplotlib fallback...")
                fallback_plotter.plot_multi_panel(
                    timestamps=self.timestamps,
                    panels=self.panels_data,
                    synchronized_zoom=self.synchronized_zoom,
                    figsize=(self.figsize[0]/100, self.figsize[1]/100)
                )
                fallback_plotter.show()
            else:
                print("Fallback: No data available to plot")
        except Exception as e:
            print(f"Fallback to matplotlib also failed: {e}")
            print("Please check your plotting dependencies")
    
    # Compatibility methods to match DataPlotter interface
    def plot_series(self, 
                   timestamps: Optional[np.ndarray] = None,
                   series_data: Optional[Dict[str, Any]] = None,
                   title: str = "Series Plot",
                   xlabel: str = "Time",
                   ylabel: str = "Value",
                   figsize: Optional[Tuple[int, int]] = None) -> None:
        """
        Plot multiple series - compatibility method that converts to multi_panel format.
        """
        if series_data is None:
            series_data = {}
        
        # Convert to multi-panel format
        panels = [{
            'series_data': series_data,
            'title': title,
            'height_ratio': 1
        }]
        
        self.plot_multi_panel(
            timestamps=timestamps or np.array([]),
            panels=panels,
            figsize=figsize
        )
    
    def create_subplots(self, rows: int = 2, height_ratios: Optional[List[float]] = None) -> None:
        """Compatibility method - not needed for Dear PyGui implementation."""
        pass
    
    def plot_candlestick(self, *args, **kwargs) -> None:
        """Compatibility method - candlestick plotting not implemented in this version."""
        print("Candlestick plotting not implemented in Dear PyGui version")
    
    def plot_volume(self, *args, **kwargs) -> None:
        """Compatibility method - volume plotting not implemented in this version.""" 
        print("Volume plotting not implemented in Dear PyGui version")
    
    def plot_indicators(self, *args, **kwargs) -> None:
        """Compatibility method - use series_data in plot_multi_panel instead."""
        print("Use series_data parameter in plot_multi_panel for indicators")
    
    def plot_signals(self, *args, **kwargs) -> None:
        """Compatibility method - signal plotting not implemented in this version."""
        print("Signal plotting not implemented in Dear PyGui version")
    
    def plot_rsi(self, *args, **kwargs) -> None:
        """Compatibility method - RSI plotting not implemented in this version."""
        print("RSI plotting not implemented in Dear PyGui version")
    
    def create_comprehensive_chart(self, *args, **kwargs) -> None:
        """Compatibility method - use plot_multi_panel instead."""
        print("Use plot_multi_panel method for comprehensive charts")
    
    def __repr__(self) -> str:
        """String representation of the plotter."""
        plot_count = len(self.plots)
        return f"DataPlotterDearPyGui(style='{self.style}', plots={plot_count}, figsize={self.figsize})"