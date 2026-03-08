import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from datetime import datetime
from matplotlib import rcParams
import bisect

rcParams['font.sans-serif'] = ['Arial']
rcParams['axes.unicode_minus'] = False


df = pd.read_excel('', dtype={'Name': str})


n_columns = [col for col in df.columns if col.startswith('Z-')]

time_format = "%m.%d-%H:%M"
dt_list = []
for col in n_columns:
    m = re.search(r'Z-(\d{1,2}\.\d{1,2})-(\d{1,2}:\d{2})', col)
    if m:
        date_part, time_part = m.groups()
        dt = datetime.strptime(f"{date_part}-{time_part}", time_format)
        dt = dt.replace(year=2025)
        dt_list.append(dt)
    else:
        dt_list.append(None)


dt_series = pd.Series(dt_list)
dt_cat = pd.Categorical(dt_series.dropna().sort_values(), ordered=True)
categories = dt_cat.categories
categories_list = list(categories)


unique_dates = sorted(set(dt.date() for dt in categories))

day_map = {d: f"Day{i+1}" for i, d in enumerate(unique_dates)}

filtered_dates = unique_dates[-7:]

time_label_list = [(9, 'Coffee'), (15, 'Dark Chocolate'), (20, 'Banana')]

label_colors = {
    'Coffee': 'gray',
    'Dark Chocolate': 'pink',
    'Banana': 'yellow'
}

output_dir = ""
os.makedirs(output_dir, exist_ok=True)

df_to_process = df.iloc[0:]

for idx, (_, row) in enumerate(df_to_process.iterrows(), start=1):
    compound_name = row['Name']

    if isinstance(compound_name, (list, tuple)):
        compound_name = "_".join(map(str, compound_name))
    else:
        compound_name = str(compound_name)

    data_vals = row[n_columns].astype(float)

    x_positions = []
    for dt in dt_list:
        if dt is not None and dt in categories:
            x_positions.append(categories.get_loc(dt))
        else:
            x_positions.append(-1)

    x_filtered = [x for x in x_positions if x >= 0]
    y_filtered = [data_vals.iloc[i] for i, x in enumerate(x_positions) if x >= 0]

    plt.figure(figsize=(20, 8))
    plt.plot(x_filtered, y_filtered, marker='o', color='black', label=f"{compound_name}")

    sorted_events = sorted(time_label_list, key=lambda x: x[0])
    for date in filtered_dates:
        day_positions = []

        for hour, label_en in sorted_events:
            target_dt = datetime.combine(date, datetime.min.time()).replace(year=2025, hour=hour)
            pos = bisect.bisect_left(categories_list, target_dt)

            if pos == len(categories_list):
                pos = len(categories_list) - 1
            elif pos > 0:
                pos = pos - 0.5

            day_positions.append((pos, label_en))

            color = label_colors.get(label_en, 'red')
            plt.axvline(pos, color=color, linestyle='--', alpha=0.5, linewidth=2.5)

        for i, (start_pos, label_en) in enumerate(day_positions):
            color = label_colors.get(label_en, 'gray')

            if i < len(day_positions) - 1:
                end_pos = day_positions[i+1][0]
            else:
                end_dt = datetime.combine(date, datetime.min.time()).replace(year=2025, hour=23, minute=59)
                end_pos_idx = bisect.bisect_left(categories_list, end_dt)
                if end_pos_idx == len(categories_list):
                    end_pos = len(categories_list) - 1
                elif end_pos_idx > 0:
                    end_pos = end_pos_idx - 0.5
                else:
                    end_pos = start_pos
            
            plt.axvspan(start_pos, end_pos, facecolor=color, alpha=0.15, edgecolor=None)

    x_labels = []
    for dt in categories:
        day_label = day_map.get(dt.date(), dt.strftime("%m.%d"))
        time_label = dt.strftime("%H:%M")
        x_labels.append(f"{day_label}-{time_label}")

    total_ticks = len(categories)
    step = max(1, total_ticks // 25)
    
    show_indices = list(range(0, total_ticks, step))
    show_labels = [x_labels[i] for i in show_indices]

    plt.xticks(show_indices, show_labels, rotation=45, ha='right', fontname="Arial", fontsize=18)

    # plt.title(f"Compound {compound_name} in volunteer 2", fontname="Arial")
    # plt.xlabel("DateTime", fontname="Arial")
    plt.ylabel("Relative metabolite abundance", fontname="Arial",fontsize=20)
    plt.yticks(fontsize=18, fontname="Arial")
    
    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_linewidth(2.5)

    ax.tick_params(width=2.5)

    from matplotlib.font_manager import FontProperties
    from matplotlib.lines import Line2D
    
    fp = FontProperties(family='Arial', size=18)

    handles, labels = plt.gca().get_legend_handles_labels()
    

    seen_labels = set()
    for _, label_en in time_label_list:
        if label_en not in seen_labels:
            color = label_colors.get(label_en, 'gray')

            custom_line = Line2D([0], [0], color=color, linestyle='--', lw=2.5, label=label_en)
            handles.append(custom_line)
            seen_labels.add(label_en)
            
    plt.legend(handles=handles, prop=fp)
    # ------------------------------------
    
    plt.tight_layout()

    clean_name = re.sub(r'[\\/*?:"<>|,\']', "", compound_name)
    clean_name = clean_name[:100]
    output_path = os.path.join(output_dir, f"{0+idx}_{clean_name}_plot.png")
    plt.savefig(output_path, dpi=1000, bbox_inches='tight')
    plt.close()

