"""
Optimization Log Visualizer
OptLogAnalyzer ile analiz edilen verileri görselleştirmek için kullanılır.
Plotly ile interaktif scatter plotlar oluşturur.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, List, Union, Dict, Any
from pathlib import Path


class OptLogVisualizer:
    """
    Optimizasyon log verilerini görselleştiren sınıf.

    Özellikler:
    - Scatter plot (dot plot) görselleştirme
    - İnteraktif grafik (zoom, hover, filter)
    - Çoklu metrik karşılaştırma
    - Renklendirme ve boyutlandırma seçenekleri
    - HTML olarak kaydetme
    """

    def __init__(self, dataframe: Optional[pd.DataFrame] = None):
        """
        Visualizer başlatıcı

        Args:
            dataframe: Görselleştirilecek DataFrame (OptLogAnalyzer'dan gelen)
        """
        self.df = dataframe

    def load_dataframe(self, df: pd.DataFrame) -> None:
        """DataFrame yükle"""
        self.df = df

    def scatter_plot(self,
                    x_col: str,
                    y_col: str,
                    title: Optional[str] = None,
                    color_col: Optional[str] = None,
                    size_col: Optional[str] = None,
                    hover_cols: Optional[List[str]] = None,
                    width: int = 1200,
                    height: int = 700,
                    show: bool = True) -> go.Figure:
        """
        Scatter plot (dot plot) oluşturur

        Args:
            x_col: X ekseni sütunu
            y_col: Y ekseni sütunu
            title: Grafik başlığı
            color_col: Renklendirme için sütun (opsiyonel)
            size_col: Nokta boyutu için sütun (opsiyonel)
            hover_cols: Hover'da gösterilecek ek sütunlar
            width: Grafik genişliği
            height: Grafik yüksekliği
            show: Grafiği göster (True) veya sadece döndür (False)

        Returns:
            Plotly Figure objesi
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return None

        # Başlık oluştur
        if title is None:
            title = f"{y_col} vs {x_col}"

        # Hover verisi hazırla
        hover_data = hover_cols if hover_cols else []

        # Plotly Express ile scatter plot
        fig = px.scatter(
            self.df,
            x=x_col,
            y=y_col,
            color=color_col,
            size=size_col,
            hover_data=hover_data,
            title=title,
            width=width,
            height=height,
            template='plotly_white'
        )

        # Eksen etiketleri
        fig.update_xaxes(title_text=x_col, showgrid=True)
        fig.update_yaxes(title_text=y_col, showgrid=True)

        # Layout
        fig.update_layout(
            hovermode='closest',
            title_font_size=16,
            showlegend=True
        )

        if show:
            fig.show()

        return fig

    def multiple_scatter_plots(self,
                              x_col: str,
                              y_cols: List[str],
                              title: Optional[str] = None,
                              color_col: Optional[str] = None,
                              rows: Optional[int] = None,
                              cols: Optional[int] = None,
                              width: int = 1400,
                              height: int = 800,
                              show: bool = True) -> go.Figure:
        """
        Birden fazla scatter plot oluşturur (subplots)

        Args:
            x_col: X ekseni sütunu (hepsi için aynı)
            y_cols: Y ekseni sütunları listesi (her biri ayrı subplot)
            title: Ana başlık
            color_col: Renklendirme için sütun
            rows: Satır sayısı (None ise otomatik)
            cols: Sütun sayısı (None ise otomatik)
            width: Grafik genişliği
            height: Grafik yüksekliği
            show: Grafiği göster

        Returns:
            Plotly Figure objesi
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return None

        n_plots = len(y_cols)

        # Otomatik layout hesapla
        if rows is None and cols is None:
            if n_plots <= 2:
                rows, cols = 1, n_plots
            elif n_plots <= 4:
                rows, cols = 2, 2
            elif n_plots <= 6:
                rows, cols = 2, 3
            else:
                rows, cols = 3, 3
        elif rows is None:
            rows = (n_plots + cols - 1) // cols
        elif cols is None:
            cols = (n_plots + rows - 1) // rows

        # Subplot başlıkları
        subplot_titles = [f"{y_col}" for y_col in y_cols]

        # Subplots oluştur
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=subplot_titles,
            vertical_spacing=0.12,
            horizontal_spacing=0.10
        )

        # Her bir subplot için scatter plot ekle
        for idx, y_col in enumerate(y_cols):
            row = idx // cols + 1
            col = idx % cols + 1

            # Renk verisi
            if color_col:
                marker_colors = self.df[color_col]
            else:
                marker_colors = 'blue'

            fig.add_trace(
                go.Scatter(
                    x=self.df[x_col],
                    y=self.df[y_col],
                    mode='markers',
                    marker=dict(
                        color=marker_colors,
                        colorscale='Viridis' if color_col else None,
                        showscale=(idx == 0 and color_col is not None),
                        size=6,
                        opacity=0.7,
                        line=dict(width=0.5, color='white')
                    ),
                    name=y_col,
                    showlegend=False,
                    hovertemplate=f'<b>{x_col}</b>: %{{x}}<br>' +
                                 f'<b>{y_col}</b>: %{{y}}<br>' +
                                 '<extra></extra>'
                ),
                row=row,
                col=col
            )

        # Ana başlık
        if title is None:
            title = f"Multiple Metrics vs {x_col}"

        # Layout güncelle
        fig.update_layout(
            title_text=title,
            title_font_size=18,
            width=width,
            height=height,
            template='plotly_white',
            hovermode='closest'
        )

        # Tüm eksenlere grid ekle
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

        if show:
            fig.show()

        return fig

    def comparison_plot(self,
                       metrics: List[str],
                       title: Optional[str] = "Optimization Metrics Comparison",
                       filter_condition: Optional[str] = None,
                       top_n: Optional[int] = None,
                       sort_by: Optional[str] = None,
                       color_col: str = 'CombNo',
                       width: int = 1400,
                       height: int = 700,
                       show: bool = True) -> go.Figure:
        """
        Farklı metrikleri karşılaştırmalı olarak gösterir

        Args:
            metrics: Görselleştirilecek metrik sütunları
            title: Grafik başlığı
            filter_condition: Pandas query formatında filtreleme (opsiyonel)
            top_n: En iyi n kayıt (sort_by ile birlikte)
            sort_by: Sıralama sütunu
            color_col: Renklendirme sütunu
            width: Grafik genişliği
            height: Grafik yüksekliği
            show: Grafiği göster

        Returns:
            Plotly Figure objesi
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return None

        # Veriyi hazırla
        df_plot = self.df.copy()

        # Filtreleme
        if filter_condition:
            df_plot = df_plot.query(filter_condition)

        # Sıralama ve top N
        if sort_by and top_n:
            df_plot = df_plot.nlargest(top_n, sort_by)

        # Grafik oluştur
        fig = go.Figure()

        # Her metrik için trace ekle
        for metric in metrics:
            if metric in df_plot.columns:
                fig.add_trace(go.Scatter(
                    x=df_plot.index,
                    y=df_plot[metric],
                    mode='markers',
                    name=metric,
                    marker=dict(size=8, opacity=0.7),
                    hovertemplate=f'<b>{metric}</b>: %{{y}}<br>' +
                                 '<extra></extra>'
                ))

        fig.update_layout(
            title=title,
            title_font_size=16,
            xaxis_title='Combination Index',
            yaxis_title='Value',
            width=width,
            height=height,
            template='plotly_white',
            hovermode='x unified',
            showlegend=True
        )

        if show:
            fig.show()

        return fig

    def correlation_heatmap(self,
                          columns: List[str],
                          title: str = "Correlation Heatmap",
                          width: int = 1000,
                          height: int = 800,
                          show: bool = True) -> go.Figure:
        """
        Korelasyon ısı haritası oluşturur

        Args:
            columns: Korelasyon hesaplanacak sütunlar
            title: Grafik başlığı
            width: Grafik genişliği
            height: Grafik yüksekliği
            show: Grafiği göster

        Returns:
            Plotly Figure objesi
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return None

        # Korelasyon matrisi hesapla
        corr_matrix = self.df[columns].corr()

        # Heatmap oluştur
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))

        fig.update_layout(
            title=title,
            title_font_size=16,
            width=width,
            height=height,
            template='plotly_white'
        )

        if show:
            fig.show()

        return fig

    def distribution_plot(self,
                         column: str,
                         plot_type: str = 'histogram',
                         bins: int = 50,
                         title: Optional[str] = None,
                         width: int = 1000,
                         height: int = 600,
                         show: bool = True) -> go.Figure:
        """
        Bir sütunun dağılımını gösterir

        Args:
            column: Görselleştirilecek sütun
            plot_type: 'histogram', 'box', veya 'violin'
            bins: Histogram için bin sayısı
            title: Grafik başlığı
            width: Grafik genişliği
            height: Grafik yüksekliği
            show: Grafiği göster

        Returns:
            Plotly Figure objesi
        """
        if self.df is None:
            print("[!] Henüz veri yüklenmedi!")
            return None

        if title is None:
            title = f"Distribution of {column}"

        if plot_type == 'histogram':
            fig = px.histogram(self.df, x=column, nbins=bins, title=title)
        elif plot_type == 'box':
            fig = px.box(self.df, y=column, title=title)
        elif plot_type == 'violin':
            fig = px.violin(self.df, y=column, title=title, box=True)
        else:
            print(f"[!] Geçersiz plot_type: {plot_type}")
            return None

        fig.update_layout(
            width=width,
            height=height,
            template='plotly_white'
        )

        if show:
            fig.show()

        return fig

    def save_figure(self, fig: go.Figure, output_path: str, format: str = 'html') -> None:
        """
        Grafiği dosyaya kaydet

        Args:
            fig: Plotly Figure objesi
            output_path: Çıktı dosyası yolu
            format: Dosya formatı ('html', 'png', 'jpg', 'svg', 'pdf')
                   NOT: png, jpg, svg, pdf için 'kaleido' paketi gerekir
        """
        if fig is None:
            print("[!] Kaydedilecek grafik yok!")
            return

        try:
            if format == 'html':
                fig.write_html(output_path)
                print(f"[OK] HTML grafik kaydedildi: {output_path}")
            else:
                # Statik görüntü için kaleido gerekir
                try:
                    fig.write_image(output_path, format=format)
                    print(f"[OK] {format.upper()} grafik kaydedildi: {output_path}")
                except Exception as e:
                    print(f"[!] Statik görüntü kaydetme hatası: {e}")
                    print("    'kaleido' paketini yükleyin: pip install kaleido")
        except Exception as e:
            print(f"[!] Kaydetme hatası: {e}")

    def create_dashboard(self,
                        metrics: Dict[str, str],
                        x_col: str = 'CombNo',
                        color_col: Optional[str] = None,
                        title: str = "Optimization Dashboard",
                        width: int = 1600,
                        height: int = 1200,
                        show: bool = True) -> go.Figure:
        """
        Çoklu metrik dashboard'u oluşturur

        Args:
            metrics: {subplot_title: column_name} dictionary
            x_col: X ekseni sütunu
            color_col: Renklendirme sütunu
            title: Ana başlık
            width: Grafik genişliği
            height: Grafik yüksekliği
            show: Grafiği göster

        Returns:
            Plotly Figure objesi

        Örnek:
            metrics = {
                'Net Profit': 'OR_NetProf',
                'Win Rate': 'OR_WinRate',
                'Total Trades': 'OR_TotTrade',
                'Profit Factor': 'OR_ProfFact'
            }
            viz.create_dashboard(metrics)
        """
        y_cols = list(metrics.values())
        subplot_titles = list(metrics.keys())

        n_plots = len(metrics)

        # Layout hesapla
        if n_plots <= 2:
            rows, cols = 1, n_plots
        elif n_plots <= 4:
            rows, cols = 2, 2
        elif n_plots <= 6:
            rows, cols = 2, 3
        else:
            rows, cols = 3, 3

        # Subplots oluştur
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=subplot_titles,
            vertical_spacing=0.12,
            horizontal_spacing=0.08
        )

        # Her bir subplot için scatter plot ekle
        for idx, (subtitle, y_col) in enumerate(metrics.items()):
            row = idx // cols + 1
            col = idx % cols + 1

            # Renk verisi
            if color_col and color_col in self.df.columns:
                marker_colors = self.df[color_col]
                colorscale = 'Viridis'
            else:
                marker_colors = 'royalblue'
                colorscale = None

            fig.add_trace(
                go.Scatter(
                    x=self.df[x_col],
                    y=self.df[y_col],
                    mode='markers',
                    marker=dict(
                        color=marker_colors,
                        colorscale=colorscale,
                        showscale=False,
                        size=5,
                        opacity=0.6,
                        line=dict(width=0.5, color='white')
                    ),
                    name=subtitle,
                    showlegend=False,
                    hovertemplate=f'<b>{x_col}</b>: %{{x}}<br>' +
                                 f'<b>{subtitle}</b>: %{{y}}<br>' +
                                 '<extra></extra>'
                ),
                row=row,
                col=col
            )

        # Layout güncelle
        fig.update_layout(
            title_text=title,
            title_font_size=20,
            width=width,
            height=height,
            template='plotly_white',
            hovermode='closest',
            showlegend=False
        )

        # Grid ekle
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

        if show:
            fig.show()

        return fig


def quick_plot(df: pd.DataFrame,
              x_col: str,
              y_col: str,
              title: Optional[str] = None,
              color_col: Optional[str] = None,
              **kwargs) -> go.Figure:
    """
    Hızlı scatter plot oluşturma fonksiyonu

    Args:
        df: DataFrame
        x_col: X ekseni sütunu
        y_col: Y ekseni sütunu
        title: Grafik başlığı
        color_col: Renklendirme sütunu
        **kwargs: Diğer parametreler (width, height, vs.)

    Returns:
        Plotly Figure objesi
    """
    viz = OptLogVisualizer(df)
    return viz.scatter_plot(x_col, y_col, title, color_col, **kwargs)
