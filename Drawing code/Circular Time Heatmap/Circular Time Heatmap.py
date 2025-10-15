import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import matplotlib.patheffects as PathEffects
import matplotlib.patches as mpatches


plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False


df = pd.read_csv(r'D:\Desktop\time_cycle\z.csv')
food_df = pd.read_csv(r'D:\Desktop\time_cycle\metabolites.csv')


additional_coffee_metabolites = [
    # "1,7-Dimethylxanthine",
    # "1-Methylxanthine",
]


molecule_to_food = dict(zip(food_df['Name'], food_df['food']))
for mol in additional_coffee_metabolites:
    molecule_to_food[mol] = 'coffee'

#sort
df['sort_key'] = df['date'].astype(str) + ' ' + df['hour']
df = df.sort_values('sort_key')

molecule_cols = [col for col in df.columns if col not in ['date', 'hour', 'sort_key']]

time_labels = [f"{h}" for d, h in zip(df['date'], df['hour'])]

# Z-score
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

coffee_keywords = ['caffeine', 'methylxanthine', 'dimethylxanthine', 'theobromine', 'theophylline',
                   'caffeic', 'ferulic', 'quinic', 'chlorogenic']
chocolate_keywords = ['catechin', 'epicatechin', 'theobromine', 'gallic', 'cianidanol']
banana_keywords = ['dopamine', 'serotonin', 'tryptophan', 'tryptamine']

unknown_metabolites = [mol for mol in molecule_cols if molecule_to_food.get(mol, 'unknown') == 'unknown']
for mol in unknown_metabolites:
    mol_lower = mol.lower()
    if any(keyword in mol_lower for keyword in coffee_keywords):
        food_molecules['coffee'].append(mol)
        molecule_to_food[mol] = 'coffee'
    elif any(keyword in mol_lower for keyword in chocolate_keywords):
        food_molecules['chocolate'].append(mol)
        molecule_to_food[mol] = 'chocolate'
    elif any(keyword in mol_lower for keyword in banana_keywords):
        food_molecules['banana'].append(mol)
        molecule_to_food[mol] = 'banana'


gap_size = 3

fig = plt.figure(figsize=(14, 14))
ax = fig.add_subplot(111, projection='polar')
ax.grid(False)
ax.xaxis.grid(False)
ax.yaxis.grid(False)

theta = np.linspace(0, 5 * np.pi / 3, len(time_labels), endpoint=False)
norm = TwoSlopeNorm(vmin=-3, vcenter=0, vmax=3)
cmap = plt.cm.seismic

current_radius = 1

for food_idx, food in enumerate(food_order):
    molecules = food_molecules[food]
    if not molecules:
        continue

    start_radius = current_radius
    for mol in molecules:
        values = zscore_data[mol].values
        ax.bar(theta, np.ones_like(theta) * 0.8,
               width=5 * np.pi / (3 * len(theta)),
               bottom=current_radius,
               color=cmap(norm(values)), edgecolor='none', alpha=0.9)
        current_radius += 1

    end_radius = current_radius

    outer_circle = mpatches.Circle((0, 0), radius=end_radius,
                                   transform=ax.transData._b,
                                   fill=False, color=food_colors[food],
                                   linewidth=2.5)
    ax.add_patch(outer_circle)

    inner_circle = mpatches.Circle((0, 0), radius=start_radius - 0.5,
                                   transform=ax.transData._b,
                                   fill=False, color=food_colors[food],
                                   linewidth=2.5)
    ax.add_patch(inner_circle)

    if food_idx < len(food_order) - 1:
        current_radius += gap_size

ax.set_yticklabels([])
ax.set_thetamin(-10)
ax.set_thetamax(290)
max_r = current_radius + 8
ax.set_rmax(max_r)

ax.set_xticks(theta)
ax.set_xticklabels([])
label_radius = current_radius + 2.5
for angle, label in zip(theta, time_labels):
    rotation_angle = np.degrees(angle)
    if 0 <= rotation_angle <= 180:
        rotation = rotation_angle - 90
        ha, va = 'right', 'center'
    else:
        rotation = rotation_angle - 270
        ha, va = 'left', 'center'

    text = ax.text(angle, label_radius, label,
                   rotation=rotation, fontsize=15,
                   rotation_mode='anchor', ha=ha, va=va,
                   fontname="Arial")
    text.set_path_effects([PathEffects.withStroke(linewidth=3, foreground='white')])

cbaxes = fig.add_axes([0.92, 0.25, 0.02, 0.5])
cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cbaxes)
cb.set_label('Z-score', fontsize=12, fontname="Arial")
cb.ax.tick_params(labelsize=10)
for t in cb.ax.get_yticklabels():
    t.set_fontname("Arial")

plt.subplots_adjust(right=0.88)
plt.savefig(r'', dpi=300, bbox_inches='tight')


updated_mapping = [{'Name': mol, 'food': molecule_to_food.get(mol, 'unknown')} for mol in molecule_cols]
pd.DataFrame(updated_mapping).to_csv(r'D:\Desktop\time_cycle\updated_metabolites.csv', index=False)
