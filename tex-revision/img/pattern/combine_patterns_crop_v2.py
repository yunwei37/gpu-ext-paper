#!/usr/bin/env python3
"""
v2: Reuse v1's crop+resize logic, then add tick numbers with matplotlib.
Reads v1's crop boundaries, produces individual subplot images,
overlays larger axis ticks and colorbar numbers.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from pathlib import Path
from PIL import Image

mpl.rcParams['pdf.compression'] = 0

SCRIPT_DIR = Path(__file__).parent

# Same crop boundaries as v1
WORKLOADS = [
    ("faiss-build",       "(a) FAISS Build",   (50, 398, 131, 774)),
    ("faiss-query",       "(b) FAISS Query",   (53, 418, 137, 813)),
    ("llama.cpp-prefill", "(c) LLaMA Prefill", (42, 342, 112, 666)),
    ("llama.cpp-decode",  "(d) LLaMA Decode",  (66, 504, 178, 986)),
    ("pytorch-dnn",       "(e) GNN Training",  (72, 536, 96, 957)),
]

TARGET_HEIGHT = 400  # same as v1

# Axis ranges and colorbar ranges read from original images
AXIS_INFO = {
    'faiss-build':      {'x': (0, 25000), 'xt': [0, 10000, 20000],  'xl': ['0','10k','20k'], 'cbar': (0, 350)},
    'faiss-query':      {'x': (0, 25000), 'xt': [0, 10000, 20000],  'xl': ['0','10k','20k'], 'cbar': (0, 350)},
    'llama.cpp-prefill': {'x': (0, 16000), 'xt': [0, 8000, 16000],  'xl': ['0','8k','16k'],  'cbar': (0, 5000)},
    'llama.cpp-decode':  {'x': (0, 13000), 'xt': [0, 6000, 12000],  'xl': ['0','6k','12k'],  'cbar': (0, 700)},
    'pytorch-dnn':      {'x': (0, 25000), 'xt': [0, 10000, 20000],  'xl': ['0','10k','20k'], 'cbar': (0, 3500)},
}

TICK_FS = 5
LABEL_FS = 6.5
TITLE_FS = 7


def load_v1_crop(wdir, crop_box):
    """Replicate v1's crop + resize to TARGET_HEIGHT."""
    top, bottom, left, right = crop_box
    img = Image.open(str(SCRIPT_DIR / wdir / "page-fault-pattern.png"))
    cropped = img.crop((left, top, right, bottom))
    w, h = cropped.size
    new_w = int(w * TARGET_HEIGHT / h)
    resized = cropped.resize((new_w, TARGET_HEIGHT), Image.LANCZOS)
    return np.array(resized)


def main():
    # Load all v1 crops
    crops = []
    for wdir, label, crop_box in WORKLOADS:
        crops.append(load_v1_crop(wdir, crop_box))

    # Width ratios from resized pixel widths (all same height)
    width_ratios = [c.shape[1] for c in crops]

    ncols = len(WORKLOADS)
    fig, axes = plt.subplots(1, ncols, figsize=(7.0, 1.5), dpi=600,
                             gridspec_kw={'width_ratios': width_ratios})

    for idx, ((wdir, label, _), crop) in enumerate(zip(WORKLOADS, crops)):
        ax = axes[idx]
        img_h, img_w = crop.shape[:2]
        info = AXIS_INFO[wdir]

        # Display the v1 crop as-is
        ax.imshow(crop, interpolation='bilinear')

        # --- X ticks at pixel positions ---
        xmin, xmax = info['x']
        xt_pixels = [img_w * (v - xmin) / (xmax - xmin) for v in info['xt']]
        ax.set_xticks(xt_pixels)
        ax.set_xticklabels(info['xl'], fontsize=TICK_FS)
        ax.tick_params(axis='x', pad=1, length=2, width=0.4)

        # --- Y axis: no numbers, just label on leftmost ---
        ax.set_yticks([])
        if idx == 0:
            ax.set_ylabel("Virtual Address →", fontsize=LABEL_FS, labelpad=1,
                          rotation=90)

        ax.set_xlabel("Time (ms)", fontsize=LABEL_FS, labelpad=1)
        ax.set_title(label, fontsize=TITLE_FS, pad=2)

        # No border
        for spine in ax.spines.values():
            spine.set_visible(False)

        # --- Colorbar numbers on right edge ---
        # The color gradient is already in the image (from v1 crop).
        # Add min at bottom-right, max at top-right.
        cmin, cmax = info['cbar']
        ax.text(img_w * 1.01, img_h - 1, str(int(cmin)),
                fontsize=TICK_FS - 0.5, ha='left', va='bottom')
        ax.text(img_w * 1.01, 0, str(int(cmax)),
                fontsize=TICK_FS - 0.5, ha='left', va='top')

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.18)

    for fmt in ("png", "pdf"):
        out = SCRIPT_DIR / f"combined_patterns_1x5_v2.{fmt}"
        fig.savefig(out, dpi=600, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        print(f"Saved: {out}")
    plt.close(fig)


if __name__ == "__main__":
    main()
