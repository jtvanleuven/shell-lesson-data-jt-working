# shell-lesson-data

Working data and exercises for an intro course on Unix, Git, and R.

## Live Website

This repo is published via GitHub Pages:

**https://jtvanleuven.github.io/shell-lesson-data-jt-working/**

## Repository Contents

```
shell-lesson-data-jt-working/
├── index.html                  # Landing page (GitHub Pages entry point)
├── gapminder-explorer.html     # Interactive Gapminder data explorer
├── gapminder_data.csv          # Raw Gapminder dataset (142 countries, 1952-2007)
├── sorted.sh                   # Shell script exercises
├── north-pacific-gyre/         # "Goo" measurement data (17 files, 10 samples)
│   ├── NENE*.txt               #   One floating-point value per line
│   ├── goodiff.sh              #   (incomplete) file comparator script
│   └── goostats.sh             #   Stats script for goo data
├── exercise-data/              # General shell lesson exercise files
│   ├── alkanes/                #   PDB files (methane, ethane, propane, ...)
│   ├── animal-counts/          #   CSV data
│   ├── creatures/              #   Data files (unicorn, basilisk, minotaur)
│   ├── writing/                #   Text files for word-counting exercises
│   └── ...
└── .gitignore                  # Excludes *.fasta (uniprot_sprot.fasta ~288 MB)
```

## Data Explorers

### Gapminder Explorer
Interactive visualization of the classic Gapminder dataset:
- Bubble chart: GDP per capita vs life expectancy, sized by population
- Trend lines over time for any selection of countries
- Sortable data table
- Filter by continent, scrub through years

### North Pacific Gyre
Raw measurement data from 10 marine samples with A/B replicates (300 observations each).
Explore with shell commands:

```bash
cd north-pacific-gyre

# Count lines in all data files
wc -l *.txt

# Find the maximum value across all files
cat *.txt | sort -n | tail -1

# Mean of a single file
awk '{sum+=$1; n++} END {print sum/n}' NENE01729A.txt

# Compare two replicate files side by side
paste NENE01729A.txt NENE01729B.txt | head -10
```

### Known Data Issues

| File | Issue |
|---|---|
| `NENE02018B.txt` | Truncated — 240 lines instead of 300 |
| `NENE01971Z.txt` | Extreme outlier (11.08 at line 206, ~10σ above mean) |
| `NENE01843B.txt` | Had scientific notation (fixed: `8.285e-05` → `0.00008285`) |
| Missing replicates | Samples 01736, 01812 (A only); 02018 (B only); 01971 (Z only) |

## Shell Script Exercises

- `sorted.sh` — sorting and text processing
- `north-pacific-gyre/goodiff.sh` — file comparison (incomplete stub)
- `north-pacific-gyre/goostats.sh` — compute stats from input data

## Requirements

- The HTML explorers are fully self-contained (data embedded) — just open in a browser.
- Shell exercises require `bash`, `awk`, `sort`, `cut`, `paste` (all standard Unix tools).
