import pandas as pd
from lightweight_charts import Chart
from datetime import datetime

class DataPlotter2:
    def __init__(self):
        self.trader_data = None
        self.full_df = None      # Complete trader data DataFrame
        self.chart_df = None     # Chart-optimized DataFrame (time|open|high|low|close|volume)
        self.custom_series = {}  # For custom data series
        self.panel_series = {}   # Panel assignments: {series_name: panel_id}
        self.panels = {}         # Panel information: {panel_id: {'series': [series_names], 'chart': chart_object}}

    def Clear(self):
        self.ClearData()

    def ClearData(self):
        self.full_df = None
        self.chart_df = None
        self.custom_series = {}
        self.panel_series = {}
        self.panels = {}

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

    def GetFullData(self):
        return self.full_df

    def GetChartData(self):
        return self.chart_df

    def AddYData(self, series_id, data_list, series_name):
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
        # Do not automatically assign to panel - require explicit registration
        print(f"DEBUG: Added custom series '{series_name}'. Use RegisterDataSeriesToPanel() to display it.")

    def RegisterDataSeriesToPanel(self, series_name, panel_id):
        """
        Assigns a data series to a specific panel.
        series_name: The name of the data series
        panel_id: Panel ID (0=main chart, 1,2,3...=subcharts)
        """
        if series_name not in self.custom_series:
            print(f"WARNING: Series '{series_name}' not found. Add it first with AddYData().")
            return

        self.panel_series[series_name] = panel_id

        # Initialize panel info if needed
        if panel_id not in self.panels:
            self.panels[panel_id] = {'series': [], 'chart': None}

        # Add series to panel if not already there
        if series_name not in self.panels[panel_id]['series']:
            self.panels[panel_id]['series'].append(series_name)

        print(f"DEBUG: Registered series '{series_name}' to panel {panel_id}")

    def Show(self):
        """
        Display the chart using lightweight-charts with panel-based rendering.
        Panel 0: Main OHLC chart with overlays
        Panel 1+: Subcharts below the main chart
        """
        try:
            if self.chart_df is None or self.chart_df.empty:
                print("ERROR: No chart data to display. Call SetData() first.")
                return

            # Calculate dynamic panel sizes based on number of panels
            unique_panels = set(self.panel_series.values()) if self.panel_series else {0}
            num_panels = len(unique_panels)

            # Dynamic height calculation: main panel gets more space
            if num_panels == 1:
                main_height = 1.0
            else:
                main_height = 0.4
                sub_height = 0.6 / (num_panels - 1) if num_panels > 1 else 0.2

            # Create main chart (Panel 0)
            chart = Chart(inner_width=0.9, inner_height=main_height)
            chart.legend(visible=True, font_size=16)
            # chart.grid(False, False)
            chart.set(self.chart_df)
            self.panels[0] = {'series': [], 'chart': chart}

            # Create subcharts for panels 1, 2, 3, etc.
            sorted_panels = sorted([p for p in unique_panels if p > 0])
            subcharts = {}

            for panel_id in sorted_panels:
                subchart = chart.create_subchart(position='bottom', width=0.9, height=sub_height, sync=True)
                subchart.legend(visible=True, font_size=16)
                subcharts[panel_id] = subchart
                if panel_id not in self.panels:
                    self.panels[panel_id] = {'series': [], 'chart': subchart}
                else:
                    self.panels[panel_id]['chart'] = subchart

            # Add series to their respective panels - only plot explicitly registered series
            registered_series = {name for name in self.custom_series.keys()
                                if name in self.panel_series}

            for series_name in registered_series:
                data = self.custom_series[series_name]
                panel_id = self.panel_series[series_name]

                if panel_id == 0:
                    # Add to main chart as overlay
                    line = chart.create_line(name=series_name)
                    line_df = pd.DataFrame({
                        'time': self.chart_df['time'],
                        series_name: data
                    })
                    line.set(line_df)
                    print(f"DEBUG: Added series '{series_name}' to main panel (Panel 0)")

                elif panel_id in subcharts:
                    # Add to subchart
                    subchart = subcharts[panel_id]
                    line = subchart.create_line(name=series_name)
                    line_df = pd.DataFrame({
                        'time': self.chart_df['time'],
                        series_name: data
                    })
                    line.set(line_df)
                    print(f"DEBUG: Added series '{series_name}' to Panel {panel_id}")
                else:
                    print(f"WARNING: Panel {panel_id} not found for series '{series_name}'")

            print(f"DEBUG: Displaying chart with {num_panels} panels...")
            chart.show(block=True)

        except Exception as e:
            print(f"ERROR in Show: {e}")
            import traceback
            traceback.print_exc()
    
    def ClearYData(self, series_id=None, series_name=None):
        """
        Clear Y data series based on series_id, series_name, or all data if no parameters provided.

        Args:
            series_id: Integer identifier for the series (for compatibility)
            series_name: String name of the series to clear
        """
        if series_id is not None and series_name is not None:
            # Both provided, prioritize series_name but check series_id for compatibility
            if series_name in self.custom_series:
                del self.custom_series[series_name]
                print(f"DEBUG: Cleared series '{series_name}' (ID: {series_id})")
            else:
                print(f"Warning: Series '{series_name}' not found")

        elif series_id is not None:
            # Only series_id provided - find and clear by ID
            # Since we don't store series_id directly, we need to match by position or convention
            series_names = list(self.custom_series.keys())
            if 0 <= series_id < len(series_names):
                series_name = series_names[series_id]
                del self.custom_series[series_name]
                print(f"DEBUG: Cleared series '{series_name}' by ID {series_id}")
            else:
                print(f"Warning: Series ID {series_id} not found")

        elif series_name is not None:
            # Only series_name provided
            if series_name in self.custom_series:
                del self.custom_series[series_name]
                print(f"DEBUG: Cleared series '{series_name}'")
            else:
                print(f"Warning: Series '{series_name}' not found")

        else:
            # No parameters - clear all Y data series
            cleared_count = len(self.custom_series)
            self.custom_series.clear()
            print(f"DEBUG: Cleared all {cleared_count} Y data series")


