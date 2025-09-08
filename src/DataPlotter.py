"""
Data Plotter for algorithmic trading system visualization.

This module contains the DataPlotter class which provides comprehensive
data visualization capabilities for OHLCV data, technical indicators, and trading signals.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import warnings

# Suppress matplotlib warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')


class DataPlotter:
    """
    Data visualization class for trading system analysis.
    
    Features:
    - OHLCV candlestick charts
    - Technical indicator overlays
    - Trading signal markers
    - Multiple subplot support
    - Customizable styling and themes
    """
    
    def __init__(self, figsize: Tuple[int, int] = (15, 10), style: str = 'dark'):
        """
        Initialize the data plotter.
        
        Args:
            figsize: Figure size as (width, height)
            style: Plot style ('dark', 'light', 'classic')
        """
        self.figsize = figsize
        self.style = style
        self.fig = None
        self.axes = []
        
        # Color schemes
        self.color_schemes = {
            'dark': {
                'bg_color': '#1e1e1e',
                'text_color': 'white',
                'grid_color': '#333333',
                'candle_up': '#00ff88',
                'candle_down': '#ff4444',
                'volume_color': '#666666',
                'ma_colors': ['#ffaa00', '#00aaff', '#ff00aa', '#aa00ff'],
                'signal_buy': '#00ff00',
                'signal_sell': '#ff0000'
            },
            'light': {
                'bg_color': 'white',
                'text_color': 'black',
                'grid_color': '#cccccc',
                'candle_up': '#26a69a',
                'candle_down': '#ef5350',
                'volume_color': '#90a4ae',
                'ma_colors': ['#ff9800', '#2196f3', '#e91e63', '#9c27b0'],
                'signal_buy': '#4caf50',
                'signal_sell': '#f44336'
            },
            'classic': {
                'bg_color': 'white',
                'text_color': 'black',
                'grid_color': '#e0e0e0',
                'candle_up': 'green',
                'candle_down': 'red',
                'volume_color': 'blue',
                'ma_colors': ['orange', 'blue', 'purple', 'brown'],
                'signal_buy': 'green',
                'signal_sell': 'red'
            }
        }
        
        self.colors = self.color_schemes.get(style, self.color_schemes['dark'])
        
        # Set matplotlib style
        plt.style.use('dark_background' if style == 'dark' else 'default')
    
    def create_subplots(self, rows: int = 2, height_ratios: Optional[List[float]] = None) -> None:
        """
        Create subplot structure.
        
        Args:
            rows: Number of subplot rows
            height_ratios: Height ratios for subplots
        """
        if height_ratios is None:
            height_ratios = [3, 1] if rows == 2 else [1] * rows
        
        self.fig, self.axes = plt.subplots(
            rows, 1, 
            figsize=self.figsize,
            gridspec_kw={'height_ratios': height_ratios, 'hspace': 0.1},
            facecolor=self.colors['bg_color']
        )
        
        # Ensure axes is always a list
        if not isinstance(self.axes, (list, np.ndarray)):
            self.axes = [self.axes]
        
        # Configure all axes
        for ax in self.axes:
            ax.set_facecolor(self.colors['bg_color'])
            ax.tick_params(colors=self.colors['text_color'])
            ax.grid(True, color=self.colors['grid_color'], alpha=0.3)
            for spine in ax.spines.values():
                spine.set_color(self.colors['text_color'])
    
    def plot_candlestick(self, 
                        timestamps: np.ndarray,
                        open_data: np.ndarray,
                        high_data: np.ndarray, 
                        low_data: np.ndarray,
                        close_data: np.ndarray,
                        ax_index: int = 0,
                        title: str = "OHLC Data") -> None:
        """
        Plot candlestick chart.
        
        Args:
            timestamps: Unix timestamps
            open_data: Open prices
            high_data: High prices
            low_data: Low prices
            close_data: Close prices
            ax_index: Subplot index
            title: Chart title
        """
        if ax_index >= len(self.axes):
            raise ValueError(f"Axis index {ax_index} out of range")
        
        ax = self.axes[ax_index]
        
        # Convert timestamps to datetime
        dates = [datetime.fromtimestamp(ts) for ts in timestamps]
        
        # Plot candlesticks
        for i, (date, o, h, l, c) in enumerate(zip(dates, open_data, high_data, low_data, close_data)):
            color = self.colors['candle_up'] if c >= o else self.colors['candle_down']
            
            # High-low line
            ax.plot([date, date], [l, h], color=color, linewidth=1)
            
            # Open-close rectangle
            height = abs(c - o)
            bottom = min(o, c)
            rect = Rectangle((mdates.date2num(date) - 0.3, bottom), 0.6, height, 
                           facecolor=color, alpha=0.8)
            ax.add_patch(rect)
        
        ax.set_title(title, color=self.colors['text_color'], fontsize=14, fontweight='bold')
        ax.set_ylabel('Price', color=self.colors['text_color'])
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, len(dates)//10)))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def plot_volume(self,
                   timestamps: np.ndarray,
                   volume_data: np.ndarray,
                   ax_index: int = 1,
                   title: str = "Volume") -> None:
        """
        Plot volume bars.
        
        Args:
            timestamps: Unix timestamps
            volume_data: Volume data
            ax_index: Subplot index
            title: Chart title
        """
        if ax_index >= len(self.axes):
            raise ValueError(f"Axis index {ax_index} out of range")
        
        ax = self.axes[ax_index]
        
        # Convert timestamps to datetime
        dates = [datetime.fromtimestamp(ts) for ts in timestamps]
        
        # Plot volume bars
        ax.bar(dates, volume_data, color=self.colors['volume_color'], alpha=0.7, width=0.8)
        
        ax.set_title(title, color=self.colors['text_color'], fontsize=12)
        ax.set_ylabel('Volume', color=self.colors['text_color'])
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, len(dates)//10)))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def plot_indicators(self,
                       timestamps: np.ndarray,
                       indicators: Dict[str, np.ndarray],
                       ax_index: int = 0) -> None:
        """
        Plot technical indicators.
        
        Args:
            timestamps: Unix timestamps
            indicators: Dictionary of indicator name -> data arrays
            ax_index: Subplot index
        """
        if ax_index >= len(self.axes):
            raise ValueError(f"Axis index {ax_index} out of range")
        
        ax = self.axes[ax_index]
        
        # Convert timestamps to datetime
        dates = [datetime.fromtimestamp(ts) for ts in timestamps]
        
        # Plot each indicator
        for i, (name, data) in enumerate(indicators.items()):
            color = self.colors['ma_colors'][i % len(self.colors['ma_colors'])]
            
            # Filter out NaN values for cleaner plots
            valid_mask = ~np.isnan(data)
            valid_dates = [d for d, v in zip(dates, valid_mask) if v]
            valid_data = data[valid_mask]
            
            ax.plot(valid_dates, valid_data, color=color, linewidth=2, 
                   label=name, alpha=0.8)
        
        # Add legend if indicators were plotted
        if indicators:
            ax.legend(loc='upper left', framealpha=0.8, 
                     facecolor=self.colors['bg_color'],
                     edgecolor=self.colors['text_color'],
                     labelcolor=self.colors['text_color'])
    
    def plot_signals(self,
                    timestamps: np.ndarray,
                    prices: np.ndarray,
                    buy_signals: np.ndarray,
                    sell_signals: np.ndarray,
                    ax_index: int = 0) -> None:
        """
        Plot trading signals.
        
        Args:
            timestamps: Unix timestamps
            prices: Price data for signal positioning
            buy_signals: Boolean array of buy signals
            sell_signals: Boolean array of sell signals
            ax_index: Subplot index
        """
        if ax_index >= len(self.axes):
            raise ValueError(f"Axis index {ax_index} out of range")
        
        ax = self.axes[ax_index]
        
        # Convert timestamps to datetime
        dates = [datetime.fromtimestamp(ts) for ts in timestamps]
        
        # Plot buy signals
        buy_indices = np.where(buy_signals)[0]
        if len(buy_indices) > 0:
            buy_dates = [dates[i] for i in buy_indices]
            buy_prices = prices[buy_indices]
            ax.scatter(buy_dates, buy_prices, color=self.colors['signal_buy'], 
                      marker='^', s=100, label='Buy Signal', zorder=5)
        
        # Plot sell signals
        sell_indices = np.where(sell_signals)[0]
        if len(sell_indices) > 0:
            sell_dates = [dates[i] for i in sell_indices]
            sell_prices = prices[sell_indices]
            ax.scatter(sell_dates, sell_prices, color=self.colors['signal_sell'], 
                      marker='v', s=100, label='Sell Signal', zorder=5)
        
        # Update legend
        if len(buy_indices) > 0 or len(sell_indices) > 0:
            ax.legend(loc='upper left', framealpha=0.8,
                     facecolor=self.colors['bg_color'],
                     edgecolor=self.colors['text_color'],
                     labelcolor=self.colors['text_color'])
    
    def plot_rsi(self,
                timestamps: np.ndarray,
                rsi_data: np.ndarray,
                ax_index: int = 2,
                title: str = "RSI") -> None:
        """
        Plot RSI indicator with overbought/oversold levels.
        
        Args:
            timestamps: Unix timestamps
            rsi_data: RSI values
            ax_index: Subplot index
            title: Chart title
        """
        if ax_index >= len(self.axes):
            # Create additional subplot if needed
            self.create_subplots(ax_index + 1)
        
        ax = self.axes[ax_index]
        
        # Convert timestamps to datetime
        dates = [datetime.fromtimestamp(ts) for ts in timestamps]
        
        # Filter out NaN values
        valid_mask = ~np.isnan(rsi_data)
        valid_dates = [d for d, v in zip(dates, valid_mask) if v]
        valid_rsi = rsi_data[valid_mask]
        
        # Plot RSI line
        ax.plot(valid_dates, valid_rsi, color='#ffaa00', linewidth=2, label='RSI')
        
        # Plot overbought/oversold levels
        ax.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
        ax.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
        ax.axhline(y=50, color='gray', linestyle='-', alpha=0.5, label='Midline (50)')
        
        ax.set_title(title, color=self.colors['text_color'], fontsize=12)
        ax.set_ylabel('RSI', color=self.colors['text_color'])
        ax.set_ylim(0, 100)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=max(1, len(dates)//10)))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        ax.legend(loc='upper left', framealpha=0.8,
                 facecolor=self.colors['bg_color'],
                 edgecolor=self.colors['text_color'],
                 labelcolor=self.colors['text_color'])
    
    def create_comprehensive_chart(self,
                                  timestamps: np.ndarray,
                                  open_data: np.ndarray,
                                  high_data: np.ndarray,
                                  low_data: np.ndarray,
                                  close_data: np.ndarray,
                                  volume_data: np.ndarray,
                                  indicators: Optional[Dict[str, np.ndarray]] = None,
                                  rsi_data: Optional[np.ndarray] = None,
                                  buy_signals: Optional[np.ndarray] = None,
                                  sell_signals: Optional[np.ndarray] = None,
                                  title: str = "Trading Analysis") -> None:
        """
        Create a comprehensive trading chart with all components.
        
        Args:
            timestamps: Unix timestamps
            open_data: Open prices
            high_data: High prices
            low_data: Low prices
            close_data: Close prices
            volume_data: Volume data
            indicators: Dictionary of technical indicators
            rsi_data: RSI values
            buy_signals: Buy signal boolean array
            sell_signals: Sell signal boolean array
            title: Main chart title
        """
        # Determine number of subplots needed
        subplot_count = 2  # Price + Volume
        if rsi_data is not None:
            subplot_count = 3  # Price + Volume + RSI
        
        # Create subplots
        height_ratios = [3, 1, 1] if subplot_count == 3 else [3, 1]
        self.create_subplots(subplot_count, height_ratios)
        
        # Plot candlestick chart
        self.plot_candlestick(timestamps, open_data, high_data, low_data, close_data, 
                             ax_index=0, title=title)
        
        # Plot indicators on price chart
        if indicators:
            self.plot_indicators(timestamps, indicators, ax_index=0)
        
        # Plot trading signals
        if buy_signals is not None or sell_signals is not None:
            buy_sigs = buy_signals if buy_signals is not None else np.zeros(len(close_data), dtype=bool)
            sell_sigs = sell_signals if sell_signals is not None else np.zeros(len(close_data), dtype=bool)
            self.plot_signals(timestamps, close_data, buy_sigs, sell_sigs, ax_index=0)
        
        # Plot volume
        self.plot_volume(timestamps, volume_data, ax_index=1)
        
        # Plot RSI if provided
        if rsi_data is not None:
            self.plot_rsi(timestamps, rsi_data, ax_index=2)
    
    def save_chart(self, filename: str, dpi: int = 300, bbox_inches: str = 'tight') -> None:
        """
        Save the chart to file.
        
        Args:
            filename: Output filename
            dpi: Image resolution
            bbox_inches: Bounding box configuration
        """
        if self.fig is None:
            raise ValueError("No chart created. Call create_comprehensive_chart() first.")
        
        self.fig.savefig(filename, dpi=dpi, bbox_inches=bbox_inches, 
                        facecolor=self.colors['bg_color'],
                        edgecolor=self.colors['text_color'])
        print(f"Chart saved to: {filename}")
    
    def show(self, interactive: bool = True) -> None:
        """
        Display the chart with interactive navigation.
        
        Args:
            interactive: Enable interactive zoom/pan controls
        """
        if self.fig is None:
            raise ValueError("No chart created. Call create_comprehensive_chart() first.")
        
        if interactive:
            # Enable interactive navigation toolbar
            # This provides zoom, pan, home, back, forward, configure subplot buttons
            from matplotlib.widgets import RectangleSelector
            import matplotlib.pyplot as plt
            
            # Enable the toolbar
            plt.rcParams['toolbar'] = 'toolbar2'
            
            # Connect mouse scroll zoom functionality
            def on_scroll(event):
                if event.inaxes is None:
                    return
                
                ax = event.inaxes
                x_center, y_center = event.xdata, event.ydata
                if x_center is None or y_center is None:
                    return
                
                # Get current axis limits
                x_min, x_max = ax.get_xlim()
                y_min, y_max = ax.get_ylim()
                
                # Zoom factor
                zoom_factor = 1.2 if event.button == 'down' else 1/1.2
                
                # Calculate new limits
                x_range = (x_max - x_min) * zoom_factor
                y_range = (y_max - y_min) * zoom_factor
                
                new_x_min = x_center - x_range/2
                new_x_max = x_center + x_range/2
                new_y_min = y_center - y_range/2
                new_y_max = y_center + y_range/2
                
                # Apply new limits
                ax.set_xlim(new_x_min, new_x_max)
                ax.set_ylim(new_y_min, new_y_max)
                
                # Redraw
                self.fig.canvas.draw()
            
            # Connect scroll event
            self.fig.canvas.mpl_connect('scroll_event', on_scroll)
            
            # Add crosshair cursor functionality
            def on_mouse_move(event):
                if event.inaxes is None:
                    return
                
                # Remove previous crosshair lines
                for ax in self.axes:
                    # Remove existing crosshair lines
                    lines_to_remove = []
                    for line in ax.lines:
                        if hasattr(line, '_crosshair'):
                            lines_to_remove.append(line)
                    for line in lines_to_remove:
                        line.remove()
                
                # Add crosshair to current axis
                ax = event.inaxes
                if event.xdata is not None and event.ydata is not None:
                    # Vertical line
                    vline = ax.axvline(x=event.xdata, color='gray', linestyle='--', alpha=0.5, linewidth=1)
                    vline._crosshair = True
                    
                    # Horizontal line
                    hline = ax.axhline(y=event.ydata, color='gray', linestyle='--', alpha=0.5, linewidth=1)
                    hline._crosshair = True
                    
                    # Update canvas
                    self.fig.canvas.draw_idle()
            
            # Connect mouse move event for crosshair
            self.fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
            
            print("Interactive mode enabled:")
            print("- Mouse wheel: Zoom in/out at cursor position")  
            print("- Toolbar: Pan, zoom box, home, back/forward")
            print("- Mouse hover: Crosshair cursor")
            print("- Right-click: Context menu with additional options")
        
        # Layout is automatically handled by constrained_layout=True in subplot creation
        # No manual layout adjustment needed
        
        plt.show()
    
    def close(self) -> None:
        """Close the current figure."""
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.axes = []
    
    def plot_series(self, 
                   timestamps: Optional[np.ndarray] = None,
                   series_data: Optional[Dict[str, Any]] = None,
                   title: str = "Series Plot",
                   xlabel: str = "Time",
                   ylabel: str = "Value",
                   figsize: Optional[Tuple[int, int]] = None) -> None:
        """
        Plot multiple series and levels on the same chart.
        
        Args:
            timestamps: Unix timestamps (if None, uses index numbers)
            series_data: Dictionary where key is series name and value can be:
                        - np.ndarray: Series data to plot as line
                        - float/int: Single value to plot as horizontal level
                        - dict: Advanced configuration with 'data', 'color', 'style', etc.
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            figsize: Figure size override
            
        Examples:
            # Plot multiple series and levels
            plotter.plot_series(
                timestamps=Time,
                series_data={
                    'Close': Close,                    # Array - line plot
                    'MA20': MA1,                      # Array - line plot  
                    'MA50': MA2,                      # Array - line plot
                    'Support': 45000,                 # Number - horizontal line
                    'Resistance': 55000,              # Number - horizontal line
                    'RSI': {'data': Rsi, 'color': 'purple', 'style': '--'}  # Advanced config
                },
                title="Price Analysis with Levels"
            )
        """
        if series_data is None:
            series_data = {}
        
        # Use provided figsize or default
        fig_size = figsize or self.figsize
        
        # Create single subplot
        self.fig, ax = plt.subplots(1, 1, figsize=fig_size, 
                                   facecolor=self.colors['bg_color'])
        self.axes = [ax]  # Keep compatibility with existing methods
        
        # Configure axis
        ax.set_facecolor(self.colors['bg_color'])
        ax.tick_params(colors=self.colors['text_color'])
        ax.grid(True, color=self.colors['grid_color'], alpha=0.3)
        for spine in ax.spines.values():
            spine.set_color(self.colors['text_color'])
        
        # Determine x-axis data
        if timestamps is not None:
            # Convert timestamps to datetime for better formatting
            x_data = [datetime.fromtimestamp(ts) for ts in timestamps]
            use_datetime = True
        else:
            # Use index numbers if no timestamps provided
            max_length = 0
            for name, data in series_data.items():
                if isinstance(data, (np.ndarray, list)):
                    max_length = max(max_length, len(data))
                elif isinstance(data, dict) and 'data' in data:
                    if isinstance(data['data'], (np.ndarray, list)):
                        max_length = max(max_length, len(data['data']))
            
            x_data = list(range(max_length))
            use_datetime = False
        
        # Color cycling for automatic colors
        color_index = 0
        
        # Plot each series
        for name, data in series_data.items():
            try:
                if isinstance(data, dict):
                    # Advanced configuration
                    plot_data = data.get('data', [])
                    color = data.get('color', self.colors['ma_colors'][color_index % len(self.colors['ma_colors'])])
                    linestyle = data.get('style', '-')
                    linewidth = data.get('width', 2)
                    alpha = data.get('alpha', 0.8)
                    
                    if isinstance(plot_data, (int, float)):
                        # Single value - horizontal line
                        ax.axhline(y=plot_data, color=color, linestyle=linestyle, 
                                  linewidth=linewidth, alpha=alpha, label=name)
                    elif isinstance(plot_data, (np.ndarray, list)) and len(plot_data) > 0:
                        # Array data - line plot
                        if use_datetime and len(x_data) >= len(plot_data):
                            # Filter out NaN values for cleaner plots
                            if isinstance(plot_data, np.ndarray):
                                valid_mask = ~np.isnan(plot_data)
                                valid_x = [x_data[i] for i, v in enumerate(valid_mask) if v and i < len(x_data)]
                                valid_y = plot_data[valid_mask]
                            else:
                                valid_x = x_data[:len(plot_data)]
                                valid_y = plot_data
                            
                            ax.plot(valid_x, valid_y, color=color, linestyle=linestyle,
                                   linewidth=linewidth, alpha=alpha, label=name)
                        else:
                            # Use index-based plotting
                            x_indices = list(range(len(plot_data)))
                            ax.plot(x_indices, plot_data, color=color, linestyle=linestyle,
                                   linewidth=linewidth, alpha=alpha, label=name)
                
                elif isinstance(data, (int, float)):
                    # Single value - horizontal level
                    color = self.colors['ma_colors'][color_index % len(self.colors['ma_colors'])]
                    ax.axhline(y=data, color=color, linestyle='--', linewidth=2, 
                              alpha=0.8, label=name)
                
                elif isinstance(data, (np.ndarray, list)) and len(data) > 0:
                    # Array data - simple line plot
                    color = self.colors['ma_colors'][color_index % len(self.colors['ma_colors'])]
                    
                    if use_datetime and len(x_data) >= len(data):
                        # Filter out NaN values for cleaner plots
                        if isinstance(data, np.ndarray):
                            valid_mask = ~np.isnan(data)
                            valid_x = [x_data[i] for i, v in enumerate(valid_mask) if v and i < len(x_data)]
                            valid_y = data[valid_mask]
                        else:
                            valid_x = x_data[:len(data)]
                            valid_y = data
                        
                        ax.plot(valid_x, valid_y, color=color, linewidth=2, 
                               alpha=0.8, label=name)
                    else:
                        # Use index-based plotting
                        x_indices = list(range(len(data)))
                        ax.plot(x_indices, data, color=color, linewidth=2,
                               alpha=0.8, label=name)
                
                color_index += 1
                
            except Exception as e:
                print(f"Warning: Could not plot series '{name}': {e}")
                continue
        
        # Set labels and title
        ax.set_title(title, color=self.colors['text_color'], fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, color=self.colors['text_color'])
        ax.set_ylabel(ylabel, color=self.colors['text_color'])
        
        # Format x-axis for datetime
        if use_datetime and timestamps is not None:
            # Use MaxNLocator to directly limit number of ticks - more reliable than HourLocator
            from matplotlib.ticker import MaxNLocator
            
            data_length = len(x_data)
            if data_length > 1000:
                max_ticks = 10  # Very large datasets - minimal ticks
            elif data_length > 500:
                max_ticks = 15  # Large datasets
            elif data_length > 100:
                max_ticks = 20  # Medium datasets  
            else:
                max_ticks = 30  # Small datasets - more detail
            
            # Force maximum number of ticks to avoid matplotlib errors
            ax.xaxis.set_major_locator(MaxNLocator(nbins=max_ticks, prune='both'))
            
            # Use shorter time format for better readability
            if data_length > 1000:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))  # Month/Day for very large datasets
            elif data_length > 100:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))  # Month/Day Hour:Min
            else:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Hour:Min for small datasets
            
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Add legend if there are series to show
        if series_data:
            ax.legend(loc='upper left', framealpha=0.8,
                     facecolor=self.colors['bg_color'],
                     edgecolor=self.colors['text_color'],
                     labelcolor=self.colors['text_color'])
        
        plt.tight_layout()

    def plot_multi_panel(self,
                        timestamps: np.ndarray,
                        panels: List[Dict[str, Any]],
                        synchronized_zoom: bool = True,
                        figsize: Optional[Tuple[int, int]] = None) -> None:
        """
        Plot multi-panel chart with N panels and synchronized zoom functionality.
        
        Args:
            timestamps: Unix timestamps
            panels: List of panel configs, each panel should have:
                   - 'series_data': Dict of series name -> data
                   - 'title': Panel title
                   - 'height_ratio': Optional height ratio (default: 1)
            synchronized_zoom: Enable synchronized zoom between panels
            figsize: Figure size override
            
        Example:
            panels = [
                {
                    'series_data': {'Close Price': self.Close, 'Level': self.Level},
                    'title': 'Price Chart',
                    'height_ratio': 3
                },
                {
                    'series_data': {'Balance': self.BakiyeFiyatList},
                    'title': 'Balance',
                    'height_ratio': 1
                }
            ]
        """
        if not panels:
            raise ValueError("At least one panel must be provided")
            
        # Use provided figsize or default
        fig_size = figsize or self.figsize
        
        # Extract height ratios from panels or use defaults
        height_ratios = []
        for panel in panels:
            ratio = panel.get('height_ratio', 1)
            height_ratios.append(ratio)
        
        # Create N-panel subplots with different height ratios
        panel_count = len(panels)
        self.fig, self.axes = plt.subplots(panel_count, 1, figsize=fig_size, 
                                          gridspec_kw={'height_ratios': height_ratios, 'hspace': 0.2},
                                          facecolor=self.colors['bg_color'],
                                          constrained_layout=True)
        
        # Ensure axes is always a list
        if not isinstance(self.axes, (list, np.ndarray)):
            self.axes = [self.axes]
        
        # Configure all axes
        for ax in self.axes:
            ax.set_facecolor(self.colors['bg_color'])
            ax.tick_params(colors=self.colors['text_color'])
            ax.grid(True, color=self.colors['grid_color'], alpha=0.3)
            for spine in ax.spines.values():
                spine.set_color(self.colors['text_color'])
        
        # Convert timestamps to datetime with error handling
        x_data = []
        for ts in timestamps:
            try:
                if isinstance(ts, (int, float)) and ts > 0:
                    x_data.append(datetime.fromtimestamp(ts))
                else:
                    # If timestamp is invalid, use index instead
                    break
            except (ValueError, OSError, OverflowError):
                # If conversion fails, use index instead
                break
        
        # If timestamp conversion failed, use index-based plotting
        if len(x_data) == 0 or len(x_data) != len(timestamps):
            print(f"Warning: Timestamp conversion failed. Using index-based plotting.")
            print(f"Sample timestamps: {timestamps[:5] if len(timestamps) > 0 else 'Empty'}")
            x_data = list(range(len(timestamps)))
            use_datetime_format = False
        else:
            use_datetime_format = True
        
        # Plot each panel
        for panel_idx, panel in enumerate(panels):
            if panel_idx >= len(self.axes):
                print(f"Warning: Panel {panel_idx} skipped - not enough axes")
                continue
                
            ax = self.axes[panel_idx]
            panel_data = panel.get('series_data', {})
            panel_title = panel.get('title', f'Panel {panel_idx}')
            
            color_index = 0
            
            # Plot all series in this panel
            for name, data in panel_data.items():
                try:
                    if isinstance(data, dict):
                        plot_data = data.get('data', [])
                        color = data.get('color', self.colors['ma_colors'][color_index % len(self.colors['ma_colors'])])
                        linestyle = data.get('style', '-')
                        linewidth = data.get('width', 2)
                        alpha = data.get('alpha', 0.8)
                        
                        if isinstance(plot_data, (int, float)):
                            ax.axhline(y=plot_data, color=color, linestyle=linestyle, 
                                     linewidth=linewidth, alpha=alpha, label=name)
                        elif isinstance(plot_data, (np.ndarray, list)) and len(plot_data) > 0:
                            if isinstance(plot_data, np.ndarray):
                                valid_mask = ~np.isnan(plot_data)
                                valid_x = [x_data[i] for i, v in enumerate(valid_mask) if v and i < len(x_data)]
                                valid_y = plot_data[valid_mask]
                            else:
                                valid_x = x_data[:len(plot_data)]
                                valid_y = plot_data
                            
                            ax.plot(valid_x, valid_y, color=color, linestyle=linestyle,
                                  linewidth=linewidth, alpha=alpha, label=name)
                    
                    elif isinstance(data, (int, float)):
                        color = self.colors['ma_colors'][color_index % len(self.colors['ma_colors'])]
                        ax.axhline(y=data, color=color, linestyle='--', linewidth=2, 
                                 alpha=0.8, label=name)
                    
                    elif isinstance(data, (np.ndarray, list)) and len(data) > 0:
                        color = self.colors['ma_colors'][color_index % len(self.colors['ma_colors'])]
                        
                        if isinstance(data, np.ndarray):
                            valid_mask = ~np.isnan(data)
                            valid_x = [x_data[i] for i, v in enumerate(valid_mask) if v and i < len(x_data)]
                            valid_y = data[valid_mask]
                        else:
                            valid_x = x_data[:len(data)]
                            valid_y = data
                        
                        ax.plot(valid_x, valid_y, color=color, linewidth=2, 
                              alpha=0.8, label=name)
                    
                    color_index += 1
                    
                except Exception as e:
                    print(f"Warning: Could not plot panel {panel_idx} series '{name}': {e}")
                    continue
            
            # Set panel labels and title
            ax.set_title(panel_title, color=self.colors['text_color'], fontsize=14, fontweight='bold')
            ax.set_ylabel('Value', color=self.colors['text_color'])
            
            # Add legend only if there are labeled artists
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend(loc='upper left', framealpha=0.8,
                        facecolor=self.colors['bg_color'],
                        edgecolor=self.colors['text_color'],
                        labelcolor=self.colors['text_color'])
            
            # Add x-axis label only to the bottom panel
            if panel_idx == len(panels) - 1:
                ax.set_xlabel('Time', color=self.colors['text_color'])
        
        # Format x-axis for all panels
        from matplotlib.ticker import MaxNLocator
        
        data_length = len(x_data)
        if data_length > 1000:
            max_ticks = 10
            date_format = '%m/%d'
        elif data_length > 500:
            max_ticks = 15
            date_format = '%m/%d %H:%M'
        elif data_length > 100:
            max_ticks = 20
            date_format = '%m/%d %H:%M'
        else:
            max_ticks = 30
            date_format = '%H:%M'
        
        # Format x-axis based on whether we're using datetime or index
        if use_datetime_format:
            for ax in self.axes:
                ax.xaxis.set_major_locator(MaxNLocator(nbins=max_ticks, prune='both'))
                ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        else:
            # Index-based formatting
            for ax in self.axes:
                ax.xaxis.set_major_locator(MaxNLocator(nbins=max_ticks, prune='both'))
                # No rotation needed for index labels
        
        # Hide x-axis labels for all panels except the bottom one
        for i, ax in enumerate(self.axes[:-1]):  # All except last
            plt.setp(ax.xaxis.get_majorticklabels(), visible=False)
        
        # Add interactive features (crosshair, zoom, etc.)
        self._setup_interactive_features()
        
        # Implement synchronized zoom if requested
        if synchronized_zoom:
            self._setup_synchronized_zoom()
        
        print(f"Multi-panel chart created with {panel_count} panels")
        if synchronized_zoom:
            print("- Synchronized zoom enabled")
        print("- Interactive features enabled (crosshair, wheel zoom)")
        
        # Layout is handled by constrained_layout=True in subplot creation
        # No need for manual tight_layout calls

    def _setup_synchronized_zoom(self) -> None:
        """
        Setup synchronized zoom functionality between panels.
        """
        if len(self.axes) < 2:
            return
        
        # Store original limits for reset functionality
        self._original_xlims = [ax.get_xlim() for ax in self.axes]
        self._original_ylims = [ax.get_ylim() for ax in self.axes]
        
        def sync_x_zoom(event_ax):
            """Synchronize X-axis zoom across all panels"""
            if event_ax in self.axes:
                xlim = event_ax.get_xlim()
                for ax in self.axes:
                    if ax != event_ax:
                        ax.set_xlim(xlim)
                self.fig.canvas.draw_idle()
        
        def on_xlims_change(ax):
            """Callback for X-axis limit changes"""
            sync_x_zoom(ax)
        
        # Connect X-axis synchronization for all axes
        for ax in self.axes:
            ax.callbacks.connect('xlim_changed', lambda ax_instance: on_xlims_change(ax_instance))
        
        # Enhanced scroll zoom with synchronization
        def on_scroll(event):
            if event.inaxes is None or event.inaxes not in self.axes:
                return
            
            ax = event.inaxes
            x_center = event.xdata
            if x_center is None:
                return
            
            # Get current X-axis limits
            x_min, x_max = ax.get_xlim()
            
            # Zoom factor
            zoom_factor = 1.2 if event.button == 'down' else 1/1.2
            
            # Calculate new X limits (only sync X-axis)
            x_range = (x_max - x_min) * zoom_factor
            new_x_min = x_center - x_range/2
            new_x_max = x_center + x_range/2
            
            # Apply X zoom to all axes (synchronized)
            for sync_ax in self.axes:
                sync_ax.set_xlim(new_x_min, new_x_max)
            
            # Apply Y zoom only to the current axis
            if event.ydata is not None:
                y_center = event.ydata
                y_min, y_max = ax.get_ylim()
                y_range = (y_max - y_min) * zoom_factor
                new_y_min = y_center - y_range/2
                new_y_max = y_center + y_range/2
                ax.set_ylim(new_y_min, new_y_max)
            
            self.fig.canvas.draw()
        
        # Connect scroll event
        self.fig.canvas.mpl_connect('scroll_event', on_scroll)
        
        # Enhanced pan functionality with synchronization
        self._pan_start = None
        
        def on_press(event):
            if event.inaxes in self.axes and event.button == 1:  # Left mouse button
                self._pan_start = {
                    'x': event.xdata,
                    'xlims': [ax.get_xlim() for ax in self.axes],
                    'ylim': event.inaxes.get_ylim(),
                    'ax': event.inaxes
                }
        
        def on_motion(event):
            if self._pan_start is None or event.inaxes != self._pan_start['ax']:
                return
            
            if event.xdata is None or event.ydata is None:
                return
            
            # Calculate X displacement (synchronized)
            dx = event.xdata - self._pan_start['x']
            
            # Apply X pan to all axes
            for i, ax in enumerate(self.axes):
                old_xlim = self._pan_start['xlims'][i]
                new_xlim = (old_xlim[0] - dx, old_xlim[1] - dx)
                ax.set_xlim(new_xlim)
            
            # Apply Y pan only to current axis
            if event.ydata is not None:
                dy = event.ydata - self._pan_start.get('y', event.ydata)
                ax = self._pan_start['ax']
                old_ylim = self._pan_start['ylim']
                new_ylim = (old_ylim[0] - dy, old_ylim[1] - dy)
                ax.set_ylim(new_ylim)
            
            self.fig.canvas.draw_idle()
        
        def on_release(event):
            self._pan_start = None
        
        # Connect pan events
        self.fig.canvas.mpl_connect('button_press_event', on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', on_motion)
        self.fig.canvas.mpl_connect('button_release_event', on_release)
        
        # Add reset zoom functionality with double-click
        def on_double_click(event):
            if event.inaxes in self.axes and event.dblclick:
                # Reset to original limits
                for i, ax in enumerate(self.axes):
                    if i < len(self._original_xlims):
                        ax.set_xlim(self._original_xlims[i])
                    if i < len(self._original_ylims):
                        ax.set_ylim(self._original_ylims[i])
                self.fig.canvas.draw()
        
        # Connect double-click reset
        self.fig.canvas.mpl_connect('button_press_event', on_double_click)
        
        print("Synchronized dual-panel mode enabled:")
        print("- Mouse wheel: Zoom in/out (X-axis synchronized, Y-axis independent)")
        print("- Left mouse drag: Pan (X-axis synchronized, Y-axis independent)")
        print("- Double-click: Reset zoom to original view")
        print("- Toolbar: Additional navigation controls")

    def _setup_interactive_features(self) -> None:
        """
        Setup interactive features like crosshair cursor and individual axis zoom.
        """
        if self.fig is None or len(self.axes) == 0:
            return
        
        # Enable matplotlib toolbar
        import matplotlib.pyplot as plt
        plt.rcParams['toolbar'] = 'toolbar2'
        
        # Store crosshair lines for cleanup
        self._crosshair_lines = []
        
        # Add crosshair cursor functionality
        def on_mouse_move(event):
            if event.inaxes is None or event.inaxes not in self.axes:
                return
                
            # Remove previous crosshair lines
            for line in self._crosshair_lines:
                try:
                    line.remove()
                except:
                    pass
            self._crosshair_lines.clear()
            
            # Add crosshair to current axis
            ax = event.inaxes
            if event.xdata is not None and event.ydata is not None:
                # Vertical line (across all panels with same X)
                for panel_ax in self.axes:
                    try:
                        vline = panel_ax.axvline(x=event.xdata, color='gray', 
                                               linestyle='--', alpha=0.5, linewidth=1)
                        self._crosshair_lines.append(vline)
                    except:
                        pass
                
                # Horizontal line (only on current panel)
                try:
                    hline = ax.axhline(y=event.ydata, color='gray', 
                                     linestyle='--', alpha=0.5, linewidth=1)
                    self._crosshair_lines.append(hline)
                except:
                    pass
                
                # Update canvas
                self.fig.canvas.draw_idle()
        
        # Connect mouse move event for crosshair
        self.fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)
        
        # Individual axis scroll zoom (without synchronization)
        def on_scroll_individual(event):
            if event.inaxes is None or event.inaxes not in self.axes:
                return
            
            ax = event.inaxes
            x_center = event.xdata
            y_center = event.ydata
            
            if x_center is None or y_center is None:
                return
            
            # Get current axis limits
            x_min, x_max = ax.get_xlim()
            y_min, y_max = ax.get_ylim()
            
            # Zoom factor
            zoom_factor = 1.2 if event.button == 'down' else 1/1.2
            
            # Calculate new limits
            x_range = (x_max - x_min) * zoom_factor
            y_range = (y_max - y_min) * zoom_factor
            
            new_x_min = x_center - x_range/2
            new_x_max = x_center + x_range/2
            new_y_min = y_center - y_range/2
            new_y_max = y_center + y_range/2
            
            # Apply new limits only to current axis
            ax.set_xlim(new_x_min, new_x_max)
            ax.set_ylim(new_y_min, new_y_max)
            
            # Redraw
            self.fig.canvas.draw_idle()
        
        # Store the individual scroll function for potential future use
        self._individual_scroll_func = on_scroll_individual
        
        print("Individual interactive features enabled:")
        print("- Crosshair cursor: Shows position across all panels")
        print("- Mouse hover: Real-time crosshair tracking")

    def __repr__(self) -> str:
        """String representation of the plotter."""
        subplot_count = len(self.axes) if self.axes else 0
        return f"DataPlotter(style='{self.style}', subplots={subplot_count}, figsize={self.figsize})"