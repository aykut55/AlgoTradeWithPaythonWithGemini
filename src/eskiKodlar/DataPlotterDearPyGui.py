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
        self.status_text = "Ready"
        self.show_header = True
        
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
        
        self.colors = self.color_schemes.get(style, self.color_schemes['dark'])
        self.timestamps = None
        self.panels_data = []
        
    def _normalize_color(self, color):
        """Convert color to normalized RGBA format for Dear PyGui."""
        if isinstance(color, list) and len(color) >= 3:
            if all(c <= 1.0 for c in color[:3]):
                return color[:4] if len(color) >= 4 else color + [1.0]
            else:
                normalized = [c/255.0 for c in color[:3]]
                if len(color) >= 4:
                    normalized.append(color[3]/255.0 if color[3] > 1.0 else color[3])
                else:
                    normalized.append(1.0)
                return normalized
        return [1.0, 1.0, 1.0, 1.0]
    
    def _create_window(self):
        """Create the main window with a menu bar and a child window for content."""
        if self.window_tag is not None:
            try:
                if dpg.does_item_exist(self.window_tag):
                    dpg.delete_item(self.window_tag)
            except Exception as e:
                print(f"Error deleting existing window: {e}")
        
        self.window_tag = "main_plot_window"
        
        with dpg.window(tag=self.window_tag, label="Trading Analysis", 
                       width=self.figsize[0], height=self.figsize[1],
                       no_close=False):

            if self.show_header:
                with dpg.menu_bar(tag="main_menu_bar"):
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
            
            # Add a child window for the plot content that fills the remaining space.
            dpg.add_child_window(tag="content_area", width=-1, height=-1)

    def _setup_crosshair(self, plot_tag):
        """Setup crosshair functionality for a plot."""
        def crosshair_callback(sender, app_data, user_data):
            mouse_x, mouse_y = dpg.get_plot_mouse_pos()
            plot_tag = user_data
            
            if plot_tag in self.crosshair_lines:
                for line_tag in self.crosshair_lines[plot_tag]:
                    try:
                        if dpg.does_item_exist(line_tag):
                            dpg.delete_item(line_tag)
                    except:
                        pass
                self.crosshair_lines[plot_tag] = []
            else:
                self.crosshair_lines[plot_tag] = []
            
            if mouse_x is not None and mouse_y is not None:
                vline_tag = f"{plot_tag}_crosshair_v"
                hline_tag = f"{plot_tag}_crosshair_h"
                
                try:
                    x_min, x_max = dpg.get_axis_limits(dpg.get_item_children(plot_tag, 1)[0])
                    y_min, y_max = dpg.get_axis_limits(dpg.get_item_children(plot_tag, 1)[1])
                    
                    dpg.add_line_series([mouse_x, mouse_x], [y_min, y_max], tag=vline_tag, parent=plot_tag)
                    dpg.set_item_theme(vline_tag, "crosshair_theme")
                    
                    dpg.add_line_series([x_min, x_max], [mouse_y, mouse_y], tag=hline_tag, parent=plot_tag)
                    dpg.set_item_theme(hline_tag, "crosshair_theme")
                    
                    self.crosshair_lines[plot_tag] = [vline_tag, hline_tag]
                except:
                    pass
        
        with dpg.item_handler_registry(tag=f"{plot_tag}_handler"):
            dpg.add_item_hover_handler(callback=crosshair_callback, user_data=plot_tag)
        
        dpg.bind_item_handler_registry(plot_tag, f"{plot_tag}_handler")
    
    def _create_themes(self):
        """Create themes for different UI elements."""
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
        """
        if not panels:
            raise ValueError("At least one panel must be provided")
        
        if not DEARPYGUI_AVAILABLE:
            print("Dear PyGui not available. Please install with: pip install dearpygui")
            return
        
        try:
            if not self.context_created:
                dpg.create_context()
                self.context_created = True
            
            self.timestamps = timestamps
            self.panels_data = panels
            self.synchronized_zoom = synchronized_zoom
            
            if figsize:
                self.figsize = figsize
            
            self._create_themes()
            self._create_window()
            
            total_ratio = sum(panel.get('height_ratio', 1) for panel in panels)
            # Estimate available height, leaving space for the menu bar (~30px) and some padding
            available_height = self.figsize[1] - 80
            
            self.panel_heights = []
            for panel in panels:
                ratio = panel.get('height_ratio', 1)
                height = int((ratio / total_ratio) * available_height)
                self.panel_heights.append(max(height, 150))
            
            # Clear previous plots and recreate them
            if dpg.does_item_exist("content_area"):
                dpg.delete_item("content_area", children_only=True)
            self.plots.clear()

            for i, (panel, height) in enumerate(zip(panels, self.panel_heights)):
                plot_tag = f"plot_{i}"
                x_axis_tag = f"x_axis_{i}"
                y_axis_tag = f"y_axis_{i}"
                panel_title = panel.get('title', f'Panel {i}')
                
                # Add the plot directly to the content_area child window
                dpg.add_plot(tag=plot_tag, label=panel_title, height=height, width=-1, parent="content_area")
                
                dpg.add_plot_axis(dpg.mvXAxis, tag=x_axis_tag, label="Time", parent=plot_tag)
                dpg.add_plot_axis(dpg.mvYAxis, tag=y_axis_tag, label="Value", parent=plot_tag)
                
                self._plot_panel_data(panel, plot_tag, x_axis_tag, y_axis_tag, i)
                
                if self.synchronized_zoom:
                    self._setup_sync_callback(plot_tag, x_axis_tag, i)
                
                self.plots.append({
                    'plot_tag': plot_tag,
                    'x_axis_tag': x_axis_tag, 
                    'y_axis_tag': y_axis_tag,
                    'panel_data': panel
                })
            
            self._setup_resize_callback()
            
            print(f"Multi-panel chart created with {len(panels)} panels using Dear PyGui")

        except Exception as e:
            print(f"Error creating Dear PyGui chart: {e}")
            import traceback
            traceback.print_exc()
    
    def _plot_panel_data(self, panel, plot_tag, x_axis_tag, y_axis_tag, panel_index):
        """Plot data for a single panel."""
        panel_data = panel.get('series_data', {})
        
        if self.timestamps is not None and len(self.timestamps) > 0:
            x_data = list(range(len(self.timestamps)))
        else:
            max_length = 0
            for data in panel_data.values():
                if isinstance(data, (np.ndarray, list)):
                    max_length = max(max_length, len(data))
            x_data = list(range(max_length))
        
        color_index = 0
        for name, data in panel_data.items():
            try:
                color = self.colors['line_colors'][color_index % len(self.colors['line_colors'])]
                if isinstance(data, (int, float)):
                    self._add_horizontal_line(data, name, color, y_axis_tag)
                elif isinstance(data, (np.ndarray, list)) and len(data) > 0:
                    self._add_line_series(x_data, data, name, color, y_axis_tag)
                color_index += 1
            except Exception as e:
                print(f"Warning: Could not plot series '{name}': {e}")

        yon_list = panel.get('yon_list', None)
        seviye_list = panel.get('seviye_list', None)
        if yon_list and seviye_list:
            try:
                self._plot_direction_levels(x_data, yon_list, seviye_list, y_axis_tag)
            except Exception as e:
                print(f"Warning: Could not plot direction levels: {e}")

    def _add_line_series(self, x_data, y_data, name, color, y_axis_tag):
        """Add a line series to the plot."""
        min_length = min(len(x_data), len(y_data))
        x_plot, y_plot = x_data[:min_length], y_data[:min_length]

        if isinstance(y_plot, np.ndarray):
            valid_mask = ~np.isnan(y_plot)
            if not np.any(valid_mask): return
            x_plot = [x for i, x in enumerate(x_plot) if valid_mask[i]]
            y_plot = y_plot[valid_mask].tolist()
        
        series_tag = f"{y_axis_tag}_{name}"
        normalized_color = self._normalize_color(color)
        
        dpg.add_line_series(x_plot, y_plot, tag=series_tag, parent=y_axis_tag, label=name)
        
        theme_tag = f"{series_tag}_theme"
        with dpg.theme(tag=theme_tag):
            with dpg.theme_component(dpg.mvLineSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, [int(c*255) for c in normalized_color])
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2)
        dpg.bind_item_theme(series_tag, theme_tag)

    def _add_horizontal_line(self, y_value, name, color, y_axis_tag):
        """Add a horizontal line to the plot."""
        x_range = [-1000000, 1000000]
        y_range = [y_value, y_value]
        series_tag = f"{y_axis_tag}_{name}_hline"
        normalized_color = self._normalize_color(color)
        
        dpg.add_line_series(x_range, y_range, tag=series_tag, parent=y_axis_tag, label=name)
        
        theme_tag = f"{series_tag}_theme"
        with dpg.theme(tag=theme_tag):
            with dpg.theme_component(dpg.mvLineSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, [int(c*255) for c in normalized_color])
                dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2)
        dpg.bind_item_theme(series_tag, theme_tag)

    def _plot_direction_levels(self, x_data, yon_list, seviye_list, y_axis_tag):
        """Plot dynamic support/resistance lines."""
        if not yon_list or not seviye_list or len(yon_list) != len(seviye_list):
            return
        
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
        
        for i, signal in enumerate(signal_changes):
            end_index = len(x_data) - 1
            x_end = x_data[-1]
            if i + 1 < len(signal_changes):
                x_end = signal_changes[i + 1]['x_pos']
                end_index = signal_changes[i + 1]['index']
            
            if abs(end_index - signal['index']) > 1:
                color = self._normalize_color(self.colors['candle_up'] if signal['direction'] == 'A' else self.colors['candle_down'])
                line_y = signal['level'] * (0.999 if signal['direction'] == 'A' else 1.001)
                x_line, y_line = [signal['x_pos'], x_end], [line_y, line_y]
                
                series_tag = f"direction_line_{i}_{signal['direction']}"
                dpg.add_line_series(x_line, y_line, tag=series_tag, parent=y_axis_tag)
                
                theme_tag = f"{series_tag}_theme"
                with dpg.theme(tag=theme_tag):
                    with dpg.theme_component(dpg.mvLineSeries):
                        dpg.add_theme_color(dpg.mvPlotCol_Line, [int(c*255) for c in color[:3]] + [160])
                        dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2)
                dpg.bind_item_theme(series_tag, theme_tag)

    def _setup_resize_callback(self):
        """Setup window resize callback."""
        if self.resize_callback_registered or not self.window_tag: return
        try:
            def resize_callback(sender, app_data, user_data):
                try:
                    new_height = dpg.get_item_height(self.window_tag)
                    if new_height > 100: self._update_panel_heights(new_height)
                except Exception as e:
                    print(f"Resize callback error: {e}")
            
            with dpg.item_handler_registry(tag=f"{self.window_tag}_resize_handler"):
                dpg.add_item_resize_handler(callback=resize_callback)
            dpg.bind_item_handler_registry(self.window_tag, f"{self.window_tag}_resize_handler")
            self.resize_callback_registered = True
        except Exception as e:
            print(f"Warning: Could not setup resize callback: {e}")

    def _update_panel_heights(self, new_window_height):
        """Update panel heights based on new window size."""
        if not self.plots or not self.panels_data: return
        try:
            total_ratio = sum(p.get('height_ratio', 1) for p in self.panels_data)
            available_height = new_window_height - 80
            
            self.panel_heights = [max(int((p.get('height_ratio', 1) / total_ratio) * available_height), 150) for p in self.panels_data]
            
            for i, plot_info in enumerate(self.plots):
                if i < len(self.panel_heights):
                    try:
                        dpg.configure_item(plot_info['plot_tag'], height=self.panel_heights[i])
                    except: pass
        except Exception as e:
            print(f"Warning: Could not update panel heights: {e}")

    def _setup_sync_callback(self, plot_tag, x_axis_tag, panel_index):
        """Setup synchronized zoom and pan callback."""
        if not self.synchronized_zoom: return
        try:
            def sync_callback(sender, app_data, user_data):
                if not self.synchronized_zoom: return
                try:
                    x_min, x_max = dpg.get_axis_limits(x_axis_tag)
                    for plot_info in self.plots:
                        if plot_info['x_axis_tag'] != x_axis_tag:
                            try:
                                dpg.set_axis_limits(plot_info['x_axis_tag'], x_min, x_max)
                            except: pass
                except: pass
            
            with dpg.item_handler_registry(tag=f"{plot_tag}_sync_handler"):
                dpg.add_item_clicked_handler(callback=sync_callback)
                dpg.add_item_hover_handler(callback=sync_callback)
            dpg.bind_item_handler_registry(plot_tag, f"{plot_tag}_sync_handler")
        except Exception as e:
            print(f"Warning: Could not setup sync callback for panel {panel_index}: {e}")

    def _on_open_data(self): print("Open data callback")
    def _on_save_chart(self): print("Save chart callback")
    def _on_export_png(self): print("Export PNG callback")
    def _on_export_csv(self): print("Export CSV callback")

    def _on_reset_zoom(self):
        for plot_info in self.plots:
            try:
                if dpg.does_item_exist(plot_info['x_axis_tag']): dpg.fit_axis_data(plot_info['x_axis_tag'])
                if dpg.does_item_exist(plot_info['y_axis_tag']): dpg.fit_axis_data(plot_info['y_axis_tag'])
            except Exception as e:
                print(f"Error resetting zoom: {e}")

    def _on_fit_window(self): self._on_reset_zoom()
    def _on_toggle_crosshair(self, sender, app_data): print(f"Toggle crosshair: {app_data}")
    def _on_toggle_sync_zoom(self, sender, app_data): self.synchronized_zoom = app_data; print(f"Sync zoom: {app_data}")
    def _on_analysis_tools(self): print("Analysis tools callback")
    def _on_indicator_panel(self): print("Indicator panel callback")
    def _on_settings(self): print("Settings callback")

    def show(self, interactive: bool = True):
        """Display the chart."""
        if self.window_tag is None: raise ValueError("Call plot_multi_panel() first.")
        if dpg.is_dearpygui_running(): return
        
        try:
            if not self.context_created:
                dpg.create_context()
                self.context_created = True
            
            dpg.create_viewport(title="Trading Analysis", width=self.figsize[0], height=self.figsize[1])
            dpg.setup_dearpygui()
            dpg.show_viewport()
            dpg.set_primary_window(self.window_tag, True)
            dpg.start_dearpygui()
            
        except Exception as e:
            print(f"Error displaying chart: {e}")
        finally:
            if dpg.is_dearpygui_running():
                dpg.stop_dearpygui()
            if self.context_created:
                dpg.destroy_context()
                self.context_created = False

    def close(self):
        if self.window_tag and dpg.does_item_exist(self.window_tag):
            dpg.delete_item(self.window_tag)
        self.window_tag = None
        self.plots.clear()

    def plot_series(self, timestamps: Optional[np.ndarray] = None, series_data: Optional[Dict[str, Any]] = None, title: str = "Series Plot", figsize: Optional[Tuple[int, int]] = None):
        panels = [{'series_data': series_data or {}, 'title': title, 'height_ratio': 1}]
        self.plot_multi_panel(timestamps=timestamps or np.array([]), panels=panels, figsize=figsize)

    def __repr__(self) -> str:
        return f"DataPlotterDearPyGui(style='{self.style}', plots={len(self.plots)}, figsize={self.figsize})"
