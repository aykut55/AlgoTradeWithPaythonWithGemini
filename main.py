import os
import plotly.io as pio
from src.AlgoTrader import AlgoTrader

# Configure plotly to avoid PyCharm internal server issues
os.environ["PLOTLY_RENDERER"] = "browser"
pio.renderers.default = "browser"

if __name__ == "__main__":
    print("Hello, Gemini!")

    print("algoTrader, started!")

    algoTrader = AlgoTrader()

    choice = 0
    if choice == 0:
        algoTrader.run_with_single_trader()
    elif choice == 1:
        algoTrader.run_with_multiple_trader()
    elif choice == 2:
        algoTrader.run_optimization_with_single_trader()
    else:
        pass

    print("algoTrader, finished!")


'''
 Perfect! Her PanelWrapper'a zoom ve pan butonları başarıyla eklendi. İşte eklenen özellikler:

  ✅ Başarıyla Eklenen Butonlar:

  🎮 Sync Controls (Grafik Senkronizasyonu):
  - ButtonZoom - Bu paneldeki zoom seviyesini diğer tüm grafiklere uygular
  - ButtonPan - Bu paneldeki pan seviyesini diğer tüm grafiklere uygular

  📊 X-Axis Controls (X Ekseni Kontrolü):
  - X Zoom+ - Sadece bu grafikteki X ekseninde zoom in yapar
  - X Zoom- - Sadece bu grafikteki X ekseninde zoom out yapar

  📈 Y-Axis Controls (Y Ekseni Kontrolü):
  - Y Zoom+ - Sadece bu grafikteki Y ekseninde zoom in yapar
  - Y Zoom- - Sadece bu grafikteki Y ekseninde zoom out yapar

  🔧 Layout ve Yerleşim:
  - Sol taraf: Kontrol butonları (80px genişlik)
  - Sağ taraf: Grafik (kalan alanı kullanır)
  - Horizontal layout: Butonlar ve grafik yan yana
  - Separators: Buton grupları arasında görsel ayırıcılar

  ⚙️ Fonksiyonalite:
  - _on_button_sync_zoom() - Mevcut grafiğin zoom seviyesini MainPanel üzerinden tüm diğer grafiklere aktarır
  - _on_button_sync_pan() - Mevcut grafiğin pan seviyesini MainPanel üzerinden tüm diğer grafiklere aktarır
  - _on_x_zoom_plus/minus() - X ekseninde 1.5x zoom in/out
  - _on_y_zoom_plus/minus() - Y ekseninde 1.5x zoom in/out
  - _get_current_plot_axis() - Mevcut panelin plot axis bilgilerini döndürür

  🎯 Smart Features:
  - Axis limit detection - Mevcut zoom/pan seviyelerini otomatik algılar
  - MainPanel integration - Tüm grafik senkronizasyonu MainPanel üzerinden yapılır
  - Error handling - Tüm fonksiyonlar güvenli exception handling'e sahip
  - Debug logging - Tüm işlemler console'a loglanır

Artık her panelin solunda butonlar var ve:
  - ButtonZoom/ButtonPan ile senkronizasyon yapabilirsiniz
  - X/Y Zoom+/- ile tek grafik bazında zoom yapabilirsiniz
  - Butonlar chart'ın solunda düzgün şekilde yerleşik

> Buttonlar chartların solunda gözükmüyor. Kontrol et...mesala panel = main_panel.AddPanel() ile panel oluşturuluyor ya. Bu panel in içinde hemen solda buttonlar olacak ve sağında chart olacak. ama senin yaptığında görünmüyor

● Haklısın! Sorun şu: _create_plots() metodunda horizontal group oluştururken parent olarak self.panel_tag kullanıyorum, ama bu yanlış. Butonlar ve plot'u aynı horizontal group içinde oluşturmam gerekiyor. Hadi düzeltelim:


'''