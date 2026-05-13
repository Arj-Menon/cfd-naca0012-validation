# CFD Validation: NACA 0012 Airfoil External Aerodynamics

*A systematic validation of RANS turbulence models (SST k-ω and Spalart-Allmaras) against benchmark experimental data for the NACA 0012 airfoil at Re = 6×10⁶, M = 0.15.*

---

## Engineering Question

*What is the accuracy of SST k-ω and Spalart-Allmaras turbulence models in predicting lift, drag, and surface pressure distributions for the NACA 0012 airfoil across a range of angles of attack, and where does each model break down?*

---

## Methodology

### Geometry
*Brief description of NACA 0012 profile, chord length used, and any geometry simplifications.*

### Mesh
- **Topology:** C-grid, far-field radius = 50c
- **Surface resolution:** Three grids — ~150 / ~250 / ~400 surface cells (coarse / medium / fine)
- **Wall treatment:** y⁺ < 1 (resolved to viscous sublayer)
- **Inflation layers:** 35 layers, growth ratio 1.2
- *Add: brief note on mesh generation tool (ANSYS Meshing / ICEM CFD) and any notable decisions.*

### Boundary Conditions
| Boundary | Type | Value |
|---|---|---|
| Inlet | Velocity inlet | M = 0.15, Re = 6×10⁶ |
| Outlet | Pressure outlet | p = 0 (gauge) |
| Airfoil wall | No-slip | Adiabatic |
| Far-field (C-grid wrap) | Velocity inlet / pressure outlet | *specify* |

*Note on fully turbulent BL assumption — no transition model used.*

### Solver Settings
- **Solver:** ANSYS Fluent, pressure-based, steady-state
- **Scheme:** *e.g., SIMPLE / Coupled; spatial discretisation choices*
- **Convergence:** *residual targets and monitor quantities used*

### Turbulence Models
- SST k-ω (Menter, 1994) — *one-line rationale for selection*
- Spalart-Allmaras (1992) — *one-line rationale for selection*

### AoA Sweep
α = 0°, 4°, 8°, 10°, 12° (fully turbulent, no stall hysteresis study)

---

## Results

### Lift and Drag Polars (C_l, C_d vs α)
*Insert figure: `figures/cl_cd_polar.png`*

*Brief prose — e.g., which model tracks Ladson (1988) better at low vs high AoA.*

### Surface Pressure Distributions (C_p vs x/c)
*Insert figures: `figures/cp_alpha_XX.png` for each AoA.*

*Brief prose — e.g., suction peak agreement, trailing edge separation onset.*

### Drag Decomposition
*Optional — if extracted: pressure drag vs skin friction drag breakdown.*

---

## Validation Against Experimental Data

| Dataset | Quantity | Source |
|---|---|---|
| Ladson et al. (1988) | C_l, C_d vs α | NASA TM-4074 |
| Gregory & O'Reilly (1970) | C_p distributions | NASA R&M 3726 |

*Data obtained from the [NASA Langley Turbulence Modeling Resource](https://turbmodels.larc.nasa.gov/naca0012_val.html).*

*Summary table: % error in C_l and C_d at each AoA for both turbulence models.*

---

## Mesh Sensitivity / GCI Study

| Grid | Surface Cells | C_l (α=8°) | C_d (α=8°) |
|---|---|---|---|
| Coarse | ~150 | — | — |
| Medium | ~250 | — | — |
| Fine | ~400 | — | — |

*GCI computed per Roache (1994) methodology. Report observed order of accuracy, GCI fine, and whether asymptotic range is achieved.*

---

## Discussion

### Turbulence Model Comparison
*Where does SST k-ω outperform SA, and vice versa? Focus on: attached flow regime, onset of separation (α = 10–12°), drag prediction accuracy.*

### Limitations
*Fully turbulent assumption vs real transition; 2D simulation vs 3D effects; steady RANS limitations near stall; mesh resolution trade-offs.*

---

## Conclusions

*2–3 sentences summarising the key finding: which model is more reliable for this flow, at what AoA range, and what the GCI study implies about solution confidence.*

---

## Repository Structure

```
cfd-naca0012-validation/
├── README.md
├── .gitignore
├── docs/                  # Theory notes, methodology writeup, reference summaries
├── mesh-screenshots/      # Mesh visualisations from ANSYS Meshing / Fluent
├── data/                  # Raw exports from Fluent (Cp, force coefficients, residuals)
├── scripts/               # Python post-processing scripts
├── figures/               # Final plots for README
└── references/            # Ladson 1988, Gregory & O'Reilly 1970, NASA TMR data files
```

---

## References

1. C. L. Ladson, C. W. Brooks Jr., A. S. Hill, and D. W. Sproles, "Computer program to obtain ordinates for NACA airfoils," NASA TM-4074, 1988.
2. N. Gregory and C. L. O'Reilly, "Low-speed aerodynamic characteristics of NACA 0012 aerofoil section, including the effects of upper-surface roughness simulating hoar frost," NASA R&M 3726, 1970.
3. NASA Langley Turbulence Modeling Resource, NACA 0012 Validation Cases. [Online]. Available: https://turbmodels.larc.nasa.gov/naca0012_val.html
4. F. R. Menter, "Two-equation eddy-viscosity turbulence models for engineering applications," *AIAA Journal*, vol. 32, no. 8, pp. 1598–1605, 1994.
5. P. R. Spalart and S. R. Allmaras, "A one-equation turbulence model for aerodynamic flows," *La Recherche Aérospatiale*, no. 1, pp. 5–21, 1994.
6. P. J. Roache, "Perspective: A method for uniform reporting of grid refinement studies," *Journal of Fluids Engineering*, vol. 116, pp. 405–413, 1994.
