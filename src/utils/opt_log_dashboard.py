"""
Optimization Log Interactive Dashboard
Plotly Dash ile interaktif web tabanlı görselleştirme dashboard'u

Özellikler:
- Dosya yükleme
- Sütun seçimi (dropdown)
- Dinamik plot oluşturma
- Filtreleme ve sıralama
- Çoklu grafik desteği
- İnteraktif kontroller
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path
import os


class OptLogDashboard:
    """Optimizasyon log verileri için interaktif dashboard"""

    def __init__(self, data_path: str = None):
        """
        Dashboard başlatıcı

        Args:
            data_path: Varsayılan veri dosyası yolu
        """
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.df = None
        self.data_path = data_path

        # Veriyi yükle
        if data_path:
            self.load_data(data_path)

        # Layout oluştur
        self.create_layout()

        # Callback'leri tanımla
        self.setup_callbacks()

    def load_data(self, file_path: str) -> bool:
        """Veri dosyasını yükle"""
        try:
            # CSV dosyasını oku
            self.df = pd.read_csv(
                file_path,
                sep=';',
                encoding='utf-8-sig',
                low_memory=False
            )

            # Virgüllü sayıları düzelt
            for col in self.df.columns:
                if self.df[col].dtype == 'object':
                    try:
                        self.df[col] = (self.df[col]
                                       .astype(str)
                                       .str.replace(',', '.')
                                       .replace('nan', None))
                        self.df[col] = pd.to_numeric(self.df[col], errors='ignore')
                    except:
                        pass

            print(f"[OK] Veri yüklendi: {len(self.df)} satır, {len(self.df.columns)} sütun")
            return True

        except Exception as e:
            print(f"[!] Veri yükleme hatası: {e}")
            return False

    def get_column_options(self):
        """Sütun seçeneklerini döndür"""
        if self.df is None:
            return []
        return [{'label': col, 'value': col} for col in self.df.columns]

    def get_numeric_columns(self):
        """Sadece numerik sütunları döndür"""
        if self.df is None:
            return []
        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
        return [{'label': col, 'value': col} for col in numeric_cols]

    def create_layout(self):
        """Dashboard layout'unu oluştur"""
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("📊 Optimization Log Dashboard", className="text-center mb-4 mt-4"),
                    html.Hr()
                ])
            ]),

            # File Info
            dbc.Row([
                dbc.Col([
                    html.Div(id='file-info', className='mb-3')
                ])
            ]),

            # Controls Row 1
            dbc.Row([
                # X Axis
                dbc.Col([
                    html.Label("X Ekseni:", className="fw-bold"),
                    dcc.Dropdown(
                        id='x-axis-dropdown',
                        options=self.get_column_options(),
                        value='CombNo' if self.df is not None and 'CombNo' in self.df.columns else None,
                        clearable=False
                    )
                ], width=3),

                # Y Axis
                dbc.Col([
                    html.Label("Y Ekseni:", className="fw-bold"),
                    dcc.Dropdown(
                        id='y-axis-dropdown',
                        options=self.get_numeric_columns(),
                        value='OR_NetProf' if self.df is not None and 'OR_NetProf' in self.df.columns else None,
                        clearable=False
                    )
                ], width=3),

                # Color
                dbc.Col([
                    html.Label("Renk (Opsiyonel):", className="fw-bold"),
                    dcc.Dropdown(
                        id='color-dropdown',
                        options=self.get_column_options(),
                        value='period' if self.df is not None and 'period' in self.df.columns else None,
                        clearable=True,
                        placeholder="Renklendirme yok"
                    )
                ], width=3),

                # Size
                dbc.Col([
                    html.Label("Boyut (Opsiyonel):", className="fw-bold"),
                    dcc.Dropdown(
                        id='size-dropdown',
                        options=self.get_numeric_columns(),
                        value=None,
                        clearable=True,
                        placeholder="Sabit boyut"
                    )
                ], width=3),
            ], className="mb-3"),

            # Controls Row 2
            dbc.Row([
                # Plot Type
                dbc.Col([
                    html.Label("Plot Tipi:", className="fw-bold"),
                    dcc.Dropdown(
                        id='plot-type-dropdown',
                        options=[
                            {'label': 'Scatter Plot', 'value': 'scatter'},
                            {'label': 'Line Plot', 'value': 'line'},
                            {'label': 'Bar Chart', 'value': 'bar'},
                        ],
                        value='scatter',
                        clearable=False
                    )
                ], width=2),

                # Top N
                dbc.Col([
                    html.Label("Top N (Opsiyonel):", className="fw-bold"),
                    dcc.Input(
                        id='top-n-input',
                        type='number',
                        placeholder='Tüm veri',
                        min=1,
                        step=1,
                        className='form-control'
                    )
                ], width=2),

                # Sort By
                dbc.Col([
                    html.Label("Sırala (Top N için):", className="fw-bold"),
                    dcc.Dropdown(
                        id='sort-by-dropdown',
                        options=self.get_numeric_columns(),
                        value=None,
                        clearable=True,
                        placeholder="Sıralama yok"
                    )
                ], width=2),

                # Filter Query
                dbc.Col([
                    html.Label("Filtre (Pandas query):", className="fw-bold"),
                    dcc.Input(
                        id='filter-input',
                        type='text',
                        placeholder='Örn: OR_NetProf > 1000000',
                        className='form-control'
                    )
                ], width=4),

                # Update Button
                dbc.Col([
                    html.Label("\u00A0", className="fw-bold"),  # Boşluk için
                    html.Br(),
                    dbc.Button(
                        "🔄 Güncelle",
                        id='update-button',
                        color='primary',
                        className='w-100'
                    )
                ], width=2),
            ], className="mb-4"),

            # Graph
            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        id="loading-graph",
                        type="default",
                        children=[
                            dcc.Graph(
                                id='main-graph',
                                style={'height': '600px'}
                            )
                        ]
                    )
                ])
            ], className="mb-3"),

            # Statistics Row
            dbc.Row([
                dbc.Col([
                    html.Div(id='statistics-info', className='mt-3')
                ])
            ]),

            # Multiple Plots Section
            html.Hr(className="mt-5"),
            dbc.Row([
                dbc.Col([
                    html.H3("📈 Çoklu Metrik Görünümü", className="mb-3"),
                ])
            ]),

            dbc.Row([
                # Metrik seçimi
                dbc.Col([
                    html.Label("Görselleştirilecek Metrikler:", className="fw-bold"),
                    dcc.Dropdown(
                        id='multi-metrics-dropdown',
                        options=self.get_numeric_columns(),
                        value=['OR_NetProf', 'OR_WinRate', 'OR_ProfFact', 'OR_TotTrade']
                        if self.df is not None else [],
                        multi=True,
                        placeholder="Metrik seçin (çoklu seçim)"
                    )
                ], width=8),

                dbc.Col([
                    html.Label("\u00A0", className="fw-bold"),
                    html.Br(),
                    dbc.Button(
                        "📊 Çoklu Grafik Oluştur",
                        id='multi-plot-button',
                        color='success',
                        className='w-100'
                    )
                ], width=4),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col([
                    dcc.Loading(
                        id="loading-multi-graph",
                        type="default",
                        children=[
                            dcc.Graph(
                                id='multi-graph',
                                style={'height': '800px'}
                            )
                        ]
                    )
                ])
            ]),

            # Footer
            html.Hr(className="mt-5"),
            dbc.Row([
                dbc.Col([
                    html.P(
                        "Optimization Log Dashboard v1.0 | Powered by Plotly Dash",
                        className="text-center text-muted"
                    )
                ])
            ])

        ], fluid=True, className="p-4")

    def setup_callbacks(self):
        """Dashboard callback'lerini ayarla"""

        # File info callback
        @self.app.callback(
            Output('file-info', 'children'),
            Input('x-axis-dropdown', 'value')  # Dummy input
        )
        def update_file_info(_):
            if self.df is None:
                return dbc.Alert("⚠️ Veri yüklenmedi!", color="warning")

            return dbc.Alert([
                html.Strong("📁 Veri Seti Bilgileri: "),
                f"{len(self.df):,} satır × {len(self.df.columns)} sütun | ",
                f"Bellek: {self.df.memory_usage(deep=True).sum() / 1024**2:.1f} MB"
            ], color="info")

        # Main graph callback
        @self.app.callback(
            Output('main-graph', 'figure'),
            [Input('update-button', 'n_clicks')],
            [State('x-axis-dropdown', 'value'),
             State('y-axis-dropdown', 'value'),
             State('color-dropdown', 'value'),
             State('size-dropdown', 'value'),
             State('plot-type-dropdown', 'value'),
             State('top-n-input', 'value'),
             State('sort-by-dropdown', 'value'),
             State('filter-input', 'value')]
        )
        def update_main_graph(n_clicks, x_col, y_col, color_col, size_col,
                            plot_type, top_n, sort_by, filter_query):
            if self.df is None:
                return go.Figure().add_annotation(
                    text="Veri yüklenmedi!",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )

            if not x_col or not y_col:
                return go.Figure().add_annotation(
                    text="Lütfen X ve Y eksenlerini seçin",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )

            # Veriyi hazırla
            df_plot = self.df.copy()

            # Filtreleme
            if filter_query:
                try:
                    df_plot = df_plot.query(filter_query)
                except Exception as e:
                    return go.Figure().add_annotation(
                        text=f"Filtre hatası: {str(e)}",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(color="red")
                    )

            # Top N
            if top_n and sort_by:
                df_plot = df_plot.nlargest(int(top_n), sort_by)

            # Plot oluştur
            if plot_type == 'scatter':
                fig = px.scatter(
                    df_plot,
                    x=x_col,
                    y=y_col,
                    color=color_col,
                    size=size_col,
                    hover_data=df_plot.columns[:10],  # İlk 10 sütun
                    title=f"{y_col} vs {x_col}",
                    template='plotly_white'
                )
            elif plot_type == 'line':
                fig = px.line(
                    df_plot,
                    x=x_col,
                    y=y_col,
                    color=color_col,
                    title=f"{y_col} vs {x_col}",
                    template='plotly_white'
                )
            elif plot_type == 'bar':
                fig = px.bar(
                    df_plot,
                    x=x_col,
                    y=y_col,
                    color=color_col,
                    title=f"{y_col} vs {x_col}",
                    template='plotly_white'
                )
            else:
                fig = go.Figure()

            fig.update_layout(
                height=600,
                hovermode='closest',
                showlegend=True
            )

            return fig

        # Statistics callback
        @self.app.callback(
            Output('statistics-info', 'children'),
            [Input('update-button', 'n_clicks')],
            [State('y-axis-dropdown', 'value'),
             State('filter-input', 'value')]
        )
        def update_statistics(n_clicks, y_col, filter_query):
            if self.df is None or not y_col:
                return ""

            # Veriyi hazırla
            df_stats = self.df.copy()
            if filter_query:
                try:
                    df_stats = df_stats.query(filter_query)
                except:
                    return ""

            # İstatistikleri hesapla
            if y_col in df_stats.columns:
                col_data = df_stats[y_col]
                if pd.api.types.is_numeric_dtype(col_data):
                    stats = {
                        'Kayıt Sayısı': f"{col_data.count():,}",
                        'Ortalama': f"{col_data.mean():,.2f}",
                        'Std Sapma': f"{col_data.std():,.2f}",
                        'Min': f"{col_data.min():,.2f}",
                        '25%': f"{col_data.quantile(0.25):,.2f}",
                        'Medyan': f"{col_data.median():,.2f}",
                        '75%': f"{col_data.quantile(0.75):,.2f}",
                        'Max': f"{col_data.max():,.2f}",
                    }

                    # Card oluştur
                    cards = []
                    for key, value in stats.items():
                        cards.append(
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6(key, className="card-subtitle mb-2 text-muted"),
                                        html.H4(value, className="card-title")
                                    ])
                                ])
                            ], width=3, className="mb-2")
                        )

                    return dbc.Row(cards)

            return ""

        # Multi graph callback
        @self.app.callback(
            Output('multi-graph', 'figure'),
            [Input('multi-plot-button', 'n_clicks')],
            [State('multi-metrics-dropdown', 'value'),
             State('x-axis-dropdown', 'value'),
             State('color-dropdown', 'value'),
             State('filter-input', 'value')]
        )
        def update_multi_graph(n_clicks, metrics, x_col, color_col, filter_query):
            if self.df is None or not metrics or not x_col:
                return go.Figure().add_annotation(
                    text="Metrik ve X ekseni seçin",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )

            # Veriyi hazırla
            df_plot = self.df.copy()
            if filter_query:
                try:
                    df_plot = df_plot.query(filter_query)
                except:
                    pass

            # Subplot sayısını hesapla
            n_plots = len(metrics)
            if n_plots <= 2:
                rows, cols = 1, n_plots
            elif n_plots <= 4:
                rows, cols = 2, 2
            elif n_plots <= 6:
                rows, cols = 2, 3
            else:
                rows, cols = 3, 3

            # Subplots oluştur
            from plotly.subplots import make_subplots

            fig = make_subplots(
                rows=rows,
                cols=cols,
                subplot_titles=metrics,
                vertical_spacing=0.12,
                horizontal_spacing=0.10
            )

            # Her metrik için scatter plot ekle
            for idx, metric in enumerate(metrics):
                row = idx // cols + 1
                col = idx % cols + 1

                if color_col and color_col in df_plot.columns:
                    marker_colors = df_plot[color_col]
                    colorscale = 'Viridis'
                else:
                    marker_colors = 'royalblue'
                    colorscale = None

                fig.add_trace(
                    go.Scatter(
                        x=df_plot[x_col],
                        y=df_plot[metric],
                        mode='markers',
                        marker=dict(
                            color=marker_colors,
                            colorscale=colorscale,
                            showscale=False,
                            size=5,
                            opacity=0.6
                        ),
                        name=metric,
                        showlegend=False
                    ),
                    row=row,
                    col=col
                )

            fig.update_layout(
                height=800,
                title_text="Çoklu Metrik Analizi",
                template='plotly_white',
                hovermode='closest'
            )

            fig.update_xaxes(showgrid=True)
            fig.update_yaxes(showgrid=True)

            return fig

    def run(self, debug=True, port=8050):
        """Dashboard'u çalıştır"""
        print("\n" + "=" * 80)
        print("🚀 Optimization Log Dashboard Başlatılıyor...")
        print("=" * 80)
        print(f"\n📊 Dashboard URL: http://localhost:{port}")
        print("🛑 Durdurmak için: CTRL+C\n")

        self.app.run_server(debug=debug, port=port)


def main():
    """Ana fonksiyon"""
    import sys

    # Varsayılan dosya yolu
    default_path = os.path.join("..", "..", "data", "singleTraderOptLog.csv")

    # Komut satırından dosya yolu al
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
    else:
        data_path = default_path

    # Dashboard oluştur ve çalıştır
    dashboard = OptLogDashboard(data_path)

    # Port seçimi
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    else:
        port = 8050

    dashboard.run(debug=True, port=port)


if __name__ == "__main__":
    main()
