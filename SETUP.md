# Setup

1. Create a public GitHub repository named exactly `jankibananki` under the `jankibananki` account.
2. Upload everything from this folder to the repository root, including the hidden `.github` directory.
3. Keep `profile-hero.svg`, `contrib-heatmap.svg`, and `README.md` in the same folder.
4. Enable GitHub Actions if GitHub asks for permission. The workflow refreshes the contribution heatmap.

## Important

The README now uses a single integrated hero image instead of two separate 49% images. This prevents the ASCII portrait and information panel from becoming misaligned or uneven in GitHub's renderer.

To change the displayed ASCII later, replace `jana-ascii.txt` and rerun `scripts/build_profile.py`.
