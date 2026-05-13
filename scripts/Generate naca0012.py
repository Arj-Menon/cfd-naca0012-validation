"""
================================================================================
NACA 0012 Coordinate Generator
================================================================================
Purpose  : Generate NACA 0012 airfoil coordinates analytically using the
           standard 4-digit NACA thickness equation. Export in Selig format
           for import into ANSYS SpaceClaim / Fluent. Compare against UIUC
           Airfoil Database reference (n0012.dat) to verify geometric accuracy.

Author   : Arjun Menon
Project  : CFD Portfolio — Project 2 (External Aerodynamics, NACA 0012)
Reference: Ladson et al. (1988), NASA TM-4074

Inputs   : t = 0.12      (thickness ratio, NACA 0012)
           c = 1.0 m     (chord length)
           N = 200       (points per surface, cosine-spaced)
           n0012.dat     (UIUC reference, place in same directory)

Outputs  : output/naca0012_generated.dat  — Selig-format coordinate file
           output/naca0012_geometry.png   — Geometry verification plot
           output/naca0012_comparison.png — Overlay vs UIUC reference

Usage    : python generate_naca0012.py
           Download n0012.dat from:
           https://m-selig.ae.illinois.edu/ads/coord_database.html
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# ── FUNCTION 1: Generate NACA 4-digit coordinates ───────────────────────────
def generate_naca4(t, c, N):
    """
    Generate NACA 4-digit symmetric airfoil coordinates using cosine spacing.

    Parameters
    ----------
    t : float  — thickness ratio (0.12 for NACA 0012)
    c : float  — chord length in metres (1.0)
    N : int    — number of points along ONE surface (200)

    Returns
    -------
    x       : 1D array, shape (N,), chord-wise positions 0 → c
    y_upper : 1D array, shape (N,), upper surface y-coordinates
    y_lower : 1D array, shape (N,), lower surface y-coordinates
    """
    # Cosine spacing: parametrize by angle theta, 0 → pi
    # Near theta=0 and theta=pi (LE and TE), points cluster automatically
    theta = np.linspace(0, np.pi, N)
    x = (c / 2) * (1 - np.cos(theta))   # x in [0, c]

    # Normalised chord coordinate (dimensionless)
    xc = x / c

    # NACA 4-digit half-thickness equation (open trailing edge)
    # Coefficient -0.1015 gives non-zero TE thickness — matches Ladson geometry
    y_t = (t / 0.2) * c * (
          0.2969 * np.sqrt(xc)
        - 0.1260 * xc
        - 0.3516 * xc**2
        + 0.2843 * xc**3
        - 0.1015 * xc**4
    )

    # Symmetric airfoil: upper = +y_t, lower = -y_t
    y_upper =  y_t
    y_lower = -y_t

    return x, y_upper, y_lower


# ── FUNCTION 2: Assemble Selig-format coordinate array ──────────────────────
def to_selig(x, y_upper, y_lower):
    """
    Re-order coordinates into Selig format:
    TE → upper surface → LE → lower surface → TE (single closed loop)

    Parameters
    ----------
    x       : 1D array, 0 → c (LE to TE)
    y_upper : 1D array, upper surface
    y_lower : 1D array, lower surface

    Returns
    -------
    coords : 2D array, shape (2*N - 1, 2), columns = [x, y]
    """
    # Upper surface: must go TE → LE, so reverse x and y_upper
    upper = np.column_stack([x[::-1], y_upper[::-1]])   # shape (N, 2)

    # Lower surface: goes LE → TE (same order as x)
    # Skip first point [1:] — LE already included at end of upper block
    lower = np.column_stack([x[1:], y_lower[1:]])       # shape (N-1, 2)

    # Concatenate vertically: upper block then lower block
    coords = np.concatenate([upper, lower], axis=0)     # shape (2N-1, 2)

    return coords


# ── FUNCTION 3: Load UIUC reference coordinate file ─────────────────────────
def load_uiuc(filepath):
    """
    Load a UIUC airfoil .dat file — handles both Selig and Lednicer formats.

    Lednicer format (what n0012.dat uses):
      Line 1: airfoil name
      Line 2: "N_upper.  N_lower."  (point counts, NOT data)
      Lines 3+: upper surface LE->TE, then lower surface LE->TE

    Selig format:
      Line 1: airfoil name
      Lines 2+: continuous loop TE->upper->LE->lower->TE

    Detection: if line 2 has two tokens that are round numbers, it is Lednicer.
    Returns x, y as combined 1D arrays covering the full airfoil.
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Lednicer detection: line 2 tokens are point counts (e.g. "66.  66.")
    line2_tokens = lines[1].strip().split()
    is_lednicer = (
        len(line2_tokens) == 2 and
        all(tok.replace('.', '').isdigit() for tok in line2_tokens)
    )

    if is_lednicer:
        n_upper = int(float(line2_tokens[0]))
        n_lower = int(float(line2_tokens[1]))
        print(f"[INFO] Lednicer format detected: {n_upper} upper, {n_lower} lower points")

        data = np.loadtxt(filepath, skiprows=2)

        upper = data[:n_upper]        # first n_upper rows = upper surface
        lower = data[n_upper:]        # remaining = lower surface

        # Combine both surfaces; skip LE duplicate at lower[0]
        x = np.concatenate([upper[:, 0], lower[1:, 0]])
        y = np.concatenate([upper[:, 1], lower[1:, 1]])

    else:
        print("[INFO] Selig format detected")
        data = np.loadtxt(filepath, skiprows=1)
        x = data[:, 0]
        y = data[:, 1]

    return x, y


# ── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # ── Parameters ──────────────────────────────────────────────────────────
    t = 0.12    # NACA 0012 thickness ratio
    c = 1.0     # chord length [m]
    N = 200     # points per surface

    # ── Generate ─────────────────────────────────────────────────────────────
    x, y_upper, y_lower = generate_naca4(t, c, N)
    coords_selig = to_selig(x, y_upper, y_lower)

    # ── Output directory ─────────────────────────────────────────────────────
    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)

    # ── Save .dat file ───────────────────────────────────────────────────────
    out_path = out_dir / "naca0012_generated.dat"
    np.savetxt(
        out_path,
        coords_selig,
        fmt="%.6f",
        header="NACA 0012",
        comments=""        # suppress numpy's default '#' before header
    )
    print(f"[OK] Coordinate file saved: {out_path}")
    print(f"     Total points in Selig file: {coords_selig.shape[0]}")
    print(f"     TE gap (open TE check): y_TE = ±{y_upper[-1]:.6f} m")

    # ── Plot 1: Geometry verification ────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 4))

    ax.plot(x, y_upper, color='steelblue', linewidth=1.5, label='Upper surface')
    ax.plot(x, y_lower, color='steelblue', linewidth=1.5, label='Lower surface')
    ax.plot(0, 0, 'ro', markersize=8, zorder=5, label='Leading edge (x=0)')
    ax.plot(c, 0, 'gs', markersize=8, zorder=5, label='Trailing edge (x=c)')

    ax.set_aspect('equal')
    ax.set_xlabel('x [m]', fontsize=12)
    ax.set_ylabel('y [m]', fontsize=12)
    ax.set_title('NACA 0012 — Generated Geometry (Cosine Spacing, N=200)', fontsize=13)
    ax.legend(fontsize=10, loc='center left', bbox_to_anchor=(1.02, 0.5),
              bbox_transform=ax.transAxes, borderaxespad=0)
    ax.grid(True, linestyle='--', alpha=0.4)

    plt.tight_layout()
    geom_path = out_dir / "naca0012_geometry.png"
    plt.savefig(geom_path, dpi=150)
    plt.close()
    print(f"[OK] Geometry plot saved: {geom_path}")

    # ── UIUC Comparison ──────────────────────────────────────────────────────
    uiuc_path = Path("n0012.dat")

    if uiuc_path.exists():
        x_uiuc, y_uiuc = load_uiuc(uiuc_path)

        # Auto-detect percent-chord format (some UIUC files ship in 0–100 scale)
        # Threshold: if max(x) > 1.5, it's clearly percent-chord, not normalised
        if np.max(x_uiuc) > 1.5:
            print("[INFO] UIUC file in percent-chord format — rescaling by /100")
            x_uiuc = x_uiuc / 100.0
            y_uiuc = y_uiuc / 100.0

        # Deviation: compare surface-by-surface to avoid non-monotonic x issues.
        # UIUC Lednicer gives upper (LE->TE) then lower (LE->TE) concatenated.
        # We know the UIUC file has n_upper points in the upper block.
        # Re-read the count from the file directly.
        with open(uiuc_path, 'r') as _f:
            _tokens = _f.readlines()[1].strip().split()
        n_upper_uiuc = int(float(_tokens[0]))
        n_lower_uiuc = int(float(_tokens[1]))

        x_u = x_uiuc[:n_upper_uiuc]
        y_u = y_uiuc[:n_upper_uiuc]
        x_l = x_uiuc[n_upper_uiuc:]
        y_l = y_uiuc[n_upper_uiuc:]

        # Generated upper and lower are already monotonic LE->TE (x: 0->1)
        y_gen_upper_interp = np.interp(x_u, x, y_upper)
        y_gen_lower_interp = np.interp(x_l, x, y_lower)

        dev_upper = np.abs(y_gen_upper_interp - y_u)
        dev_lower = np.abs(y_gen_lower_interp - y_l)
        deviation = np.concatenate([dev_upper, dev_lower])
        x_dev     = np.concatenate([x_u, x_l])

        max_dev  = np.max(deviation)
        mean_dev = np.mean(deviation)

        print(f"\n[UIUC Comparison]")
        print(f"  Max  deviation: {max_dev:.6f} m  ({max_dev*1000:.4f} mm)")
        print(f"  Mean deviation: {mean_dev:.6f} m  ({mean_dev*1000:.4f} mm)")

        if max_dev < 1e-3:
            print("  [PASS] Max deviation < 1 mm — geometry matches UIUC reference.")
        else:
            print("  [WARN] Deviation > 1 mm — check trailing edge convention or file format.")

        # ── Plot 2: Comparison overlay + deviation ───────────────────────────
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7))

        # Subplot 1 — Airfoil overlay
        ax1.plot(x, y_upper, color='steelblue',  linewidth=2.0,
                 label='Generated (analytical, N=200)')
        ax1.plot(x, y_lower, color='steelblue',  linewidth=2.0)
        ax1.plot(x_uiuc, y_uiuc, 'o', color='tomato', markersize=3,
                 label='UIUC n0012.dat reference')
        ax1.set_aspect('equal')
        ax1.set_ylabel('y [m]', fontsize=11)
        ax1.set_title('NACA 0012 — Generated vs UIUC Reference', fontsize=13)
        ax1.legend(fontsize=10)
        ax1.grid(True, linestyle='--', alpha=0.4)

        # Subplot 2 — Deviation plot
        ax2.plot(x_dev, deviation * 1000, color='darkorange', linewidth=1.5)
        ax2.axhline(y=mean_dev * 1000, color='gray', linestyle='--',
                    linewidth=1.0, label=f'Mean = {mean_dev*1000:.4f} mm')
        ax2.set_xlabel('x/c [m]', fontsize=11)
        ax2.set_ylabel('|Δy| [mm]', fontsize=11)
        ax2.set_title('Point-wise Deviation: Generated vs UIUC', fontsize=12)
        ax2.legend(fontsize=10)
        ax2.grid(True, linestyle='--', alpha=0.4)

        plt.tight_layout()
        comp_path = out_dir / "naca0012_comparison.png"
        plt.savefig(comp_path, dpi=150)
        plt.close()
        print(f"[OK] Comparison plot saved: {comp_path}")

    else:
        print("\n[INFO] n0012.dat not found in current directory.")
        print("       Download from: https://m-selig.ae.illinois.edu/ads/coord_database.html")
        print("       Place n0012.dat alongside this script and re-run.")