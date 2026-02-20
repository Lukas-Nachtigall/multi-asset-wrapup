{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "a7e1c31a-c829-455c-9428-c03f3d69e10d",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "[*********************100%***********************]  8 of 8 completed\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Update abgeschlossen für 2026-02-13\n"
     ]
    }
   ],
   "source": [
    "import os\n",
    "import yfinance as yf\n",
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "from datetime import datetime, timedelta\n",
    "\n",
    "def run_weekly_wrapup():\n",
    "    # 1. Zeitraum berechnen (Letzte Woche Mo-Fr)\n",
    "    today = datetime.now()\n",
    "    last_monday = today - timedelta(days=today.weekday() + 7)\n",
    "    last_friday = last_monday + timedelta(days=4)\n",
    "    file_date = last_friday.strftime('%Y-%m-%d')\n",
    "    \n",
    "    # 2. Assets & Daten laden\n",
    "    asset_dict = {\n",
    "        \"^GSPC\": \"S&P 500\", \"^GDAXI\": \"DAX\", \"EEM\": \"Emerging Markets\",\n",
    "        \"IEF\": \"Treasuries\", \"LQD\": \"Corps\", \"GC=F\": \"Gold\",\n",
    "        \"CL=F\": \"Oil\", \"BTC-USD\": \"Bitcoin\"\n",
    "    }\n",
    "    \n",
    "    raw_data = yf.download(list(asset_dict.keys()), \n",
    "                           start=last_monday.strftime('%Y-%m-%d'), \n",
    "                           end=(last_friday + timedelta(days=1)).strftime('%Y-%m-%d'))\n",
    "    \n",
    "    data = raw_data['Adj Close'] if 'Adj Close' in raw_data.columns else raw_data['Close']\n",
    "    \n",
    "    # 3. Performance berechnen\n",
    "    clean_data = data.dropna()\n",
    "    weekly_perf = ((clean_data.iloc[-1] / clean_data.iloc[0]) - 1) * 100\n",
    "    \n",
    "    df_report = pd.DataFrame(weekly_perf, columns=['Performance_Pct'])\n",
    "    df_report.index.name = 'Ticker'\n",
    "    df_report = df_report.sort_values(by='Performance_Pct', ascending=False)\n",
    "    \n",
    "    # 4. Ordner erstellen\n",
    "    os.makedirs('data/weekly', exist_ok=True)\n",
    "    os.makedirs('reports', exist_ok=True)\n",
    "    \n",
    "    # 5. Speichern (CSV)\n",
    "    df_report.to_csv(f\"data/weekly/wrapup_{file_date}.csv\")\n",
    "    \n",
    "    # 6. Grafik erstellen\n",
    "    plt.figure(figsize=(14, 8))\n",
    "    sns.set_theme(style=\"whitegrid\")\n",
    "    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in df_report['Performance_Pct']]\n",
    "    \n",
    "    ax = sns.barplot(x='Performance_Pct', y=df_report.index.map(asset_dict), \n",
    "                     data=df_report, palette=colors, hue=df_report.index, legend=False)\n",
    "    \n",
    "    # Achsen-Puffer für die Labels\n",
    "    current_xlim = ax.get_xlim()\n",
    "    margin = max(abs(current_xlim[0]), abs(current_xlim[1])) * 0.2\n",
    "    ax.set_xlim(current_xlim[0] - margin, current_xlim[1] + margin)\n",
    "    \n",
    "    plt.title(f'Weekly Multi-Asset Performance: {last_monday.strftime(\"%d.%m.\")} - {last_friday.strftime(\"%d.%m.%Y\")}', fontsize=16)\n",
    "    plt.axvline(0, color='black', lw=1.5, ls='--')\n",
    "    \n",
    "    for i, v in enumerate(df_report['Performance_Pct']):\n",
    "        ax.text(v + (margin*0.05 if v >= 0 else -margin*0.05), i, f'{v:.2f}%', \n",
    "                va='center', fontweight='bold', ha='left' if v >= 0 else 'right')\n",
    "\n",
    "    # Grafik speichern - 1. Als Archiv mit Datum\n",
    "    plot_filename = f\"reports/wrapup_{file_date}.png\"\n",
    "    plt.savefig(plot_filename, bbox_inches='tight')\n",
    "    \n",
    "    # Grafik speichern - 2. Als 'latest.png' für die README (Überschreibt die alte)\n",
    "    plt.savefig(\"reports/latest.png\", bbox_inches='tight')\n",
    "    \n",
    "    plt.close()\n",
    "    print(f\"Update abgeschlossen: Archiv und latest.png erstellt.\")\n",
    "    print(f\"Update abgeschlossen für {file_date}\")\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    run_weekly_wrapup()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "352389c0-4cf4-4cbb-a787-a238ae88f92e",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python [conda env:base] *",
   "language": "python",
   "name": "conda-base-py"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
