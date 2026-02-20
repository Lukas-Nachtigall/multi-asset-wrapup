import os
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

def run_pro_wrapup():
    # 1. Zeiträume definieren
    today = datetime.now()
    # Logik: Wenn Freitag/Samstag/Sonntag, nimm diesen Montag, sonst Vorwoche
    if today.weekday() >= 4:
        last_monday = today - timedelta(days=today.weekday())
    else:
        last_monday = today - timedelta(days=today.weekday() + 7)
        
    last_friday = last_monday + timedelta(days=4)
    file_date = last_friday.strftime('%Y-%m-%d')
    start_history = last_monday - timedelta(days=120) 
    
    asset_dict = {
        "^GSPC": "S&P 500", "^GDAXI": "DAX", "EEM": "Emerging Markets",
        "IEF": "Treasuries", "LQD": "Corps", "GC=F": "Gold",
        "CL=F": "Oil", "BTC-USD": "Bitcoin"
    }
    
    # 2. Daten laden (mit Puffer für heute)
    download_end = (last_friday + timedelta(days=1)).strftime('%Y-%m-%d')
    raw_data = yf.download(list(asset_dict.keys()), 
                           start=start_history.strftime('%Y-%m-%d'), 
                           end=download_end,
                           progress=False)
    data = raw_data['Adj Close'] if 'Adj Close' in raw_data.columns else raw_data['Close']
    
    # 3. Wöchentliche Performance
    weekly_prices = data.loc[last_monday.strftime('%Y-%m-%d'):].dropna()
    if weekly_prices.empty:
        print("Keine Daten für diese Woche gefunden.")
        return

    perf_series = ((weekly_prices.iloc[-1] / weekly_prices.iloc[0]) - 1) * 100
    df_report = pd.DataFrame(perf_series, columns=['Performance_Pct']).sort_values(by='Performance_Pct', ascending=False)
    
    # 4. Risiko & Trend Logik
    def get_market_metrics(ticker, current_perf):
        hist_returns = data[ticker].pct_change(5).dropna() * 100
        std_dev = hist_returns.std()
        risk = "⚠️ Extrem" if abs(current_perf) > 2 * std_dev else "🔄 Volatil" if abs(current_perf) > std_dev else "✅ Stabil"
        
        price_4w_ago = data[ticker].iloc[-20] if len(data) > 20 else data[ticker].iloc[0]
        current_price = data[ticker].iloc[-1]
        trend_pct = ((current_price / price_4w_ago) - 1) * 100
        trend_emoji = "📈" if trend_pct > 0.5 else "📉" if trend_pct < -0.5 else "➡️"
        return risk, trend_emoji

    # 5. Ordner & Grafik
    os.makedirs('data/weekly', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    plt.figure(figsize=(12, 7))
    sns.set_theme(style="whitegrid")
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in df_report['Performance_Pct']]
    sns.barplot(x='Performance_Pct', y=df_report.index.map(asset_dict), data=df_report, palette=colors, hue=df_report.index, legend=False)
    plt.title(f'Multi-Asset Performance ({last_monday.strftime("%d.%m.")} - {last_friday.strftime("%d.%m.%Y")})', fontsize=15)
    plt.axvline(0, color='black', lw=1)
    plt.savefig("reports/latest.png", bbox_inches='tight')
    plt.savefig(f"reports/wrapup_{file_date}.png", bbox_inches='tight')
    plt.close()

    # 6. Tabelle für README
    table_lines = ["| Asset | Performance | Trend (4W) | Risiko-Status |", "| :--- | :--- | :--- | :--- |"]
    for ticker, row in df_report.iterrows():
        risk_status, trend_icon = get_market_metrics(ticker, row['Performance_Pct'])
        table_lines.append(f"| {asset_dict[ticker]} | {row['Performance_Pct']:+.2f}% | {trend_icon} | {risk_status} |")
    
    readme_content = f"""# 📈 Multi-Asset Weekly Wrap-up

## 🚀 Aktueller Wochenrückblick ({file_date})
![Weekly Performance](reports/latest.png)

### 📊 Markt-Kontext & Analyse
{"\n".join(table_lines)}

---
*Automatisch aktualisiert am {datetime.now().strftime('%d.%m.%Y um %H:%M')}*
"""
    with open("README.md", "w", encoding='utf-8') as f:
        f.write(readme_content)
    
    df_report.to_csv(f"data/weekly/wrapup_{file_date}.csv")
    print(f"Update für {file_date} erfolgreich!")

if __name__ == "__main__":
    run_pro_wrapup()