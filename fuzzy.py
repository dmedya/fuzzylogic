import tkinter as tk
from tkinter import messagebox
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from openai import OpenAI
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# OpenAI istemcisi
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # API anahtarını çevre değişkeninden al

# Bulanık mantık üyelik fonksiyonları ve kurallar
toprak_nem = ctrl.Antecedent(np.arange(0, 101, 1), 'toprak_nem')
sicaklik = ctrl.Antecedent(np.arange(0, 41, 1), 'sicaklik')
ruzgar = ctrl.Antecedent(np.arange(0, 31, 1), 'ruzgar')
yagmur = ctrl.Antecedent(np.arange(0, 101, 1), 'yagmur')
saat = ctrl.Antecedent(np.arange(0, 24, 1), 'saat')

sulama_suresi = ctrl.Consequent(np.arange(0, 61, 1), 'sulama_suresi')
sulama_miktari = ctrl.Consequent(np.arange(0, 11, 1), 'sulama_miktari')

toprak_nem['dusuk'] = fuzz.trimf(toprak_nem.universe, [0, 0, 30])
toprak_nem['orta'] = fuzz.trimf(toprak_nem.universe, [20, 50, 80])
toprak_nem['yuksek'] = fuzz.trimf(toprak_nem.universe, [60, 100, 100])

sicaklik['soguk'] = fuzz.trimf(sicaklik.universe, [0, 0, 15])
sicaklik['ilik'] = fuzz.trimf(sicaklik.universe, [10, 20, 30])
sicaklik['sicak'] = fuzz.trimf(sicaklik.universe, [25, 40, 40])

ruzgar['dusuk'] = fuzz.trimf(ruzgar.universe, [0, 0, 10])
ruzgar['orta'] = fuzz.trimf(ruzgar.universe, [5, 15, 25])
ruzgar['yuksek'] = fuzz.trimf(ruzgar.universe, [20, 30, 30])

yagmur['yok'] = fuzz.trimf(yagmur.universe, [0, 0, 20])
yagmur['az'] = fuzz.trimf(yagmur.universe, [10, 40, 70])
yagmur['cok'] = fuzz.trimf(yagmur.universe, [60, 100, 100])

saat['gece'] = fuzz.trimf(saat.universe, [0, 0, 6])
saat['gunduz'] = fuzz.trimf(saat.universe, [5, 12, 19])
saat['aksam'] = fuzz.trimf(saat.universe, [18, 23, 23])

sulama_suresi['kisa'] = fuzz.trimf(sulama_suresi.universe, [0, 0, 20])
sulama_suresi['orta'] = fuzz.trimf(sulama_suresi.universe, [15, 30, 45])
sulama_suresi['uzun'] = fuzz.trimf(sulama_suresi.universe, [40, 60, 60])

sulama_miktari['az'] = fuzz.trimf(sulama_miktari.universe, [0, 0, 4])
sulama_miktari['orta'] = fuzz.trimf(sulama_miktari.universe, [3, 6, 8])
sulama_miktari['cok'] = fuzz.trimf(sulama_miktari.universe, [7, 10, 10])

rule1_sure = ctrl.Rule(
    toprak_nem['dusuk'] & sicaklik['sicak'] & ruzgar['dusuk'] & yagmur['yok'] & saat['gunduz'],
    sulama_suresi['uzun']
)
rule1_miktar = ctrl.Rule(
    toprak_nem['dusuk'] & sicaklik['sicak'] & ruzgar['dusuk'] & yagmur['yok'] & saat['gunduz'],
    sulama_miktari['cok']
)

rule2_sure = ctrl.Rule(
    toprak_nem['orta'] & sicaklik['ilik'] & ruzgar['orta'] & yagmur['az'] & saat['aksam'],
    sulama_suresi['orta']
)
rule2_miktar = ctrl.Rule(
    toprak_nem['orta'] & sicaklik['ilik'] & ruzgar['orta'] & yagmur['az'] & saat['aksam'],
    sulama_miktari['orta']
)

rule3_sure = ctrl.Rule(
    toprak_nem['yuksek'] | yagmur['cok'],
    sulama_suresi['kisa']
)
rule3_miktar = ctrl.Rule(
    toprak_nem['yuksek'] | yagmur['cok'],
    sulama_miktari['az']
)

sulama_ctrl = ctrl.ControlSystem([rule1_sure, rule1_miktar, rule2_sure, rule2_miktar, rule3_sure, rule3_miktar])

def slider_olustur(parent, text, from_, to_, resolution=1):
    frame = tk.Frame(parent, bg="#f3e5f5")
    label = tk.Label(frame, text=text, font=("Arial", 12), bg="#f3e5f5", fg="#4a148c")
    label.pack()
    scale = tk.Scale(frame, from_=from_, to=to_, orient="horizontal", length=300,
                     bg="#e1bee7", fg="#4a148c", resolution=resolution)
    scale.pack(pady=5)
    frame.pack(pady=8)
    scale.set(from_)
    return scale

def plot_membership_functions(nem_val):
    # Create a new figure with two subplots
    fig, (ax0, ax1) = plt.subplots(nrows=2, figsize=(10, 8))
    
    # Plot membership functions for toprak nemi
    ax0.plot(toprak_nem.universe, fuzz.trimf(toprak_nem.universe, [0, 0, 30]), 'b', label='Düşük')
    ax0.plot(toprak_nem.universe, fuzz.trimf(toprak_nem.universe, [20, 50, 80]), 'g', label='Orta')
    ax0.plot(toprak_nem.universe, fuzz.trimf(toprak_nem.universe, [60, 100, 100]), 'r', label='Yüksek')
    ax0.plot([nem_val, nem_val], [0, 1], 'k--', label=f'Giriş: {nem_val}')
    ax0.set_title('Toprak Nemi Üyelik Fonksiyonları')
    ax0.legend()
    
    # Create empty subplot for results
    ax1.set_title('Sulama Sonuçları')
    ax1.bar(['Süre (dk)', 'Miktar (lt)'], [0, 0], color=['blue', 'green'])
    ax1.set_ylim([0, 60])
    
    plt.tight_layout()
    return fig, (ax0, ax1)

def show_graphs(nem_val, sure, miktar):
    # Create a new window for graphs
    graph_window = tk.Toplevel()
    graph_window.title("Sulama Analizi Grafikleri")
    graph_window.geometry("800x800")
    
    # Create plot
    fig, (ax0, ax1) = plot_membership_functions(nem_val)
    
    # Update results plot
    ax1.clear()
    ax1.bar(['Süre (dk)', 'Miktar (lt)'], [sure, miktar], color=['blue', 'green'])
    ax1.set_title('Sulama Sonuçları')
    ax1.set_ylim([0, 60])
    
    # Add plot to window
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

def hesapla():
    nem_val = nem_scale.get()
    sicaklik_val = sicaklik_scale.get()
    ruzgar_val = ruzgar_scale.get()
    yagmur_val = yagmur_scale.get()
    saat_val = saat_scale.get()

    try:
        sim = ctrl.ControlSystemSimulation(sulama_ctrl)

        sim.input['toprak_nem'] = nem_val
        sim.input['sicaklik'] = sicaklik_val
        sim.input['ruzgar'] = ruzgar_val
        sim.input['yagmur'] = yagmur_val
        sim.input['saat'] = saat_val

        sim.compute()

        sure = sim.output['sulama_suresi']
        miktar = sim.output['sulama_miktari']

        # Show graphs in a new window
        show_graphs(nem_val, sure, miktar)

        messagebox.showinfo(
            "Hesaplama Sonucu",
            f"Sulama Süresi: {sure:.2f} dakika\nSulama Miktarı: {miktar:.2f} litre"
        )

    except Exception as e:
        messagebox.showerror("Hesaplama Hatası", str(e))

def gpt_mesaj():
    nem_val = nem_scale.get()
    sicaklik_val = sicaklik_scale.get()
    ruzgar_val = ruzgar_scale.get()
    yagmur_val = yagmur_scale.get()
    saat_val = saat_scale.get()

    prompt = (
        f"Toprak nemi: {nem_val}, sıcaklık: {sicaklik_val}, rüzgar hızı: {ruzgar_val}, "
        f"yağmur ihtimali: {yagmur_val}, saat: {saat_val}. "
        f"Bu verilere göre akıllı sulama için süre ve miktar önerisi yap."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        gpt_cevap = response.choices[0].message.content
        messagebox.showinfo("GPT Tavsiyesi", gpt_cevap)
    except Exception as e:
        messagebox.showerror("GPT Hatası", str(e))

root = tk.Tk()
root.title("Akıllı Sulama Sistemi")
root.geometry("400x700")  # Back to original size
root.configure(bg="#f3e5f5")

baslik = tk.Label(root, text="Akıllı Sulama Kontrolü", font=("Helvetica", 18, "bold"),
                  bg="#f3e5f5", fg="#4a148c")
baslik.pack(pady=15)

# Create frame for controls
controls_frame = tk.Frame(root, bg="#f3e5f5")
controls_frame.pack(fill=tk.X, padx=10)

nem_scale = slider_olustur(controls_frame, "Toprak Nemi (%)", 0, 100)
sicaklik_scale = slider_olustur(controls_frame, "Hava Sıcaklığı (°C)", 0, 40)
ruzgar_scale = slider_olustur(controls_frame, "Rüzgar Hızı (km/s)", 0, 30)
yagmur_scale = slider_olustur(controls_frame, "Yağmur İhtimali (%)", 0, 100)
saat_scale = slider_olustur(controls_frame, "Günün Saati (0-23)", 0, 23)

button_frame = tk.Frame(controls_frame, bg="#f3e5f5")
button_frame.pack(pady=10)

hesapla_btn = tk.Button(button_frame, text="Hesapla", command=hesapla)
hesapla_btn.pack(side=tk.LEFT, padx=5)

gpt_btn = tk.Button(button_frame, text="GPT Mesajı Göster", command=gpt_mesaj)
gpt_btn.pack(side=tk.LEFT, padx=5)

root.mainloop()
