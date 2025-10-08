# Chatgpt ile birlikte yazdık, calismadi, claude ile düzeltildi
import numpy as np
import pandas as pd
import dearpygui.dearpygui as dpg
import threading, time

# =========================
# Config
# =========================
NUM_BARS      = 1000
WINDOW_SIZE   = 200
AUTO_SCROLL   = True
DOUBLE_CLICK_MODE = "LAST"  # "LAST" or "ALL"

SMA_WINDOW    = 20
RSI_WINDOW    = 14
MACD_FAST     = 12
MACD_SLOW     = 26
MACD_SIGNAL   = 9

# =========================
# Data & indicators
# =========================
def generate_big_ohlc(num_bars=500):
    np.random.seed(42)
    price = np.cumsum(np.random.randn(num_bars)) + 100.0
    open_  = price + np.random.randn(num_bars) * 0.5
    close  = price + np.random.randn(num_bars) * 0.5
    high   = np.maximum(open_, close) + np.random.rand(num_bars)
    low    = np.minimum(open_, close) - np.random.rand(num_bars)
    volume = np.random.randint(100, 1000, size=num_bars)
    return pd.DataFrame({"Open":open_, "High":high, "Low":low, "Close":close, "Volume":volume})

def sma(series, window=SMA_WINDOW):
    return series.rolling(window).mean()

def rsi(series, window=RSI_WINDOW):
    d = series.diff()
    gain = (d.where(d>0,0)).rolling(window).mean()
    loss = (-d.where(d<0,0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - (100/(1+rs))).fillna(50.0)

def macd(series, fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    m = ema_fast - ema_slow
    s = m.ewm(span=signal, adjust=False).mean()
    return m, s, m - s

def detect_signal(curr_close, curr_sma, prev_close, prev_sma):
    if prev_close < prev_sma and curr_close > curr_sma:
        return "BUY"
    if prev_close > prev_sma and curr_close < curr_sma:
        return "SELL"
    return "FLAT"

# =========================
# Globals
# =========================
df = generate_big_ohlc(NUM_BARS)
SMA = sma(df["Close"])
RSI = rsi(df["Close"])
MACD, MACD_SIG, MACD_HIST = macd(df["Close"])

SIGNALS = ["FLAT"] * len(df)
for i in range(1, len(df)):
    SIGNALS[i] = detect_signal(df["Close"].iloc[i], SMA.iloc[i],
                               df["Close"].iloc[i-1], SMA.iloc[i-1])

end_idx = len(df) - 1
start_idx = max(0, end_idx - WINDOW_SIZE + 1)

x_price = list(range(start_idx, end_idx+1))
y_sma = SMA.iloc[start_idx:end_idx+1].bfill().tolist()
x_vol   = x_price.copy()
y_vol   = df["Volume"].iloc[start_idx:end_idx+1].tolist()
x_rsi   = x_price.copy()
y_rsi   = RSI.iloc[start_idx:end_idx+1].tolist()
x_macd  = x_price.copy()
y_macd      = MACD.iloc[start_idx:end_idx+1].tolist()
y_macd_sig  = MACD_SIG.iloc[start_idx:end_idx+1].tolist()
y_macd_hist = MACD_HIST.iloc[start_idx:end_idx+1].tolist()

buy_x, buy_y = [], []
sell_x, sell_y = [], []
for i in range(start_idx+1, end_idx+1):
    if SIGNALS[i] != SIGNALS[i-1]:
        if SIGNALS[i] == "BUY":
            buy_x.append(i); buy_y.append(df["Close"].iloc[i])
        elif SIGNALS[i] == "SELL":
            sell_x.append(i); sell_y.append(df["Close"].iloc[i])

# aktif sinyal çizgisi durumu
current_segment = "FLAT"
active_line = None
seg_x, seg_y = [], []

# zoom linkleme & aktif panel
active_panel = "price"   # "price", "vol", "rsi", "macd"
link_y_zoom = False
link_x_zoom = True

# Pan state
is_panning = False
last_mouse_pos = None

# =========================
# Helpers
# =========================
def draw_candles(from_idx, to_idx):
    # Her candle için ayrı line series oluştur (wicks için)
    for i in range(from_idx, to_idx+1):
        row = df.iloc[i]
        # High-Low wick
        dpg.add_line_series([i, i], [row["Low"], row["High"]], 
                           parent="y_axis_price", tag=f"wick_{i}")
        
        # Open-Close body
        color_tag = "green" if row["Close"] >= row["Open"] else "red"
        dpg.add_line_series([i, i], [row["Open"], row["Close"]], 
                           parent="y_axis_price", tag=f"body_{color_tag}_{i}")

def handle_signal_change(sig, idx, price):
    global current_segment, active_line, seg_x, seg_y, buy_x,buy_y,sell_x,sell_y
    if sig != current_segment:
        active_line = None
        if sig == "BUY":
            buy_x.append(idx); buy_y.append(price)
            dpg.configure_item("buy_series", x=buy_x, y=buy_y)
            seg_x, seg_y = [idx], [price]
            active_line = dpg.add_line_series(seg_x, seg_y, label="BUY line", parent="y_axis_price")
        elif sig == "SELL":
            sell_x.append(idx); sell_y.append(price)
            dpg.configure_item("sell_series", x=sell_x, y=sell_y)
            seg_x, seg_y = [idx], [price]
            active_line = dpg.add_line_series(seg_x, seg_y, label="SELL line", parent="y_axis_price")
        current_segment = sig
    else:
        if current_segment in ("BUY","SELL") and active_line:
            seg_x.append(idx); seg_y.append(price)
            dpg.configure_item(active_line, x=seg_x, y=seg_y)

# =========================
# Zoom Control & Synchronization
# =========================
def apply_zoom(axis_ids, mode):
    for axis in axis_ids:
        try:
            if mode == "reset":
                dpg.set_axis_limits_auto(axis)
            else:
                vmin, vmax = dpg.get_axis_limits(axis)
                if vmax <= vmin:
                    continue
                center = (vmin + vmax) / 2
                rng = (vmax - vmin) / 2
                if mode == "in":  rng *= 0.8
                if mode == "out": rng *= 1.25
                dpg.set_axis_limits(axis, center-rng, center+rng)
        except: pass

def sync_x_axis_to_all(source_axis):
    """Synchronize X-axis zoom from one panel to all others"""
    try:
        vmin, vmax = dpg.get_axis_limits(source_axis)
        x_axes = ["x_axis_price", "x_axis_vol", "x_axis_rsi", "x_axis_macd"]
        for axis in x_axes:
            if axis != source_axis:
                dpg.set_axis_limits(axis, vmin, vmax)
    except: pass

def zoom_in_all():
    """Zoom in on all panels synchronously"""
    x_axes = ["x_axis_price", "x_axis_vol", "x_axis_rsi", "x_axis_macd"]
    y_axes = ["y_axis_price", "y_axis_vol", "y_axis_rsi", "y_axis_macd"]
    apply_zoom(x_axes, "in")
    apply_zoom(y_axes, "in")

def zoom_out_all():
    """Zoom out on all panels synchronously"""
    x_axes = ["x_axis_price", "x_axis_vol", "x_axis_rsi", "x_axis_macd"]
    y_axes = ["y_axis_price", "y_axis_vol", "y_axis_rsi", "y_axis_macd"]
    apply_zoom(x_axes, "out")
    apply_zoom(y_axes, "out")

def zoom_reset_all():
    """Reset zoom on all panels synchronously"""
    x_axes = ["x_axis_price", "x_axis_vol", "x_axis_rsi", "x_axis_macd"]
    y_axes = ["y_axis_price", "y_axis_vol", "y_axis_rsi", "y_axis_macd"]
    apply_zoom(x_axes, "reset")
    apply_zoom(y_axes, "reset")

def key_handler(sender, app_data):
    global active_panel
    key = app_data
    if link_y_zoom:
        y_axes = ["y_axis_price","y_axis_rsi","y_axis_macd","y_axis_vol"]
    else:
        y_axes = [f"y_axis_{active_panel}"]
    if link_x_zoom:
        x_axes = ["x_axis_price","x_axis_rsi","x_axis_macd","x_axis_vol"]
    else:
        x_axes = [f"x_axis_{active_panel}"]

    # Use simple key codes instead of constants
    if key == 61: apply_zoom(y_axes, "in")    # = key (61)
    elif key == 45: apply_zoom(y_axes, "out") # - key (45)
    elif key == 48: apply_zoom(y_axes, "reset") # 0 key (48)
    elif key == 91: apply_zoom(x_axes, "in")    # [ key (91)
    elif key == 93: apply_zoom(x_axes, "out")   # ] key (93)
    elif key == 92: apply_zoom(x_axes, "reset") # \ key (92)

def button_zoom(axis_type, mode):
    global active_panel
    if axis_type == "y":
        axes = ["y_axis_price","y_axis_rsi","y_axis_macd","y_axis_vol"] if link_y_zoom else [f"y_axis_{active_panel}"]
    else:
        axes = ["x_axis_price","x_axis_rsi","x_axis_macd","x_axis_vol"] if link_x_zoom else [f"x_axis_{active_panel}"]
    apply_zoom(axes, mode)

# =========================
# Events
# =========================
def set_active_panel(sender, app_data, user_data):
    global active_panel
    active_panel = user_data

def toggle_link_y(sender, app_data):
    global link_y_zoom
    link_y_zoom = app_data

def toggle_link_x(sender, app_data):
    global link_x_zoom
    link_x_zoom = app_data
    # X axis linking is handled manually in zoom functions

def plot_mouse_handler(sender, app_data):
    global is_panning, last_mouse_pos
    
    mouse_button = app_data[1]  # 0=left, 1=right, 2=middle
    click_count = app_data[2]   # 1=single, 2=double
    
    if mouse_button == 0:  # Left mouse button
        if click_count == 2:  # Double click
            if DOUBLE_CLICK_MODE=="LAST":
                idx=len(df)-1
                for axis_name in ["x_axis_price", "x_axis_vol", "x_axis_rsi", "x_axis_macd"]:
                    dpg.set_axis_limits(axis_name, idx-WINDOW_SIZE, idx)
            elif DOUBLE_CLICK_MODE=="ALL":
                for axis_name in ["x_axis_price", "x_axis_vol", "x_axis_rsi", "x_axis_macd"]:
                    dpg.set_axis_limits(axis_name, 0, len(df)-1)
            apply_zoom(["y_axis_price","y_axis_vol","y_axis_rsi","y_axis_macd"], "reset")
        else:  # Single click - start panning
            is_panning = True
            last_mouse_pos = dpg.get_mouse_pos()

def plot_mouse_drag_handler(sender, app_data):
    global is_panning, last_mouse_pos
    
    if is_panning and last_mouse_pos:
        current_pos = dpg.get_mouse_pos()
        dx = current_pos[0] - last_mouse_pos[0]
        
        # Pan all X axes
        for axis_name in ["x_axis_price", "x_axis_vol", "x_axis_rsi", "x_axis_macd"]:
            try:
                vmin, vmax = dpg.get_axis_limits(axis_name)
                range_size = vmax - vmin
                # Convert pixel movement to data units (approximate)
                pan_amount = -dx * range_size / 800  # Assume 800px width
                dpg.set_axis_limits(axis_name, vmin + pan_amount, vmax + pan_amount)
            except:
                pass
        
        last_mouse_pos = current_pos

def plot_mouse_release_handler(sender, app_data):
    global is_panning
    is_panning = False

def mouse_wheel_handler(sender, app_data):
    """Handle mouse wheel zoom with automatic synchronization across all panels"""
    wheel_delta = app_data
    
    if wheel_delta > 0:  # Scroll up - zoom in
        zoom_in_all()
    elif wheel_delta < 0:  # Scroll down - zoom out
        zoom_out_all()

# =========================
# Realtime Append
# =========================
def append_right(new_bar):
    global df,SMA,RSI,MACD,MACD_SIG,MACD_HIST,SIGNALS
    idx=len(df)
    df.loc[idx]=new_bar
    SMA=sma(df["Close"]); RSI=rsi(df["Close"])
    MACD,MACD_SIG,MACD_HIST=macd(df["Close"])

    # Add new candle as individual line series
    # High-Low wick
    dpg.add_line_series([idx, idx], [new_bar["Low"], new_bar["High"]], 
                       parent="y_axis_price", tag=f"wick_{idx}")
    
    # Open-Close body
    color_tag = "green" if new_bar["Close"] >= new_bar["Open"] else "red"
    dpg.add_line_series([idx, idx], [new_bar["Open"], new_bar["Close"]], 
                       parent="y_axis_price", tag=f"body_{color_tag}_{idx}")

    x_price.append(idx); y_sma.append(SMA.iloc[-1])
    dpg.configure_item("sma_series", x=x_price, y=y_sma)
    x_vol.append(idx); y_vol.append(new_bar["Volume"])
    dpg.configure_item("vol_series", x=x_vol, y=y_vol)
    x_rsi.append(idx); y_rsi.append(RSI.iloc[-1])
    dpg.configure_item("rsi_series", x=x_rsi, y=y_rsi)
    dpg.configure_item("rsi70_series", x=x_rsi, y=[70]*len(x_rsi))
    dpg.configure_item("rsi30_series", x=x_rsi, y=[30]*len(x_rsi))
    x_macd.append(idx); y_macd.append(MACD.iloc[-1])
    y_macd_sig.append(MACD_SIG.iloc[-1]); y_macd_hist.append(MACD_HIST.iloc[-1])
    dpg.configure_item("macd_series", x=x_macd, y=y_macd)
    dpg.configure_item("macd_sig_series", x=x_macd, y=y_macd_sig)
    dpg.configure_item("macd_hist_series", x=x_macd, y=y_macd_hist)

    if idx>0:
        sig=detect_signal(df["Close"].iloc[-1],SMA.iloc[-1],df["Close"].iloc[-2],SMA.iloc[-2])
        SIGNALS.append(sig)
        handle_signal_change(sig,idx,df["Close"].iloc[-1])

    if AUTO_SCROLL:
        # Tüm X axis'leri sync et
        for axis_name in ["x_axis_price", "x_axis_vol", "x_axis_rsi", "x_axis_macd"]:
            dpg.set_axis_limits(axis_name, idx-WINDOW_SIZE, idx)

def realtime_feed():
    while dpg.is_dearpygui_running():
        time.sleep(1)
        last_close=df["Close"].iloc[-1]
        new_bar={"Open":last_close+np.random.randn()*0.3,
                 "High":last_close+np.random.rand(),
                 "Low": last_close-np.random.rand(),
                 "Close":last_close+np.random.randn()*0.5,
                 "Volume":int(np.random.randint(100,1000))}
        append_right(new_bar)

# =========================
# GUI
# =========================
def main():
    dpg.create_context()
    dpg.create_viewport(title="AlgoTrade Dashboard Full", width=1600, height=1000)

    with dpg.window(label="Dashboard", width=1580, height=980):
        with dpg.menu_bar():
            dpg.add_menu_item(label="Link Y Zoom", check=True, callback=toggle_link_y)
            dpg.add_menu_item(label="Link X Zoom", check=True, callback=toggle_link_x, default_value=True)

        with dpg.group(horizontal=True):
            dpg.add_text("Y Controls:")
            dpg.add_button(label="Y Zoom In",  callback=lambda: button_zoom("y","in"))
            dpg.add_button(label="Y Zoom Out", callback=lambda: button_zoom("y","out"))
            dpg.add_button(label="Y Reset",    callback=lambda: button_zoom("y","reset"))
            dpg.add_spacer(width=24)
            dpg.add_text("X Controls:")
            dpg.add_button(label="X Zoom In",  callback=lambda: button_zoom("x","in"))
            dpg.add_button(label="X Zoom Out", callback=lambda: button_zoom("x","out"))
            dpg.add_button(label="X Reset",    callback=lambda: button_zoom("x","reset"))
            dpg.add_spacer(width=24)
            dpg.add_text("Sync Controls:")
            dpg.add_button(label="Zoom In All",  callback=zoom_in_all)
            dpg.add_button(label="Zoom Out All", callback=zoom_out_all)
            dpg.add_button(label="Reset All",    callback=zoom_reset_all)

        # PRICE
        with dpg.plot(label="Price", height=400, width=-1, tag="price_plot"):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="Bars", tag="x_axis_price")
            dpg.add_plot_axis(dpg.mvYAxis, label="Price", tag="y_axis_price")
            draw_candles(start_idx, end_idx)
            dpg.add_line_series(x_price, y_sma, label="SMA(20)", parent="y_axis_price", tag="sma_series")
            dpg.add_scatter_series(buy_x, buy_y, label="BUY ▲", parent="y_axis_price", tag="buy_series")
            dpg.add_scatter_series(sell_x, sell_y, label="SELL ▼", parent="y_axis_price", tag="sell_series")
            with dpg.item_handler_registry(tag="price_handlers"):
                dpg.add_item_clicked_handler(callback=set_active_panel, user_data="price")
                dpg.add_item_double_clicked_handler(callback=plot_mouse_handler)
            dpg.bind_item_handler_registry("price_plot", "price_handlers")

        # VOLUME
        with dpg.plot(label="Volume", height=120, width=-1, tag="vol_plot"):
            dpg.add_plot_legend()  # <-- legend eklendi
            dpg.add_plot_axis(dpg.mvXAxis, label="Bars", tag="x_axis_vol")
            dpg.add_plot_axis(dpg.mvYAxis, label="Vol",  tag="y_axis_vol")
            dpg.add_bar_series(x_vol, y_vol, label="Vol", parent="y_axis_vol", tag="vol_series")
            with dpg.item_handler_registry(tag="vol_handlers"):
                dpg.add_item_clicked_handler(callback=set_active_panel, user_data="vol")
                dpg.add_item_double_clicked_handler(callback=plot_mouse_handler)
            dpg.bind_item_handler_registry("vol_plot", "vol_handlers")

        # RSI
        with dpg.plot(label="RSI", height=160, width=-1, tag="rsi_plot"):
            dpg.add_plot_legend()  # <-- legend eklendi
            dpg.add_plot_axis(dpg.mvXAxis, label="Bars", tag="x_axis_rsi")
            dpg.add_plot_axis(dpg.mvYAxis, label="RSI",  tag="y_axis_rsi")
            dpg.add_line_series(x_rsi, y_rsi, label="RSI(14)", parent="y_axis_rsi", tag="rsi_series")
            dpg.add_line_series(x_rsi, [70]*len(x_rsi), label="70", parent="y_axis_rsi", tag="rsi70_series")
            dpg.add_line_series(x_rsi, [30]*len(x_rsi), label="30", parent="y_axis_rsi", tag="rsi30_series")
            with dpg.item_handler_registry(tag="rsi_handlers"):
                dpg.add_item_clicked_handler(callback=set_active_panel, user_data="rsi")
                dpg.add_item_double_clicked_handler(callback=plot_mouse_handler)
            dpg.bind_item_handler_registry("rsi_plot", "rsi_handlers")

        # MACD
        with dpg.plot(label="MACD", height=200, width=-1, tag="macd_plot"):
            dpg.add_plot_legend()  # <-- legend eklendi
            dpg.add_plot_axis(dpg.mvXAxis, label="Bars", tag="x_axis_macd")
            dpg.add_plot_axis(dpg.mvYAxis, label="MACD", tag="y_axis_macd")
            dpg.add_line_series(x_macd, y_macd, label="MACD", parent="y_axis_macd", tag="macd_series")
            dpg.add_line_series(x_macd, y_macd_sig, label="Signal", parent="y_axis_macd", tag="macd_sig_series")
            dpg.add_bar_series(x_macd, y_macd_hist, label="Hist", parent="y_axis_macd", tag="macd_hist_series")
            with dpg.item_handler_registry(tag="macd_handlers"):
                dpg.add_item_clicked_handler(callback=set_active_panel, user_data="macd")
                dpg.add_item_double_clicked_handler(callback=plot_mouse_handler)
            dpg.bind_item_handler_registry("macd_plot", "macd_handlers")

        # X eksenlerini linklemek için manual sync gerekiyor
        # Bu Dear PyGui'de otomatik değil, zoom fonksiyonlarında handle ediliyor

    # Klavye kısayolları ve mouse için global handler
    with dpg.handler_registry():
        dpg.add_key_down_handler(callback=key_handler)
        dpg.add_mouse_move_handler(callback=plot_mouse_drag_handler)
        dpg.add_mouse_release_handler(callback=plot_mouse_release_handler)
        dpg.add_mouse_wheel_handler(callback=mouse_wheel_handler)

    dpg.setup_dearpygui()
    dpg.show_viewport()

    # Realtime feed thread
    threading.Thread(target=realtime_feed, daemon=True).start()

    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
