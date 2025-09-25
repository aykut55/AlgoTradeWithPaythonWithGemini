import pandas as pd
from lightweight_charts import Chart
from datetime import datetime

class DataPlotter2:
    def __init__(self):
        self.trader_data = None
        self.full_df = None      # Complete trader data DataFrame
        self.chart_df = None     # Chart-optimized DataFrame (time|open|high|low|close|volume)
        self.custom_series = {}  # For custom data series

    def ClearData(self):
        self.full_df = None
        self.chart_df = None
        self.custom_series = {}
        pass

    def _set_full_data(self, trader):
        """
        Create full DataFrame with all trader data.
        """
        try:
            data_length = len(trader.Close) if hasattr(trader, 'Close') else 0
            if data_length == 0:
                print("ERROR: No Close data found in trader object")
                return

            def get_list(attr, default, length):
                val = getattr(trader, attr, None)
                if val is not None and len(val) == length:
                    return val
                return [default] * length

            full_data = {
                'EpochTime': get_list('EpochTime', 0, data_length),
                'DateTime': get_list('DateTime', "", data_length),
                'Date': get_list('Date', "", data_length),
                'Time': get_list('Time', "", data_length),
                'Open': get_list('Open', 0.0, data_length),
                'High': get_list('High', 0.0, data_length),
                'Low': get_list('Low', 0.0, data_length),
                'Close': trader.Close,
                'Volume': get_list('Volume', 1.0, data_length),
                'Lot': get_list('Lot', 1.0, data_length),
            }
            self.full_df = pd.DataFrame(full_data)
            print(f"DEBUG: Created Full DataFrame with {len(self.full_df)} rows")
            
        except Exception as e:
            print(f"ERROR in _set_full_data: {e}")
            import traceback
            traceback.print_exc()

    def _set_chart_data(self, time_data, open_data, high_data, low_data, close_data, volume_data):
        """
        Create chart DataFrame optimized for lightweight-charts from direct data arrays.
        """
        try:
            if close_data is None or not hasattr(close_data, '__len__') or len(close_data) == 0:
                print("ERROR: No Close data found")
                self.chart_df = None
                return

            data_length = len(close_data)
            
            chart_data = {
                'time': list(time_data[:data_length]) if time_data is not None and len(time_data) >= data_length else list(range(data_length)),
                'open': list(open_data[:data_length]) if open_data is not None and len(open_data) >= data_length else [0.0] * data_length,
                'high': list(high_data[:data_length]) if high_data is not None and len(high_data) >= data_length else [0.0] * data_length,
                'low': list(low_data[:data_length]) if low_data is not None and len(low_data) >= data_length else [0.0] * data_length,
                'close': list(close_data[:data_length]),
                'volume': list(volume_data[:data_length]) if volume_data is not None and len(volume_data) >= data_length else [1.0] * data_length
            }

            self.chart_df = pd.DataFrame(chart_data)

            if pd.api.types.is_string_dtype(self.chart_df['time']):
                self.chart_df['time'] = pd.to_datetime(self.chart_df['time'], errors='coerce')

            for col in ['open', 'high', 'low', 'close', 'volume']:
                self.chart_df[col] = pd.to_numeric(self.chart_df[col], errors='coerce').fillna(0)

            print(f"DEBUG: Created Chart DataFrame with {len(self.chart_df)} rows")

        except Exception as e:
            print(f"ERROR in _set_chart_data: {e}")
            import traceback
            traceback.print_exc()
            self.chart_df = None

    def SetData(self, trader):
        """
        Set trader data for the main OHLC chart.
        """
        self.trader_data = trader
        try:
            self._set_full_data(trader)
            self._set_chart_data(trader.DateTime, trader.Open, trader.High, trader.Low, trader.Close, trader.Volume)
        except Exception as e:
            print(f"ERROR in SetData: {e}")
            import traceback
            traceback.print_exc()

    def AddData(self, series_id, data_list, series_name):
        """
        Adds a custom data series to be plotted as a line on the main chart.
        series_id: An integer identifier for the series (currently unused, for compatibility).
        data_list: The list of data points.
        series_name: The unique name for the series, used as a key and for the legend.
        """
        if self.chart_df is None:
            print("ERROR: Main chart data must be set first using SetData().")
            return
            
        if len(data_list) != len(self.chart_df):
            print(f"Warning: Length of series '{series_name}' ({len(data_list)}) does not match main chart data length ({len(self.chart_df)}). Series not added.")
            return
            
        self.custom_series[series_name] = data_list
        print(f"DEBUG: Added custom series '{series_name}'.")

    def Show(self):
        """
        Display the chart using lightweight-charts with the main data and custom series.
        """
        try:
            if self.chart_df is None or self.chart_df.empty:
                print("ERROR: No chart data to display. Call SetData() first.")
                return
                
            chart = Chart()
            chart.set(self.chart_df)
            
            # Add custom series as lines on the main chart
            for name, data in self.custom_series.items():
                line = chart.create_line(name=name)
                
                # The DataFrame passed to line.set() must contain a column with the same name as the line.
                line_df = pd.DataFrame({
                    'time': self.chart_df['time'],
                    name: data
                })
                line.set(line_df)
            
            print("DEBUG: Displaying chart...")
            chart.show(block=True)
            
        except Exception as e:
            print(f"ERROR in Show: {e}")
            import traceback
            traceback.print_exc()
    
    def GetFullData(self):
        return self.full_df
    
    def GetChartData(self):
        return self.chart_df
