#!/usr/bin/env python3
"""
Crop heatmap+colorbar from each page-fault-pattern.png,
combine into 1x5 using pure PIL (no matplotlib imshow distortion).
Add labels with matplotlib text only.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from pathlib import Path
from PIL import Image

mpl.rcParams['pdf.compression'] = 0

SCRIPT_DIR = Path(__file__).parent

# (dir, label, crop (top, bottom, left, right))
WORKLOADS = [
    ("faiss-build",       "(a) FAISS Build",   (50, 398, 131, 774)),
    ("faiss-query",       "(b) FAISS Query",   (53, 418, 137, 813)),
    ("llama.cpp-prefill", "(c) LLaMA Prefill", (42, 342, 112, 666)),
    ("llama.cpp-decode",  "(d) LLaMA Decode",  (66, 504, 178, 986)),
    ("pytorch-dnn",       "(e) GNN Training",  (72, 536, 96, 957)),
]

TARGET_HEIGHT = 400  # all crops resized to this height
GAP = 8  # pixels between images


def main():
    crops = []
    for wdir, label, (top, bottom, left, right) in WORKLOADS:
        img = Image.open(str(SCRIPT_DIR / wdir / "page-fault-pattern.png"))
        cropped = img.crop((left, top, right, bottom))
        # Resize to uniform height, preserve aspect ratio
        w, h = cropped.size
        new_w = int(w * TARGET_HEIGHT / h)
        resized = cropped.resize((new_w, TARGET_HEIGHT), Image.LANCZOS)
        crops.append(resized)

    # Combine horizontally with gaps
    total_w = sum(c.width for c in crops) + GAP * (len(crops) - 1)
    combined = Image.new('RGB', (total_w, TARGET_HEIGHT), (255, 255, 255))
    x = 0
    centers = []  # x-centers for labels
    for c in crops:
        combined.paste(c, (x, 0))
        centers.append(x + c.width // 2)
        x += c.width + GAP

    # Now use matplotlib ONLY for adding text labels around the combined image
    # The image is placed as-is, no imshow resampling
    fig_width = 7.0  # paper \textwidth
    fig_height = fig_width * TARGET_HEIGHT / total_w
    # Add room for title and xlabel
    title_frac = 0.12
    xlabel_frac = 0.10
    total_height = fig_height / (1 - title_frac - xlabel_frac)

    fig = plt.figure(figsize=(fig_width, total_height), dpi=600)
    # Image area
    ax = fig.add_axes([0.04, xlabel_frac, 0.96, 1 - title_frac - xlabel_frac])
    ax.imshow(np.array(combined), interpolation='none', aspect='auto')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylabel("Virtual Addr.", fontsize=7, labelpad=2)

    # Add subplot titles and "Time" labels at image coordinates
    labels = [w[1] for w in WORKLOADS]
    for cx, label in zip(centers, labels):
        # Title above
        ax.text(cx, -TARGET_HEIGHT * 0.04, label, fontsize=7.5,
                ha='center', va='bottom', transform=ax.transData)
        # "Time" below
        ax.text(cx, TARGET_HEIGHT * 1.03, "Time", fontsize=7,
                ha='center', va='top', transform=ax.transData)

    for spine in ax.spines.values():
        spine.set_visible(False)

    for fmt in ("png", "pdf"):
        out = SCRIPT_DIR / f"combined_patterns_1x5_crop.{fmt}"
        fig.savefig(out, dpi=600, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        print(f"Saved: {out}")
    plt.close(fig)


if __name__ == "__main__":
    main()
