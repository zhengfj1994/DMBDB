import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
from datetime import datetime
import numpy as np
from sklearn.preprocessing import StandardScaler


plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False


df_raw = pd.read_excel(r'')
df_raw.set_index('Name', inplace=True)

df_raw.index.name = None

def extract_datetime(col_name):
    match = re.search(r'(\d+)\.(\d+)-(\d{1,2}:\d{2})', col_name)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        time_str = match.group(3)
        dt = datetime.strptime(f"2025-{month:02d}-{day:02d} {time_str}", "%Y-%m-%d %H:%M")
        return dt
    else:
        return datetime.max

sorted_info = sorted([(col, extract_datetime(col)) for col in df_raw.columns], key=lambda x: x[1])
sorted_columns = [info[0] for info in sorted_info]
sorted_datetimes = [info[1] for info in sorted_info]

df_sorted = df_raw[sorted_columns]

unique_dates = sorted({dt.date() for dt in sorted_datetimes if dt != datetime.max})
day_map = {d: f"Day{i+1}" for i, d in enumerate(unique_dates)}

x_labels = []
for dt in sorted_datetimes:
    if dt == datetime.max:
        x_labels.append("Unknown")
    else:
        day_label = day_map[dt.date()]
        x_labels.append(day_label)


df_log = np.log1p(df_sorted)

scaler = StandardScaler()
df_scaled = pd.DataFrame(
    scaler.fit_transform(df_log.T).T,
    index=df_log.index,
    columns=df_log.columns
)


plt.figure(figsize=(14, 10))
ax = sns.heatmap(
    df_scaled,
    cmap="vlag",
    xticklabels=x_labels,
    yticklabels=False,
    vmin=-2, vmax=2,
    cbar_kws={"label": "score (log1p transformed)"}
)


ax.set_yticks([])
ax.set_ylabel('')

plt.title("Time-Series Heatmap of Metabolites (volunteer 2)", fontsize=16, fontname="Arial")
plt.xticks(rotation=45, ha='right', fontsize=6, fontname="Arial")

try:
    cb_ax = ax.figure.axes[-1]
    cb_ax.set_ylabel("score (log1p transformed)", fontname="Arial")
    for t in cb_ax.get_yticklabels():
        t.set_fontname("Arial")
except Exception:
    pass

plt.tight_layout()
plt.savefig(r"", dpi=300)
plt.close()

