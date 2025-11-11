import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
import pandas as pd
from datetime import datetime

# Configure plotly to work offline and avoid PyCharm issues
pyo.init_notebook_mode(connected=False)

class DataPlotter3:
    def __init__(self):
        self.trader = None
        self.full_df = None
        self.custom_series = {}
        self.series_panels = {}  # {series_name: panel_id}
        self.line_properties = {}  # {series_name: {'color': 'color', 'lineWidth': width}}
        self.title = ""
        self.fig = None
        self.panel_count = 4  # Default to 4 panels like DataPlotter2
        
    def Clear(self):
        self.ClearData()
        
    def ClearData(self):
        self.trader = None
        self.full_df = None
        self.custom_series = {}
        self.series_panels = {}
        self.line_properties = {}
        self.title = ""
        self.fig = None
        
    def SetData(self, trader):
        """Set trader data and create base DataFrame"""
        self.trader = trader
        self._create_full_dataframe()
        
    def _create_full_dataframe(self):
        """Create full DataFrame with OHLCV data"""
        try:
            data_length = len(self.trader.Close) if hasattr(self.trader, 'Close') else 0
            if data_length == 0:
                print("ERROR: No Close data found in trader object")
                return
                
            # Create time array
            if hasattr(self.trader, 'Time') and len(self.trader.Time) > 0:
                time_array = self.trader.Time
            else:
                # Create simple index-based time array
                time_array = list(range(data_length))
                
            # Get OHLCV data
            open_data = getattr(self.trader, 'Open', [self.trader.Close[0]] * data_length)
            high_data = getattr(self.trader, 'High', self.trader.Close)
            low_data = getattr(self.trader, 'Low', self.trader.Close)
            close_data = self.trader.Close
            volume_data = getattr(self.trader, 'Volume', [0] * data_length)
            
            # Ensure all arrays have same length
            min_length = min(len(time_array), len(open_data), len(high_data), 
                           len(low_data), len(close_data), len(volume_data))
                           
            self.full_df = pd.DataFrame({
                'time': time_array[:min_length],
                'open': open_data[:min_length],
                'high': high_data[:min_length],
                'low': low_data[:min_length],
                'close': close_data[:min_length],
                'volume': volume_data[:min_length]
            })
            
            print(f"DataFrame created with {len(self.full_df)} records")
            
        except Exception as e:
            print(f"Error creating DataFrame: {e}")
            
    def SetTitle(self, title):
        """Set chart title"""
        self.title = title
        
    def AddYData(self, series_id, data, series_name):
        """Add custom data series"""
        if len(data) > 0:
            self.custom_series[series_name] = data
            
    def RegisterDataSeriesToPanel(self, series_name, panel_id):
        """Register data series to specific panel"""
        self.series_panels[series_name] = panel_id
        
    def SetLineProperties(self, series_name, color=None, lineWidth=1):
        """Set line properties for a series"""
        if series_name not in self.line_properties:
            self.line_properties[series_name] = {}
        if color:
            self.line_properties[series_name]['color'] = color
        self.line_properties[series_name]['lineWidth'] = lineWidth
        
    def plotDataPlotly(self, trader, max_points=10000):
        """Main plotting method using Plotly based on plotDataFinal
        
        Args:
            trader: Trading data object
            max_points: Maximum number of points to display for performance (default: 10000)
        """
        
        # Time array boşsa, basit index array oluştur
        if len(self.trader.Time) == 0:
            print("=== WARNING: Time array boş! Index array oluşturuluyor ===")
            time_array = list(range(len(self.trader.Close)))
        else:
            time_array = self.trader.Time

        # Performance optimization: Downsample data if too large
        data_length = len(self.trader.Close)
        if data_length > max_points:
            print(f"=== PERFORMANCE: Downsampling from {data_length} to {max_points} points ===")
            # Calculate step size for downsampling
            step = max(1, data_length // max_points)
            
            # Downsample all arrays
            time_array = time_array[::step]
            trader_close = self.trader.Close[::step]
            trader_open = getattr(self.trader, 'Open', self.trader.Close)[::step] if hasattr(self.trader, 'Open') else trader_close
            trader_high = getattr(self.trader, 'High', self.trader.Close)[::step] if hasattr(self.trader, 'High') else trader_close
            trader_low = getattr(self.trader, 'Low', self.trader.Close)[::step] if hasattr(self.trader, 'Low') else trader_close
            
            # Downsample moving averages if they exist
            ma5_data = self.trader.Ma5[::step] if hasattr(self.trader, 'Ma5') and len(self.trader.Ma5) > 0 else []
            ma8_data = self.trader.Ma8[::step] if hasattr(self.trader, 'Ma8') and len(self.trader.Ma8) > 0 else []
            ma13_data = self.trader.Ma13[::step] if hasattr(self.trader, 'Ma13') and len(self.trader.Ma13) > 0 else []
            ma21_data = self.trader.Ma21[::step] if hasattr(self.trader, 'Ma21') and len(self.trader.Ma21) > 0 else []
            ma50_data = self.trader.Ma50[::step] if hasattr(self.trader, 'Ma50') and len(self.trader.Ma50) > 0 else []
            ma100_data = self.trader.Ma100[::step] if hasattr(self.trader, 'Ma100') and len(self.trader.Ma100) > 0 else []
            ma200_data = self.trader.Ma200[::step] if hasattr(self.trader, 'Ma200') and len(self.trader.Ma200) > 0 else []
            most_data = self.trader.Most[::step] if hasattr(self.trader, 'Most') and len(self.trader.Most) > 0 else []
            exmov_data = self.trader.ExMov[::step] if hasattr(self.trader, 'ExMov') and len(self.trader.ExMov) > 0 else []
        else:
            # Use full data
            trader_close = self.trader.Close
            trader_open = getattr(self.trader, 'Open', self.trader.Close)
            trader_high = getattr(self.trader, 'High', self.trader.Close)
            trader_low = getattr(self.trader, 'Low', self.trader.Close)
            
            ma5_data = getattr(self.trader, 'Ma5', [])
            ma8_data = getattr(self.trader, 'Ma8', [])
            ma13_data = getattr(self.trader, 'Ma13', [])
            ma21_data = getattr(self.trader, 'Ma21', [])
            ma50_data = getattr(self.trader, 'Ma50', [])
            ma100_data = getattr(self.trader, 'Ma100', [])
            ma200_data = getattr(self.trader, 'Ma200', [])
            most_data = getattr(self.trader, 'Most', [])
            exmov_data = getattr(self.trader, 'ExMov', [])

        LevelZero1 = self.create_level_series(len(self.trader.Close), 0)
        LevelZero2 = self.create_level_series(len(self.trader.Close), 0)

        balance = trader.Lists.BakiyeFiyatList
        bakiye = trader.Lists.BakiyeFiyatList

        getiriFiyatList = trader.Lists.GetiriFiyatList
        getiriFiyatNetList = trader.Lists.GetiriFiyatNetList

        getiriKz = trader.Lists.GetiriKz
        getiriKzNet = trader.Lists.GetiriKzNet

        karZararPuanList = trader.Lists.KarZararPuanList
        karZararFiyatList = trader.Lists.KarZararFiyatList

        # Calculate additional data
        farkList = [0.0] * len(trader.Lists.BakiyeFiyatList)
        for i in range(len(trader.Lists.BakiyeFiyatList)):
            farkList[i] = trader.Lists.BakiyeFiyatList[i] - trader.Lists.GetiriFiyatList[i]

        farkList2 = [0.0] * len(trader.Lists.GetiriKz)
        for i in range(len(trader.Lists.GetiriKz)):
            farkList2[i] = trader.Lists.GetiriKz[i] - trader.Lists.GetiriKzNet[i]

        print(f"farkList: {farkList[-1] if farkList else 'Empty'}")
        print(f"farkList2: {farkList2[-1] if farkList2 else 'Empty'}")

        print("=== plotDataPlotly başlıyor ===")
        
        # Create subplot with 4 panels
        self.fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            row_heights=[0.4, 0.2, 0.2, 0.2],
            subplot_titles=('Price & Indicators', 'Trading Signals', 'P&L', 'Returns')
        )

        # Panel 0: Main price chart with candlesticks
        candlestick = go.Candlestick(
            x=time_array,
            open=trader_open,
            high=trader_high,
            low=trader_low,
            close=trader_close,
            name="OHLC"
        )
        self.fig.add_trace(candlestick, row=1, col=1)

        # Add Moving Averages to main panel
        if len(ma5_data) > 0:
            self.fig.add_trace(go.Scatter(x=time_array, y=ma5_data, name='MA5', 
                                        line=dict(color='blue', width=2)), row=1, col=1)
        if len(ma8_data) > 0:
            self.fig.add_trace(go.Scatter(x=time_array, y=ma8_data, name='MA8', 
                                        line=dict(color='green', width=2)), row=1, col=1)
        if len(ma13_data) > 0:
            self.fig.add_trace(go.Scatter(x=time_array, y=ma13_data, name='MA13', 
                                        line=dict(color='purple', width=2)), row=1, col=1)
        if len(ma21_data) > 0:
            self.fig.add_trace(go.Scatter(x=time_array, y=ma21_data, name='MA21', 
                                        line=dict(color='red', width=2)), row=1, col=1)
        if len(ma50_data) > 0:
            self.fig.add_trace(go.Scatter(x=time_array, y=ma50_data, name='MA50', 
                                        line=dict(color='orange', width=2)), row=1, col=1)
        if len(ma100_data) > 0:
            self.fig.add_trace(go.Scatter(x=time_array, y=ma100_data, name='MA100', 
                                        line=dict(color='brown', width=2)), row=1, col=1)
        if len(ma200_data) > 0:
            self.fig.add_trace(go.Scatter(x=time_array, y=ma200_data, name='MA200', 
                                        line=dict(color='orange', width=3)), row=1, col=1)
        
        # Add other indicators
        if len(most_data) > 0:
            self.fig.add_trace(go.Scatter(x=time_array, y=most_data, name='Most', 
                                        line=dict(color='cyan', width=1)), row=1, col=1)
        if len(exmov_data) > 0:
            self.fig.add_trace(go.Scatter(x=time_array, y=exmov_data, name='ExMov', 
                                        line=dict(color='magenta', width=1)), row=1, col=1)

        # Panel 1: Trading Signals
        if hasattr(trader, 'combined_data_normalized') and len(trader.combined_data_normalized) > 0:
            self.fig.add_trace(go.Scatter(x=time_array, y=trader.combined_data_normalized, name='TradingSignals', 
                                        line=dict(color='cyan', width=1)), row=2, col=1)
        
        self.fig.add_trace(go.Scatter(x=time_array, y=LevelZero1, name='LevelZero1', 
                                    line=dict(color='red', width=1)), row=2, col=1)

        # Panel 2: P&L Data
        self.fig.add_trace(go.Scatter(x=time_array, y=LevelZero2, name='LevelZero2', 
                                    line=dict(color='red', width=1)), row=3, col=1)
        self.fig.add_trace(go.Scatter(x=time_array, y=karZararFiyatList, name='karZararFiyatList', 
                                    line=dict(color='blue', width=1)), row=3, col=1)

        # Panel 3: Returns
        self.fig.add_trace(go.Scatter(x=time_array, y=getiriFiyatNetList, name='getiriFiyatNetList', 
                                    line=dict(color='green', width=1)), row=4, col=1)

        # Update layout
        self.fig.update_layout(
            title=self.title if self.title else "Trading Chart",
            xaxis_rangeslider_visible=True,  # Rangeslider'ı aktif et
            height=800,
            showlegend=True,
            # Performance optimizations for large datasets
            xaxis=dict(
                rangeslider=dict(
                    visible=True,
                    thickness=0.1  # Rangeslider kalınlığı
                ),
                type='linear'
            ),
            # Reduce rendering complexity
            dragmode='zoom',
            hovermode='x unified'
        )

        print("=== plotDataPlotly bitti ===")
        
    def create_level_series(self, length, level):
        """Create a horizontal line at specified level"""
        return [level] * length
        
    def Show(self):
        """Display the chart"""
        if self.fig:
            try:
                # Try to show in browser instead of PyCharm to avoid HTTP 500 error
                import plotly.offline as pyo
                
                # Performance optimization for chart display
                config = {
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['pan2d', 'lasso2d'],
                    'responsive': True,
                    'scrollZoom': True,
                    'doubleClick': 'reset+autosize'
                }
                
                # Force browser display to avoid PyCharm internal server issues
                pyo.plot(self.fig, config=config, auto_open=True)
                print("Chart opened in web browser")
                
            except Exception as e:
                print(f"Error showing chart in browser: {e}")
                # Fallback to default show
                try:
                    self.fig.show()
                except Exception as e2:
                    print(f"Error showing chart: {e2}")
                    # Save as HTML file as last resort
                    self.fig.write_html("trading_chart.html")
                    print("Chart saved as trading_chart.html")
        else:
            print("No chart to display. Call plotDataPlotly first.")