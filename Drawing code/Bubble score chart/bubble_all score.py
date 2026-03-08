import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.colors import LinearSegmentedColormap, Normalize

plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False 


def load_data(filepath):
    df = pd.read_excel(filepath)
    return df.sort_values('score', ascending=False)


def plot_labeled_bubble(df, output_folder='output', top_n=15):
    data = df.head(top_n).copy()
    os.makedirs(output_folder, exist_ok=True)
    fig, ax = plt.subplots(figsize=(20, 26))
    colors = ["darkblue", "white", "darkred"]
    custom_cmap = LinearSegmentedColormap.from_list("blue_red", colors)
    norm = Normalize(vmin=data['score'].min(), vmax=data['score'].max())
    color_values = custom_cmap(norm(data['score']))

    scatter = ax.scatter(
        x=data['score'],
        y=np.arange(len(data)),
        s=data['score'] * 500,
        c=color_values,
        alpha=0.85,
        edgecolor='white',
        linewidth=0.8
    )


    ax.set_yticks(np.arange(len(data)))
    ax.set_yticklabels(data['Biomarker Name'], fontsize=55, fontname="Arial")


    for i, (count, name) in enumerate(zip(data['score'], data['Biomarker Name'])):
        ax.text(
            count + data['score'].max() * 0.03,
            i,
            f"{count}",
            va='center',
            ha='left',
            fontsize=40,
            color='black',
            weight='bold',
            fontname="Arial"
        )


        from mpl_toolkits.axes_grid1 import make_axes_locatable

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="10%", pad=0.2) 

        cbar = fig.colorbar(
            plt.cm.ScalarMappable(norm=norm, cmap=custom_cmap),
            cax=cax
        )
        # cbar.set_label('Score', fontsize=20, fontname="Arial")
        for t in cbar.ax.get_yticklabels():
            t.set_fontname("Arial")
            t.set_fontsize(50)

    
    # ax.set_title(f'Top {top_n} Biomarkers by Score',
    #              fontsize=26, pad=25, color='#333366', fontname="Arial")
    ax.set_xlabel('Score', fontsize=55, fontname="Arial")
    ax.set_ylabel('Biomarker Name', fontsize=55, fontname="Arial")
    ax.set_xlim(4.5, data['score'].max() * 1.1)
    ax.grid(True, linestyle=':', alpha=0.3, color='#dddddd')
    ax.tick_params(axis='x', labelsize=55)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')


    output_path = os.path.join(output_folder, 'all score.png')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()


if __name__ == "__main__":
    try:
        input_file = ""
        output_dir = ""

        df = load_data(input_file)
        plot_labeled_bubble(df, output_folder=output_dir)
    except FileNotFoundError:
        print(f"Error: Input file {input_file} not found. Please check the path.")
    except PermissionError:
        print(f"Error: No write permission for output directory {output_dir}")
    except Exception as e:
        print(f"An unknown error occurred: {str(e)}")
