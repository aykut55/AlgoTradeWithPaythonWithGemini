import pandas as pd
from lightweight_charts import Chart
from datetime import datetime

class DataPlotter2:
    def __init__(self):
        self.trader = None
        self.full_df = None      # Complete trader data DataFrame
        self.chart_df = None     # Chart-optimized DataFrame (time|open|high|low|close|volume)
        self.custom_series = {}  # For custom data series
        self.series_ids = {}     # Series ID mapping: {series_name: series_id}
        self.panel_series = {}   # Panel assignments: {series_name: panel_id}
        self.line_properties = {}  # Line properties: {series_name: {'color': '#FF0000', 'lineWidth': 2, 'lineStyle': 0}}
        self.panels = {}         # Panel information: {panel_id: {'series': [series_names], 'chart': chart_object}}
        self.title = ""          # Chart title
        self.pan_bars = 20       # Number of bars to pan left/right
        self.current_start = 0   # Current starting position
        self.visible_bars = 100  # Default number of visible bars
        self.main_chart = None   # Reference to main chart for pan operations

    def Clear(self):
        self.ClearData()

    def ClearData(self):
        self.trader = None
        self.full_df = None
        self.chart_df = None
        self.custom_series = {}
        self.series_ids = {}
        self.panel_series = {}
        self.line_properties = {}
        self.panels = {}
        self.title = ""
        self.current_start = 0
        self.main_chart = None

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
            # print(f"DEBUG: Created Full DataFrame with {len(self.full_df)} rows")
            
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

            # print(f"DEBUG: Created Chart DataFrame with {len(self.chart_df)} rows")

        except Exception as e:
            print(f"ERROR in _set_chart_data: {e}")
            import traceback
            traceback.print_exc()
            self.chart_df = None

    def SetData(self, trader):
        """
        Set trader data for the main OHLC chart.
        """
        self.trader = trader
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

    def SetTitle(self, title):
        """
        Set the chart title.
        """
        self.title = title
        # print(f"DEBUG: Chart title set to '{title}'")

    def GetTitle(self):
        """
        Get the current chart title.
        """
        return self.title


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
        self.series_ids[series_name] = series_id  # Store series_id for special handling
        # Do not automatically assign to panel - require explicit registration
        # print(f"DEBUG: Added custom series '{series_name}'. Use RegisterDataSeriesToPanel() to display it.")

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

        # print(f"DEBUG: Registered series '{series_name}' to panel {panel_id}")

    def SetLineProperties(self, series_name, color=None, lineWidth=None, lineStyle=None, lineType=None):
        """
        Set line properties for a specific data series
        
        Args:
            series_name: Name of the data series
            color: Line color (e.g., '#FF0000', 'red', 'green')
            lineWidth: Line thickness (1-10)
            lineStyle: Line style (0=solid, 1=dotted, 2=dashed)
            lineType: Chart type ('line', 'area', 'histogram')
        """
        if series_name not in self.line_properties:
            self.line_properties[series_name] = {}
        
        if color is not None:
            self.line_properties[series_name]['color'] = color
        if lineWidth is not None:
            self.line_properties[series_name]['lineWidth'] = lineWidth
        if lineStyle is not None:
            self.line_properties[series_name]['lineStyle'] = lineStyle
        if lineType is not None:
            self.line_properties[series_name]['lineType'] = lineType
            
        print(f"DEBUG: Set line properties for '{series_name}': {self.line_properties[series_name]}")

    def ShowTradingSignals(self, tradingSignals, tradingSignalsInfo, panelNo=0):
        """
        Create trading signals visualization from trader's YönList and SeviyeList
        Displays buy/sell signal segments on the main chart with segment-based coloring
        """

        # Add Trading Signals to chart
        self.AddYData(series_id=1000, data_list=tradingSignals, series_name="Trading Signals")
        self.RegisterDataSeriesToPanel("Trading Signals", panel_id=panelNo)
        self.tradingSignals = tradingSignals
        self.tradingSignalsInfo = tradingSignalsInfo

        self.SetLineProperties("Trading Signals", color='red', lineWidth=2)

        # Create segment-based colored series for A (Buy) and S (Sell) signals
        # self._createSegmentColoredSeries(panelNo)

        # Create individual marker series for each signal change (as fallback approach)
        # self._createMarkerSeries(panelNo)

        print("DEBUG: Trading signals added successfully with segment-based coloring")

    def _createSegmentColoredSeries(self, panelNo):
        """
        Add signal change markers (A, S, F) as text annotations on chart
        """
        try:
            if not hasattr(self, 'tradingSignalsInfo') or not self.tradingSignalsInfo:
                print("WARNING: No tradingSignalsInfo available for segment coloring")
                return
            
            # Store text markers for plotting
            self.signal_markers = []
            
            # Process each segment to find signal changes
            for segment in self.tradingSignalsInfo:
                start_idx = segment.get("start", 0)
                direction = segment.get("direction", "")
                level = segment.get("level", 0)
                
                # Determine marker text
                marker_text = ""
                if direction == "BUY" or direction == "A":
                    marker_text = "A"
                elif direction == "SELL" or direction == "S":
                    marker_text = "S"
                elif direction == "FLAT" or direction == "F":
                    marker_text = "F"
                else:
                    continue
                
                # Store marker info for later use in Show()
                marker_info = {
                    'index': start_idx,
                    'text': marker_text,
                    'level': level if level != 0 else (self.tradingSignals[start_idx] if start_idx < len(self.tradingSignals) and self.tradingSignals[start_idx] is not None else 0)
                }
                self.signal_markers.append(marker_info)
                
                print(f"DEBUG: Added marker '{marker_text}' at index {start_idx}, level {marker_info['level']}")
                
        except Exception as e:
            print(f"ERROR in _createSegmentColoredSeries: {e}")
            import traceback
            traceback.print_exc()

    def _createMarkerSeries(self, panelNo):
        """
        Create visible marker series for signal changes - each marker as a single point
        """
        try:
            if not hasattr(self, 'tradingSignalsInfo') or not self.tradingSignalsInfo:
                return
            
            for idx, segment in enumerate(self.tradingSignalsInfo):
                start_idx = segment.get("start", 0)
                direction = segment.get("direction", "")
                level = segment.get("level", 0)
                
                # Skip if no valid direction
                if direction not in ["BUY", "A", "SELL", "S", "FLAT", "F"]:
                    continue
                    
                # Get marker level 
                marker_level = level
                if marker_level == 0 and start_idx < len(self.tradingSignals):
                    marker_level = self.tradingSignals[start_idx]
                if marker_level is None:
                    marker_level = self.chart_df['close'].iloc[start_idx] if start_idx < len(self.chart_df) else 0
                
                # Create single point series for the marker
                marker_data = [None] * len(self.tradingSignals)
                marker_data[start_idx] = marker_level
                
                # Determine marker properties
                marker_text = direction[0] if len(direction) > 0 else "?"  # A, S, F etc
                
                if direction in ["BUY", "A"]:
                    color = '#00FF00'  # Green
                elif direction in ["SELL", "S"]:
                    color = '#FF0000'  # Red
                else:
                    color = '#0000FF'  # Blue for other signals
                
                # Add marker series
                series_name = f"Signal_{marker_text}_{idx}"
                self.AddYData(series_id=5000 + idx, data_list=marker_data, series_name=series_name)
                self.RegisterDataSeriesToPanel(series_name, panel_id=panelNo)
                self.SetLineProperties(series_name, color=color, lineWidth=5)  # Thick point
                
                print(f"DEBUG: Added marker series '{series_name}' at index {start_idx}, level {marker_level}")
                
        except Exception as e:
            print(f"ERROR in _createMarkerSeries: {e}")
            import traceback
            traceback.print_exc()

    def get_signal_segments(self):
        """
        Create signal segments from YonList and SeviyeList
        Returns list of segments with start, end, level, and direction
        """
        segments = []
        current_direction = None
        current_level = None
        segment_start = None
        
        for i, (yon, seviye) in enumerate(zip(self.YonList, self.SeviyeList)):
            # String değerleri doğru şekilde çevir: 'A' = Buy, 'S' = Sell
            if yon == 'A':
                yon_val = 1  # Buy signal
            elif yon == 'S':
                yon_val = -1  # Sell signal  
            else:
                yon_val = 0  # No signal
                
            try:
                seviye_val = float(seviye) if seviye != 0 else 0
            except (ValueError, TypeError):
                seviye_val = 0
                
            if yon_val != 0:  # Signal var
                direction = "BUY" if yon_val == 1 else "SELL"
                level = seviye_val if seviye_val != 0 else self.chart_df['close'].iloc[i]
                
                if current_direction != direction or current_level != level:
                    # Önceki segmenti bitir
                    if current_direction is not None and segment_start is not None:
                        segments.append({
                            "start": segment_start,
                            "end": i - 1,
                            "level": current_level,
                            "direction": current_direction
                        })
                    
                    # Yeni segment başlat
                    current_direction = direction
                    current_level = level
                    segment_start = i
            else:  # Signal yok
                if current_direction is not None and segment_start is not None:
                    # Mevcut segmenti bitir
                    segments.append({
                        "start": segment_start,
                        "end": i - 1,
                        "level": current_level,
                        "direction": current_direction
                    })
                    current_direction = None
                    current_level = None
                    segment_start = None
        
        # Son segmenti bitir
        if current_direction is not None and segment_start is not None:
            segments.append({
                "start": segment_start,
                "end": len(self.YonList) - 1,
                "level": current_level,
                "direction": current_direction
            })
        
        return segments

    def leftPan(self, chart):
        """
        Pan chart to the left by pan_bars amount
        """
        try:
            if self.chart_df is None or len(self.chart_df) == 0:
                print("ERROR: No chart data available for panning")
                return
            
            total_bars = len(self.chart_df)
            self.current_start = max(0, self.current_start - self.pan_bars)
            
            end_index = min(self.current_start + self.visible_bars, total_bars)
            
            if self.current_start < total_bars:
                chart.time_scale().set_visible_range({
                    'from': self.chart_df['time'].iloc[self.current_start],
                    'to': self.chart_df['time'].iloc[end_index - 1]
                })
                print(f"DEBUG: Panned left - showing bars {self.current_start} to {end_index - 1}")
            
        except Exception as e:
            print(f"ERROR: Left pan failed: {e}")

    def rightPan(self, chart):
        """
        Pan chart to the right by pan_bars amount
        """
        try:
            if self.chart_df is None or len(self.chart_df) == 0:
                print("ERROR: No chart data available for panning")
                return
            
            total_bars = len(self.chart_df)
            max_start = max(0, total_bars - self.visible_bars)
            self.current_start = min(max_start, self.current_start + self.pan_bars)
            
            end_index = min(self.current_start + self.visible_bars, total_bars)
            
            if self.current_start < total_bars:
                chart.time_scale().set_visible_range({
                    'from': self.chart_df['time'].iloc[self.current_start],
                    'to': self.chart_df['time'].iloc[end_index - 1]
                })
                print(f"DEBUG: Panned right - showing bars {self.current_start} to {end_index - 1}")
            
        except Exception as e:
            print(f"ERROR: Right pan failed: {e}")

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

            # Create main chart (Panel 0) - larger size
            chart = Chart(width=1400, height=900, inner_width=1.0, inner_height=main_height)
            chart.legend(visible=True, font_size=16)

            # Add title if set
            if self.title:
                chart.topbar.textbox('title', self.title)

            # Add spacer to push buttons to the right side
            chart.topbar.textbox('spacer', '                    ')  # Long space

            # Store main chart reference for pan operations
            self.main_chart = chart

            # Implement button handlers
            def handle_reset_zoom(chart_ref):
                try:
                    chart.time_scale().fit_content()
                    print("DEBUG: Zoom reset")
                except Exception as e:
                    print(f"ERROR: Reset zoom failed: {e}")

            def handle_show_all(chart_ref):
                try:
                    # Show all data points
                    self.current_start = 0
                    chart.time_scale().set_visible_logical_range({
                        'from': 0,
                        'to': len(self.chart_df) - 1
                    })
                    print("DEBUG: Showing all data")
                except Exception as e:
                    print(f"ERROR: Show all failed: {e}")

            def handle_show_recent(chart_ref):
                try:
                    # Show last N bars (e.g., last 100 bars)
                    recent_count = min(self.visible_bars, len(self.chart_df))
                    if recent_count > 0:
                        self.current_start = max(0, len(self.chart_df) - recent_count)
                        chart.time_scale().set_visible_logical_range({
                            'from': len(self.chart_df) - recent_count,
                            'to': len(self.chart_df) - 1
                        })
                    print(f"DEBUG: Showing recent {recent_count} bars")
                except Exception as e:
                    print(f"ERROR: Show recent failed: {e}")

            def handle_left_pan(chart_ref):
                try:
                    if self.chart_df is None or len(self.chart_df) == 0:
                        print("ERROR: No chart data available for panning")
                        return
                    
                    total_bars = len(self.chart_df)
                    self.current_start = max(0, self.current_start - self.pan_bars)
                    
                    end_index = min(self.current_start + self.visible_bars, total_bars)
                    
                    if self.current_start < total_bars:
                        chart.time_scale().set_visible_logical_range({
                            'from': self.current_start,
                            'to': end_index - 1
                        })
                        print(f"DEBUG: Panned left - showing bars {self.current_start} to {end_index - 1}")
                    
                except Exception as e:
                    print(f"ERROR: Left pan failed: {e}")

            def handle_right_pan(chart_ref):
                try:
                    if self.chart_df is None or len(self.chart_df) == 0:
                        print("ERROR: No chart data available for panning")
                        return
                    
                    total_bars = len(self.chart_df)
                    max_start = max(0, total_bars - self.visible_bars)
                    self.current_start = min(max_start, self.current_start + self.pan_bars)
                    
                    end_index = min(self.current_start + self.visible_bars, total_bars)
                    
                    if self.current_start < total_bars:
                        chart.time_scale().set_visible_logical_range({
                            'from': self.current_start,
                            'to': end_index - 1
                        })
                        print(f"DEBUG: Panned right - showing bars {self.current_start} to {end_index - 1}")
                    
                except Exception as e:
                    print(f"ERROR: Right pan failed: {e}")

            # Button handlers - lightweight-charts Python wrapper may not support click events
            # For now, these are visual buttons only
            # To implement functionality, you would need to use keyboard shortcuts or other methods
            print("INFO: Buttons are visual only. Click events may not be supported in this version.")

            # Add buttons to topbar (will appear on the right)
            chart.topbar.button('left_pan', 'Left Pan', func=handle_left_pan)
            chart.topbar.button('right_pan', 'Right Pan', func=handle_right_pan)
            chart.topbar.button('reset_zoom', 'Reset Zoom', func=handle_reset_zoom)
            chart.topbar.button('show_all', 'Show All Data', func=handle_show_all)
            chart.topbar.button('show_recent', 'Show Recent', func=handle_show_recent)
            chart.topbar.menu("menu", ('1min', '5min', '30min'), func=None)

            # Add panel-specific buttons for each subchart
            for panel_id in sorted([p for p in unique_panels if p > 0]):
                chart.topbar.button(f'panel_{panel_id}_toggle', f'Panel {panel_id}')

            # chart.grid(False, False)
            chart.set(self.chart_df)

            self.panels[0] = {'series': [], 'chart': chart}

            # Create subcharts for panels 1, 2, 3, etc.
            sorted_panels = sorted([p for p in unique_panels if p > 0])
            subcharts = {}

            for panel_id in sorted_panels:
                subchart = chart.create_subchart(position='bottom', width=1.0, height=sub_height, sync=True)
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
                
                # Get line properties for this series
                properties = self.line_properties.get(series_name, {})
                
                if panel_id == 0:
                    # Add to main chart as overlay
                    line = self._createLineWithProperties(chart, series_name, properties)
                    
                elif panel_id in subcharts:
                    # Add to subchart
                    subchart = subcharts[panel_id]
                    line = self._createLineWithProperties(subchart, series_name, properties)
                    
                else:
                    print(f"WARNING: Panel {panel_id} not found for series '{series_name}'")
                    continue
                
                # Set data for the line
                line_df = pd.DataFrame({
                    'time': self.chart_df['time'],
                    series_name: data
                })
                line.set(line_df)
                # print(f"DEBUG: Added series '{series_name}' to Panel {panel_id}")

            # Add signal change markers as text annotations
            self._addSignalMarkers(chart, subcharts)

            # Set browser window title if possible
            if self.title:
                try:
                    chart.run_script(f"document.title = '{self.title}';")
                except:
                    pass

            # print(f"DEBUG: Displaying chart '{self.title}' with {num_panels} panels...")
            chart.show(block=True)

        except Exception as e:
            print(f"ERROR in Show: {e}")
            import traceback
            traceback.print_exc()

    def _createLineWithProperties(self, chart_obj, series_name, properties):
        """
        Create a line with specified properties (color, width, style)
        """
        try:
            color = properties.get('color', None)
            lineWidth = properties.get('lineWidth', None)
            lineStyle = properties.get('lineStyle', None)
            
            # Try different methods to apply properties
            if color:
                try:
                    # Method 1: color parameter
                    line = chart_obj.create_line(name=series_name, color=color)
                    print(f"DEBUG: Applied color '{color}' to '{series_name}' (Method 1)")
                    return line
                except Exception as e1:
                    try:
                        # Method 2: options dictionary
                        options = {}
                        if color:
                            options['color'] = color
                        if lineWidth:
                            options['lineWidth'] = lineWidth
                        if lineStyle is not None:
                            options['lineStyle'] = lineStyle
                            
                        line = chart_obj.create_line(name=series_name, **options)
                        print(f"DEBUG: Applied properties {options} to '{series_name}' (Method 2)")
                        return line
                    except Exception as e2:
                        # Method 3: set properties after creation
                        line = chart_obj.create_line(name=series_name)
                        try:
                            if color:
                                line.color = color
                            if lineWidth:
                                line.lineWidth = lineWidth
                            print(f"DEBUG: Applied properties to '{series_name}' (Method 3)")
                        except Exception as e3:
                            print(f"DEBUG: Could not apply properties to '{series_name}' - using default")
                        return line
            else:
                # No special properties, create standard line
                return chart_obj.create_line(name=series_name)
                
        except Exception as e:
            print(f"ERROR creating line for '{series_name}': {e}")
            # Fallback to basic line
            return chart_obj.create_line(name=series_name)

    def _addSignalMarkers(self, chart, subcharts):
        """
        Add signal change markers (A, S, F) as text annotations on chart
        """
        try:
            if not hasattr(self, 'signal_markers') or not self.signal_markers:
                return
            
            for marker in self.signal_markers:
                index = marker['index']
                text = marker['text']
                level = marker['level']
                
                # Create marker data point
                if index < len(self.chart_df):
                    marker_time = self.chart_df['time'].iloc[index]
                    
                    # Try different methods to add text marker
                    try:
                        # Method 1: Using chart marker/annotation
                        chart.marker(
                            time=marker_time,
                            position='above_bar',
                            color='black',
                            shape='text',
                            text=text
                        )
                        print(f"DEBUG: Added text marker '{text}' at index {index} (Method 1)")
                    except:
                        try:
                            # Method 2: Using tooltip or label
                            chart.add_marker({
                                'time': marker_time,
                                'position': 'aboveBar',
                                'color': 'black',
                                'shape': 'circle',
                                'text': text
                            })
                            print(f"DEBUG: Added text marker '{text}' at index {index} (Method 2)")
                        except:
                            # Method 3: Create as a very short line series with specific styling
                            marker_data = [None] * len(self.chart_df)
                            marker_data[index] = level
                            
                            marker_series_name = f"Marker_{text}_{index}"
                            self.custom_series[marker_series_name] = marker_data
                            self.series_ids[marker_series_name] = 9000 + index
                            
                            # Add as point/circle marker
                            marker_line = chart.create_line(name=f"{text}")
                            marker_df = pd.DataFrame({
                                'time': self.chart_df['time'],
                                marker_series_name: marker_data
                            })
                            marker_line.set(marker_df)
                            
                            print(f"DEBUG: Added fallback marker '{text}' at index {index} (Method 3)")
                            
        except Exception as e:
            print(f"ERROR in _addSignalMarkers: {e}")
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


