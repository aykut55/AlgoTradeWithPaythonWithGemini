# -*- coding: utf-8 -*-
"""
Custom Visualizer for Optimization Results
Kullanıcı tarafından özelleştirilmiş görselleştirme sınıfı
"""

import sys
import io
# Windows console encoding fix
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
import os

# Set browser renderer to avoid IDE port issues
pio.renderers.default = "browser"


class MyCustomVisualizer:
    """
    Özelleştirilmiş görselleştirme sınıfı

    Kullanım:
        viz = MyCustomVisualizer(analyzer.df)
        viz.plot_getfyt_percent()
        viz.plot_custom(x='CombNo', y='OR_NetProf', color='period')
    """

    def __init__(self, dataframe: pd.DataFrame, output_dir: str = None):
        """
        Visualizer başlatıcı

        Args:
            dataframe: Görselleştirilecek DataFrame (analyzer.df)
            output_dir: HTML dosyalarının kaydedileceği klasör (varsayılan: output)
        """
        self.df = dataframe

        # Output klasörü
        if output_dir is None:
            # Script'in bulunduğu yerden iki üst klasör
            script_dir = Path(__file__).parent
            self.output_dir = script_dir.parent.parent / "output"
        else:
            self.output_dir = Path(output_dir)

        # Klasörü oluştur
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Grafik sayacı (otomatik isimlendirme için)
        self.plot_counter = 0

        print(f"[MyCustomVisualizer] Başlatıldı: {len(self.df)} satır")
        print(f"[MyCustomVisualizer] Output klasörü: {self.output_dir}")

    def plot_getfyt_percent(self, show=True, save=True):
        """
        OR_GetFyt% görselleştirmesi

        X: CombNo
        Y: OR_GetFyt%
        Color: period
        Hover: Tüm önemli sütunlar

        Args:
            show: Tarayıcıda göster
            save: HTML olarak kaydet

        Returns:
            Plotly Figure objesi
        """
        print("\n" + "=" * 80)
        print("OR_GetFyt% Scatter Plot Oluşturuluyor...")
        print("=" * 80)

        # Hover sütunları
        hover_cols = [
            'CombNo',
            'period',
            'percent',
            'OptResult',
            'OR_IlkBakFy',
            'OR_BakFiyat',
            'OR_GetFiyat',
            'OR_GetFyt%',
            'OR_KomFiyat',
            'OR_BakFyNet',
            'OR_GetFyNet',
            'OR_GetFy%N'
        ]

        # Mevcut olmayan sütunları filtrele
        available_hover_cols = [col for col in hover_cols if col in self.df.columns]

        # Scatter plot oluştur
        fig = px.scatter(
            self.df,
            x='CombNo',
            y='OR_GetFyt%',
            color='period',
            hover_data=available_hover_cols,
            title='OR_GetFyt% Distribution by CombNo',
            labels={
                'CombNo': 'Combination Number',
                'OR_GetFyt%': 'Getiri Fiyat %',
                'period': 'Period'
            },
            template='plotly_white',
            height=700,
            width=1400
        )

        # Nokta stilini ayarla - Daha büyük ve belirgin
        fig.update_traces(
            marker=dict(
                size=5,  # Daha büyük nokta
                opacity=0.85,  # Daha görünür
                line=dict(width=1, color='white')
            )
        )

        # Layout güncelle
        fig.update_layout(
            hovermode='closest',
            title_font_size=16,
            showlegend=True,
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray')
        )

        # Kaydet
        if save:
            self.plot_counter += 1
            filename = f"custom_plot_{self.plot_counter}_getfyt_percent.html"
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            print(f"[OK] Grafik kaydedildi: {filepath}")

        # Göster
        if show:
            fig.show()

        return fig

    def plot_custom(self,
                   x: str,
                   y: str,
                   color: str = None,
                   size: str = None,
                   hover_cols: list = None,
                   title: str = None,
                   show: bool = True,
                   save: bool = True):
        """
        Özelleştirilmiş scatter plot

        Args:
            x: X ekseni sütunu
            y: Y ekseni sütunu
            color: Renklendirme sütunu (opsiyonel)
            size: Boyutlandırma sütunu (opsiyonel)
            hover_cols: Hover'da gösterilecek sütunlar
            title: Grafik başlığı
            show: Tarayıcıda göster
            save: HTML olarak kaydet

        Returns:
            Plotly Figure objesi
        """
        print(f"\n[MyCustomVisualizer] {y} vs {x} grafiği oluşturuluyor...")

        # Başlık oluştur
        if title is None:
            title = f"{y} vs {x}"

        # Hover sütunları
        if hover_cols is None:
            # Varsayılan önemli sütunlar
            hover_cols = ['CombNo', 'period', 'percent', 'OR_NetProf',
                         'OR_WinRate', 'OR_ProfFact', 'OR_TotTrade']

        # Mevcut sütunları filtrele
        available_hover_cols = [col for col in hover_cols if col in self.df.columns]

        # Scatter plot oluştur
        fig = px.scatter(
            self.df,
            x=x,
            y=y,
            color=color,
            size=size,
            hover_data=available_hover_cols,
            title=title,
            template='plotly_white',
            height=700,
            width=1400
        )

        # Stil - Nokta boyutunu belirginleştir
        marker_config = dict(
            opacity=0.85,
            line=dict(width=1, color='white')
        )

        # Eğer size parametresi verilmemişse, sabit orta boyut kullan
        if size is None:
            marker_config['size'] = 8  # Orta boyutta nokta

        fig.update_traces(marker=marker_config)

        # Layout
        fig.update_layout(
            hovermode='closest',
            title_font_size=16,
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray')
        )

        # Kaydet
        if save:
            self.plot_counter += 1
            # Dosya adını sanitize et
            safe_y = y.replace('%', 'percent').replace('/', '_')
            filename = f"custom_plot_{self.plot_counter}_{safe_y}.html"
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            print(f"[OK] Grafik kaydedildi: {filepath}")

        # Göster
        if show:
            fig.show()

        return fig

    def plot_net_profit(self, show=True, save=True):
        """
        Net Profit görselleştirmesi

        Args:
            show: Tarayıcıda göster
            save: HTML olarak kaydet

        Returns:
            Plotly Figure objesi
        """
        return self.plot_custom(
            x='CombNo',
            y='OR_NetProf',
            color='period',
            size='OR_TotTrade',
            hover_cols=['CombNo', 'period', 'percent', 'OR_NetProf',
                       'OR_WinRate', 'OR_ProfFact', 'OR_TotTrade'],
            title='Net Profit Distribution',
            show=show,
            save=save
        )

    def plot_win_rate(self, show=True, save=True):
        """
        Win Rate görselleştirmesi

        Args:
            show: Tarayıcıda göster
            save: HTML olarak kaydet

        Returns:
            Plotly Figure objesi
        """
        return self.plot_custom(
            x='CombNo',
            y='OR_WinRate',
            color='OR_ProfFact',
            hover_cols=['CombNo', 'period', 'OR_WinRate', 'OR_NetProf',
                       'OR_ProfFact', 'OR_TotTrade'],
            title='Win Rate Distribution',
            show=show,
            save=save
        )

    def plot_total_trades(self, show=True, save=True):
        """
        Total Trades görselleştirmesi

        Args:
            show: Tarayıcıda göster
            save: HTML olarak kaydet

        Returns:
            Plotly Figure objesi
        """
        return self.plot_custom(
            x='CombNo',
            y='OR_TotTrade',
            color='OR_WinRate',
            size='OR_NetProf',
            hover_cols=['CombNo', 'period', 'OR_TotTrade', 'OR_NetProf',
                       'OR_WinRate'],
            title='Total Trades Distribution',
            show=show,
            save=save
        )

    def plot_multiple(self, y_cols: list, x_col: str = 'CombNo',
                     color_col: str = 'period', show=True, save=True):
        """
        Çoklu metrik görselleştirmesi (subplots)

        Args:
            y_cols: Y ekseni sütun listesi
            x_col: X ekseni sütunu
            color_col: Renklendirme sütunu
            show: Tarayıcıda göster
            save: HTML olarak kaydet

        Returns:
            Plotly Figure objesi
        """
        from plotly.subplots import make_subplots

        print(f"\n[MyCustomVisualizer] {len(y_cols)} metrik için çoklu grafik oluşturuluyor...")

        n_plots = len(y_cols)

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
            subplot_titles=y_cols,
            vertical_spacing=0.12,
            horizontal_spacing=0.10
        )

        # Her metrik için scatter plot ekle
        for idx, y_col in enumerate(y_cols):
            row = idx // cols + 1
            col = idx % cols + 1

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
                        opacity=0.6
                    ),
                    name=y_col,
                    showlegend=False
                ),
                row=row,
                col=col
            )

        # Layout
        fig.update_layout(
            height=800,
            width=1400,
            title_text=f"Multiple Metrics vs {x_col}",
            template='plotly_white',
            hovermode='closest'
        )

        fig.update_xaxes(showgrid=True)
        fig.update_yaxes(showgrid=True)

        # Kaydet
        if save:
            self.plot_counter += 1
            filename = f"custom_plot_{self.plot_counter}_multiple_metrics.html"
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            print(f"[OK] Çoklu grafik kaydedildi: {filepath}")

        # Göster
        if show:
            fig.show()

        return fig

    def plot_period_percent_combined(self, show=True, save=True):
        """
        Period ve Percent'i tek grafikte göster

        X: OR_GetFyt%
        Y: period
        Color: percent (color bar ile)
        Size: OR_NetProf (opsiyonel)

        Returns:
            Plotly Figure objesi
        """
        print("\n[MyCustomVisualizer] Period & Percent Combined Plot oluşturuluyor...")

        hover_cols = ['CombNo', 'period', 'percent', 'OR_GetFyt%',
                     'OR_NetProf', 'OR_WinRate', 'OR_TotTrade', 'OR_ProfFact']

        # Mevcut sütunları filtrele
        available_hover_cols = [col for col in hover_cols if col in self.df.columns]

        # Scatter plot oluştur
        fig = px.scatter(
            self.df,
            x='OR_GetFyt%',
            y='period',
            color='percent',  # Percent color bar ile gösterilecek
            size='OR_NetProf',  # Net kar ile boyutlandırma (opsiyonel)
            hover_data=available_hover_cols,
            title='OR_GetFyt% vs Period & Percent (Combined View)',
            labels={
                'OR_GetFyt%': 'Getiri Fiyat %',
                'period': 'Period',
                'percent': 'Percent',
                'OR_NetProf': 'Net Profit'
            },
            template='plotly_white',
            color_continuous_scale='Viridis',  # Güzel renk skalası
            height=700,
            width=1400
        )

        # Y eksenini kategorik yap (period discrete olsun)
        fig.update_yaxes(type='category')

        # Layout
        fig.update_layout(
            hovermode='closest',
            title_font_size=16,
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
            coloraxis_colorbar=dict(
                title="Percent",
                thickness=15,
                len=0.7
            )
        )

        # Kaydet
        if save:
            self.plot_counter += 1
            filename = f"custom_plot_{self.plot_counter}_period_percent_combined.html"
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            print(f"[OK] Combined grafik kaydedildi: {filepath}")

        # Göster
        if show:
            fig.show()

        return fig

    def plot_x_y_z(self,
                   x: str,
                   y: str,
                   z: str,
                   title: str = None,
                   size_ref: str = None,
                   show: bool = True,
                   save: bool = True):
        """
        Esnek 3 boyutlu dot plot

        Args:
            x: X ekseni sütunu
            y: Y ekseni sütunu
            z: Renk (color bar) sütunu
            title: Grafik başlığı
            size_ref: Nokta boyutu için referans sütun (None ise x'i kullanır)
            show: Tarayıcıda göster
            save: HTML olarak kaydet

        Returns:
            Plotly Figure objesi

        Örnekler:
            # Örnek 1: OR_GetFyt% (x), period (y), percent (renk)
            viz.plot_x_y_z('OR_GetFyt%', 'period', 'percent')

            # Örnek 2: period (x), percent (y), OR_GetFyt% (renk)
            viz.plot_x_y_z('period', 'percent', 'OR_GetFyt%')

            # Örnek 3: Özel boyut referansı
            viz.plot_x_y_z('OR_GetFyt%', 'period', 'percent', size_ref='OR_NetProf')
        """
        print(f"\n[MyCustomVisualizer] X-Y-Z Plot: {x} vs {y} (color: {z})...")

        # Başlık oluştur
        if title is None:
            title = f"{y} vs {x} (colored by {z})"

        # Boyut referansı (default: x eksenini kullan)
        if size_ref is None:
            size_ref = x

        # Hover sütunları
        hover_cols = ['CombNo', x, y, z, size_ref, 'period', 'percent', 'OR_GetFiyat', 'OR_KomFiyat',
                      'OR_GetFyNet', 'OR_Islem', 'OR_KomIslem', 'OR_KarliOra', 'OR_MaxDD', 'OR_ProfFact', 'OR_NetProf']
        # Tekrarları kaldır ve mevcut olanları filtrele
        hover_cols = list(dict.fromkeys(hover_cols))  # Tekrarları kaldır
        available_hover_cols = [col for col in hover_cols if col in self.df.columns]

        # Scatter plot oluştur
        fig = px.scatter(
            self.df,
            x=x,
            y=y,
            color=z,  # Z color bar ile gösterilecek
            size=size_ref,  # Boyut referansı
            hover_data=available_hover_cols,
            title=title,
            labels={
                x: x,
                y: y,
                z: z,
                size_ref: size_ref
            },
            template='plotly_white',
            color_continuous_scale='Viridis',  # Güzel renk skalası
            height=700,
            width=1400
        )

        # Y ekseni kategorik mi kontrol et (period, percent gibi)
        if y in ['period', 'percent'] or self.df[y].nunique() < 50:
            fig.update_yaxes(type='category')

        # Layout
        fig.update_layout(
            hovermode='closest',
            title_font_size=16,
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray', title=x),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray', title=y),
            coloraxis_colorbar=dict(
                title=z,
                thickness=15,
                len=0.7
            )
        )

        # Kaydet
        if save:
            self.plot_counter += 1
            # Dosya adını sanitize et
            safe_x = x.replace('%', 'pct').replace('/', '_')
            safe_y = y.replace('%', 'pct').replace('/', '_')
            safe_z = z.replace('%', 'pct').replace('/', '_')
            filename = f"custom_plot_{self.plot_counter}_x{safe_x}_y{safe_y}_z{safe_z}.html"
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            print(f"[OK] X-Y-Z grafik kaydedildi: {filepath}")

        # Göster
        if show:
            fig.show()

        return fig

    def plot_x_y(self,
                 x: str,
                 y: str,
                 title: str = None,
                 hover_cols: list = None,
                 show: bool = True,
                 save: bool = True):
        """
        Basit 2 boyutlu scatter plot (renk ve boyut olmadan)

        Args:
            x: X ekseni sütunu
            y: Y ekseni sütunu
            title: Grafik başlığı
            hover_cols: Hover'da gösterilecek sütunlar (opsiyonel)
            show: Tarayıcıda göster
            save: HTML olarak kaydet

        Returns:
            Plotly Figure objesi

        Örnekler:
            # Örnek 1: Basit 2D plot
            viz.plot_x_y('CombNo', 'OR_GetFyNet')

            # Örnek 2: Özel başlık ile
            viz.plot_x_y('CombNo', 'OR_GetFyNet', title='Getiri vs Kombinasyon')

            # Örnek 3: Özel hover sütunları ile
            viz.plot_x_y('CombNo', 'OR_GetFyNet',
                        hover_cols=['CombNo', 'period', 'OR_GetFyNet', 'OR_KomFiyat'])
        """
        print(f"\n[MyCustomVisualizer] 2D Plot: {y} vs {x}...")

        # Başlık oluştur
        if title is None:
            title = f"{y} vs {x}"

        # plot_custom'ı çağır (color=None, size=None ile 2D plot olur)
        return self.plot_custom(
            x=x,
            y=y,
            color=None,  # Renk yok - 2D plot
            size=None,   # Boyut yok - sabit nokta boyutu
            hover_cols=hover_cols,
            title=title,
            show=show,
            save=save
        )

    def plot_x_y_z_dashboard(self,
                             plots: list,
                             title: str = "X-Y-Z Dashboard",
                             cols: int = 2,
                             width: int = 1600,
                             height: int = 800,
                             show: bool = True,
                             save: bool = True):
        """
        Birden fazla X-Y-Z grafiğini yan yana dashboard'da göster

        Args:
            plots: Liste içinde her plot için dict:
                   [{'x': 'col1', 'y': 'col2', 'z': 'col3', 'title': 'Plot 1', 'size_ref': 'col4'}, ...]
            title: Ana dashboard başlığı
            cols: Sütun sayısı (default: 2 - yan yana)
            width: Toplam genişlik
            height: Toplam yükseklik
            show: Tarayıcıda göster
            save: HTML olarak kaydet

        Returns:
            Plotly Figure objesi

        Örnek:
            plots = [
                {'x': 'OR_GetFyt%', 'y': 'period', 'z': 'percent', 'title': 'GetFyt%', 'size_ref': 'OR_GetFyt%'},
                {'x': 'OR_GetFiyat', 'y': 'period', 'z': 'percent', 'title': 'GetFiyat', 'size_ref': 'OR_GetFiyat'}
            ]
            viz.plot_x_y_z_dashboard(plots)
        """
        from plotly.subplots import make_subplots

        print(f"\n[MyCustomVisualizer] X-Y-Z Dashboard oluşturuluyor ({len(plots)} grafik)...")

        n_plots = len(plots)
        rows = (n_plots + cols - 1) // cols  # Ceiling division

        # Subplot başlıkları
        subplot_titles = [p.get('title', f"Plot {i+1}") for i, p in enumerate(plots)]

        # Subplots oluştur
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=subplot_titles,
            vertical_spacing=0.15,
            horizontal_spacing=0.10,
            specs=[[{'type': 'scatter'} for _ in range(cols)] for _ in range(rows)]
        )

        # Her bir plot için trace ekle
        for idx, plot_info in enumerate(plots):
            row = idx // cols + 1
            col = idx % cols + 1

            x_col = plot_info['x']
            y_col = plot_info['y']
            z_col = plot_info['z']
            size_ref = plot_info.get('size_ref', x_col)

            # Her plot için color bar pozisyonu hesapla
            # Subplot grid'de pozisyona göre x konumu ayarla
            colorbar_x = 1.02 if col == cols else (col / cols) - 0.02

            # Y pozisyonu: her satır için ayrı ayarla
            subplot_height = 1.0 / rows
            colorbar_y = 1.0 - (row - 0.5) * subplot_height
            colorbar_len = subplot_height * 0.8  # Subplot yüksekliğinin %80'i

            # Scatter trace oluştur
            trace = go.Scatter(
                x=self.df[x_col],
                y=self.df[y_col],
                mode='markers',
                marker=dict(
                    color=self.df[z_col],
                    colorscale='Viridis',
                    showscale=True,  # Her plotun kendi color bar'ı
                    size=self.df[size_ref] / self.df[size_ref].max() * 20,  # Normalize size
                    opacity=0.7,
                    line=dict(width=1, color='white'),
                    colorbar=dict(
                        title=z_col,
                        thickness=10,
                        len=colorbar_len,
                        x=colorbar_x,
                        y=colorbar_y,
                        yanchor='middle'
                    )
                ),
                name=f"{y_col} vs {x_col}",
                showlegend=False,
                hovertemplate=f'<b>{x_col}</b>: %{{x}}<br>' +
                             f'<b>{y_col}</b>: %{{y}}<br>' +
                             f'<b>{z_col}</b>: %{{marker.color}}<br>' +
                             '<extra></extra>'
            )

            fig.add_trace(trace, row=row, col=col)

            # Eksen etiketleri
            fig.update_xaxes(title_text=x_col, row=row, col=col, showgrid=True)
            fig.update_yaxes(title_text=y_col, row=row, col=col, showgrid=True)

            # Y ekseni kategorik mi kontrol et
            if y_col in ['period', 'percent'] or self.df[y_col].nunique() < 50:
                fig.update_yaxes(type='category', row=row, col=col)

        # Layout
        fig.update_layout(
            title_text=title,
            title_font_size=18,
            width=width,
            height=height,
            template='plotly_white',
            hovermode='closest'
        )

        # Kaydet
        if save:
            self.plot_counter += 1
            filename = f"custom_plot_{self.plot_counter}_dashboard_{len(plots)}plots.html"
            filepath = self.output_dir / filename
            fig.write_html(str(filepath))
            print(f"[OK] Dashboard kaydedildi: {filepath}")

        # Göster
        if show:
            fig.show()

        return fig

    def get_stats(self):
        """DataFrame hakkında özet istatistikler"""
        print("\n" + "=" * 80)
        print("DataFrame İstatistikleri")
        print("=" * 80)
        print(f"Satır sayısı: {len(self.df):,}")
        print(f"Sütun sayısı: {len(self.df.columns)}")
        print(f"Bellek kullanımı: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

        # Sayısal sütunlar
        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns
        print(f"Sayısal sütun sayısı: {len(numeric_cols)}")
        print("=" * 80)


# Hızlı kullanım fonksiyonu
def quick_viz(dataframe: pd.DataFrame, output_dir: str = None):
    """
    Hızlı görselleştirme başlatıcı

    Args:
        dataframe: Görselleştirilecek DataFrame
        output_dir: Çıktı klasörü

    Returns:
        MyCustomVisualizer objesi
    """
    return MyCustomVisualizer(dataframe, output_dir)
