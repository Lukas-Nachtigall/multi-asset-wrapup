import os
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

def run_pro_wrapup():
    # 1. Zeiträume definieren
    today = datetime.now()
    
    # Logik für Wochenabschluss (Freitag bis Freitag)
    if today.weekday() >= 4: # Fr, Sa, So
        last_monday = today - timedelta(days=today.weekday())
    else: # Mo, Di, Mi, Do
        last_monday = today - timedelta(days=today.weekday() + 7)
        
    last_friday = last_monday + timedelta(days=4)
    prev_friday = last_monday - timedelta(days=3) # Der Startpunkt für die Performance
    
    file_date = last_friday.strftime('%Y-%m-%d')
    start_history = last_monday - timedelta(days=150) # Mehr Puffer für 4W-Trend & Volatilität
    
    # TICKER-UPDATE: .DE für Euro-Preise (passend zu Trade Republic)
    asset_dict = {
        "SXR8.DE": "S&P 500 (EUR)", 
        "^GDAXI": "DAX", 
        "IS3N.DE": "Emerging Markets",
        "EUNH.DE": "Treasuries (EUR)", 
        "IEAC.DE": "Corps (EUR)", 
        "GC=F": "Gold",
        "CL=F": "Oil", 
        "BTC-USD": "Bitcoin"
    }
    
   # 2. Daten laden
    download_end = (last_friday + timedelta(days=1)).strftime('%Y-%m-%d')
    raw_data = yf.download(list(asset_dict.keys()), 
                           start=start_history.strftime('%Y-%m-%d'), 
                           end=download_end,
                           progress=False)
                           
    data = raw_data['Adj Close'] if 'Adj Close' in raw_data.columns else raw_data['Close']

    # WICHTIG: Erst Uhrzeiten entfernen, dann Lücken füllen
    data.index = pd.to_datetime(data.index).date
    data = data.ffill().bfill()
    
    perf_dict = {}
    metrics_dict = {}

    for ticker in asset_dict.keys():
        try:
            # 1. Handelstage finden (sucht den nächsten realen Datenpunkt in der Vergangenheit)
            actual_start_date = data.index[data.index <= prev_friday.date()][-1]
            actual_end_date   = data.index[data.index <= last_friday.date()][-1]
            actual_4w_date    = data.index[data.index <= (last_friday - timedelta(days=28)).date()][-1]

            # 2. Preise abrufen
            price_start = data.loc[actual_start_date, ticker]
            price_end   = data.loc[actual_end_date, ticker]
            price_4w    = data.loc[actual_4w_date, ticker]

            # 3. Wöchentliche Performance
            perf_pct = ((price_end / price_start) - 1) * 100
            perf_dict[ticker] = perf_pct
            
            # 4. Risiko-Status
            hist_returns = data[ticker].pct_change(5).dropna() * 100
            std_dev = hist_returns.std()
            if std_dev > 0:
                risk_status = "⚠️ Extrem" if abs(perf_pct) > 2 * std_dev else "🔄 Volatil" if abs(perf_pct) > std_dev else "✅ Stabil"
            else:
                risk_status = "✅ Stabil"
            
            # 5. Trend (4 Wochen)
            trend_pct = ((price_end / price_4w) - 1) * 100
            trend_icon = "📈" if trend_pct > 0.5 else "📉" if trend_pct < -0.5 else "➡️"
            
            metrics_dict[ticker] = (risk_status, trend_icon)
            
        except Exception as e:
            print(f"Fehler bei {ticker}: {e}")
            perf_dict[ticker] = 0.0
            metrics_dict[ticker] = ("N/A", "➡️")

    # Ergebnis-DataFrame erstellen
    df_report = pd.DataFrame.from_dict(perf_dict, orient='index', columns=['Performance_Pct']).sort_values(by='Performance_Pct', ascending=False)

    # 5. Grafik & Report-Erstellung
    os.makedirs('reports', exist_ok=True)
    plt.figure(figsize=(12, 7))
    sns.set_theme(style="whitegrid")
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in df_report['Performance_Pct']]
    
    sns.barplot(x='Performance_Pct', y=df_report.index.map(asset_dict), data=df_report, palette=colors, hue=df_report.index, legend=False)
    plt.title(f'Multi-Asset Performance ({prev_friday.strftime("%d.%m.")} - {last_friday.strftime("%d.%m.%Y")})', fontsize=15)
    plt.axvline(0, color='black', lw=1)
    plt.savefig("reports/latest.png", bbox_inches='tight')
    plt.close()

    # 6. README Tabelle
    table_lines = ["| Asset | Performance | Trend (4W) | Risiko-Status |", "| :--- | :--- | :--- | :--- |"]
    for ticker, row in df_report.iterrows():
        risk_status, trend_icon = metrics_dict[ticker]
        table_lines.append(f"| {asset_dict[ticker]} | {row['Performance_Pct']:+.2f}% | {trend_icon} | {risk_status} |")
    
    table_string = "\n".join(table_lines)
    readme_content = f"""# 📈 Multi-Asset Weekly Wrap-up\n\n## Aktueller Wochenrückblick ({file_date})\n![Weekly Performance](reports/latest.png)\n\n### Markt-Kontext & Analyse\n{table_string}\n\n--- \n*Automatisch aktualisiert am {datetime.now().strftime('%d.%m.%Y um %H:%M')}*"""
    
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"Update für {file_date} erfolgreich!")

if __name__ == "__main__":
    run_pro_wrapup()