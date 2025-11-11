# PRECISE-LOCATION PATTERN: BEST PRACTICE!
# This method of importing Highcharts for Python objects yields the fastest
# performance for the import statement. However, it is more verbose and requires
# you to navigate the extensive Highcharts Core for Python API.
# Import classes using precise module indications. For example:
from highcharts_core.chart import Chart
from highcharts_core.global_options.shared_options import SharedOptions
from highcharts_core.options import HighchartsOptions
from highcharts_core.options.plot_options.bar import BarOptions
from highcharts_core.options.series.bar import BarSeries
from highcharts_stock.chart import Chart
from highcharts_stock.options.series.hlc import OHLCSeries
import requests

class HighchartsDataPlotter:
    def __init__(self):
        self.fig = None

    def run(self):
        stock_response = requests.get('https://demo-live-data.highcharts.com/aapl-ohlc.json')
        stock_data = stock_response.text
        data = stock_response.text

        as_dict = {
            'range_selector': {
                'selected': 2
            },
            'title': {
                'text': 'AAPL Stock Price'
            },
            'series': [
                {
                    'type': 'ohlc',
                    'name': 'AAPL Stock Price',
                    'data': stock_data,
                    'data_grouping': {
                        'units': [[
                            'week',
                            [1]
                        ],
                        [
                            'month',
                            [1, 2, 3, 4, 6]
                        ]]
                    }
                }
            ]
        }

        options = {
            'rangeSelector': {
                'selected': 2
            },

            'yAxis': [{
                'height': '75%',
                'resize': {
                    'enabled': True
                },
                'labels': {
                    'align': 'right',
                    'x': -3
                },
                'title': {
                    'text': 'AAPL'
                }
            }, {
                'top': '75%',
                'height': '25%',
                'labels': {
                    'align': 'right',
                    'x': -3
                },
                'offset': 0,
                'title': {
                    'text': 'MACD'
                }
            }],

            'title': {
                'text': 'AAPL Stock Price'
            },

            'subtitle': {
                'text': 'With MACD and Pivot Points technical indicators'
            },

            'series': [{
                'type': 'ohlc',
                'id': 'aapl',
                'name': 'AAPL Stock Price',
                'data': data,
                'zIndex': 1
            }]
        }

        # chart = Chart.from_options(as_dict)
        chart = Chart.from_options(options)
        chart.is_stock_chart = True

        chart = chart.options.series[0].add_indicator(chart,
                                                      'macd',
                                                      indicator_kwargs={
                                                          'y_axis': 1
                                                      })
        chart = chart.options.series[0].add_indicator(chart,
                                                      'pivotpoints',
                                                      indicator_kwargs={
                                                          'z_index': 0,
                                                          'line_width': 1,
                                                          'data_labels': {
                                                              'overflow': 'none',
                                                              'crop': False,
                                                              'y': 4,
                                                              'style': {
                                                                  'font_size': 9
                                                              }
                                                          }
                                                      })

        chart.display()


