import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import matplotlib.patheffects as PathEffects
import matplotlib.patches as mpatches


plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False


df = pd.read_excel('')
metabolites = pd.read_excel('')
molecule_to_food = dict(zip(metabolites['Name'], metabolites['food']))


# Ensure hour is string before concatenation
df['sort_key'] = df['date'].astype(str) + ' ' + df['hour'].astype(str)
df = df.sort_values('sort_key')


molecule_cols = [col for col in df.columns if col not in ['date', 'hour', 'sort_key']]

time_labels = [str(h)[:5] for h in df['hour']]

zscore_data = pd.DataFrame()
for col in molecule_cols:
    log_values = np.log1p(df[col])
    zscore_data[col] = (log_values - log_values.mean()) / log_values.std() if log_values.std() != 0 else 0


food_order = ['coffee', 'chocolate', 'banana']
food_colors = {
    'coffee': '#FF4B4B',
    'chocolate': '#4B7BFF',
    'banana': '#9D4EDD'
}

food_molecules = {food: [] for food in food_order}
for mol in molecule_cols:
    food = molecule_to_food.get(mol, 'unknown')
    if food in food_order:
        food_molecules[food].append(mol)



theta = np.linspace(0, 5 * np.pi / 3, len(time_labels), endpoint=False)
norm = TwoSlopeNorm(vmin=-3, vcenter=0, vmax=3)
cmap = plt.cm.seismic

for food in food_order:
    molecules = food_molecules[food]
    if not molecules:
        continue
    
   
    n_mols = len(molecules)
    if n_mols <= 5:
        scale_factor = 6.0  
    elif n_mols <= 10:
        scale_factor = 3.5
    elif n_mols <= 20:
        scale_factor = 2.0
    else:
        scale_factor = 1.2
        

    radius_step = 1.0 * scale_factor
    bar_height = 0.9 * scale_factor 


    fig = plt.figure(figsize=(14, 14))
    ax = fig.add_subplot(111, projection='polar')
    ax.grid(False)
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)
    current_radius = 2.0 * scale_factor 
    start_radius = current_radius
    legend_labels = []
    print(f"\nFood Group: {food} - Plotting Order (Inner ring -> Outer ring):")

    for i, mol in enumerate(molecules):
        print(f"  Ring {i+1}: {mol}")
        legend_labels.append(f"{i+1}. {mol}")
        
        values = zscore_data[mol].values
        ax.bar(theta, np.ones_like(theta) * bar_height,
               width=5 * np.pi / (3 * len(theta)),
               bottom=current_radius,
               color=cmap(norm(values)), edgecolor='none', alpha=0.9)
        current_radius += radius_step

    end_radius = current_radius
    
    outer_circle = mpatches.Circle((0, 0), radius=end_radius,
                                   transform=ax.transData._b,
                                   fill=False, color=food_colors[food],
                                   linewidth=3.0 * np.sqrt(scale_factor))

    inner_circle = mpatches.Circle((0, 0), radius=start_radius - (0.1 * scale_factor), 
                                   transform=ax.transData._b,
                                   fill=False, color=food_colors[food],
                                   linewidth=3.0 * np.sqrt(scale_factor))
    ax.add_patch(inner_circle)


    ax.set_yticklabels([])
    ax.set_thetamin(-10)
    ax.set_thetamax(290)
    
    label_offset = 1.0 * scale_factor 
    label_radius = end_radius + label_offset 
    max_r = label_radius + (1.5 * scale_factor) 
    ax.set_rmax(max_r)
    ax.set_xticks(theta)
    ax.set_xticklabels([])
    
    for angle, label in zip(theta, time_labels):
        rotation_angle = np.degrees(angle)
        if 0 <= rotation_angle <= 180:
            rotation = rotation_angle - 90
            ha, va = 'right', 'center'
        else:
            rotation = rotation_angle - 270
            ha, va = 'left', 'center'

        font_size = 18 + (scale_factor * 1.5) 
        text = ax.text(angle, label_radius, label,
                       rotation=rotation, fontsize=font_size,
                       rotation_mode='anchor', ha=ha, va=va,
                       fontname="Arial")  
        text.set_path_effects([PathEffects.withStroke(linewidth=3, foreground='white')])

    cbaxes = fig.add_axes([0.92, 0.25, 0.02, 0.5])
    cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cbaxes)

    cb.set_label('Z-score', fontsize=24 + scale_factor, fontname="Arial")
    cb.ax.tick_params(labelsize=20 + scale_factor)
    for t in cb.ax.get_yticklabels():
        t.set_fontname("Arial")

    plt.subplots_adjust(right=0.85, left=0.05, bottom=0.05, top=0.95) 
    save_path = rf'X:\X\X{food}.eps'
    plt.savefig(save_path, dpi=1000, bbox_inches='tight')
    plt.close(fig)


