#!/usr/bin/env python3
"""Build uniprot-explorer.html with embedded sample data."""
import json

# Read sample TSV
with open("/tmp/sample.tsv") as f:
    lines = [l.strip().split("\t") for l in f if l.strip()]

header = lines[0]
rows = lines[1:]

# Convert to JSON-able list of dicts
data = []
for r in rows:
    d = {}
    for i, h in enumerate(header):
        if i >= 2:
            d[h] = int(r[i])
        else:
            d[h] = r[i]
    data.append(d)

sample_json = json.dumps(data)
header_json = json.dumps(header)

html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UniProt SProt Explorer</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
:root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #242836;
    --border: #2e3348;
    --text: #e2e8f0;
    --text-dim: #8892a8;
    --accent: #6366f1;
    --accent-glow: rgba(99,102,241,0.3);
    --green: #34d399;
    --red: #f87171;
    --amber: #fbbf24;
    --cyan: #22d3ee;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    background: var(--bg);
    color: var(--text);
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 14px;
    line-height: 1.6;
}
.container { max-width: 1400px; margin: 0 auto; padding: 20px; }

/* Header */
.header {
    text-align: center;
    padding: 40px 20px 30px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
}
.header h1 {
    font-size: 28px;
    background: linear-gradient(135deg, var(--accent), var(--cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
}
.header p { color: var(--text-dim); font-size: 13px; }

/* Stats bar */
.stats-bar {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
}
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.stat-card .value {
    font-size: 24px;
    font-weight: 700;
    color: var(--accent);
}
.stat-card .label {
    font-size: 11px;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* Tabs */
.tab-bar {
    display: flex;
    gap: 4px;
    margin-bottom: 20px;
    border-bottom: 2px solid var(--border);
    padding-bottom: 0;
}
.tab-btn {
    background: none;
    border: none;
    color: var(--text-dim);
    padding: 10px 20px;
    cursor: pointer;
    font-family: inherit;
    font-size: 13px;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s;
}
.tab-btn:hover { color: var(--text); }
.tab-btn.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
}
.tab-view { display: none; }
.tab-view.active { display: block; }

/* Charts */
.chart-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 24px;
}
.chart-grid.full { grid-template-columns: 1fr; }
.chart-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
}
.chart-box h3 {
    font-size: 13px;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px;
}
.chart-box canvas { max-height: 320px; }

/* Table */
.table-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow-x: auto;
    max-height: 500px;
    overflow-y: auto;
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}
th {
    position: sticky;
    top: 0;
    background: var(--surface2);
    color: var(--text-dim);
    text-transform: uppercase;
    font-size: 10px;
    letter-spacing: 1px;
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
}
th:hover { color: var(--text); }
th .sort-arrow { margin-left: 4px; opacity: 0.5; }
td {
    padding: 8px 12px;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
}
tr:hover td { background: var(--surface2); }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
td.aa-highlight { color: var(--cyan); }

/* Search & filter */
.controls {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;
    align-items: center;
}
.search-box {
    flex: 1;
    min-width: 200px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    color: var(--text);
    font-family: inherit;
    font-size: 13px;
    outline: none;
}
.search-box:focus { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-glow); }
select {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 14px;
    color: var(--text);
    font-family: inherit;
    font-size: 13px;
    outline: none;
}
.btn {
    background: var(--accent);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-family: inherit;
    font-size: 13px;
    cursor: pointer;
    transition: opacity 0.2s;
}
.btn:hover { opacity: 0.85; }
.btn.secondary {
    background: var(--surface2);
    color: var(--text-dim);
}

/* Loading overlay */
.loading {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 12px;
    padding: 60px;
    color: var(--text-dim);
}
.spinner {
    width: 32px; height: 32px;
    border: 3px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Responsive */
@media (max-width: 768px) {
    .chart-grid { grid-template-columns: 1fr; }
    .header h1 { font-size: 20px; }
    .stats-bar { grid-template-columns: repeat(2, 1fr); }
}

/* Detail panel */
.detail-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
}
.detail-panel h3 {
    font-size: 16px;
    color: var(--accent);
    margin-bottom: 8px;
}
.detail-panel .meta {
    color: var(--text-dim);
    font-size: 12px;
    margin-bottom: 16px;
}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>UniProt SProt Explorer</h1>
        <p>575,748 proteins &middot; 14,919 organisms &middot; Amino acid composition &amp; length analysis</p>
    </div>

    <!-- Stats -->
    <div class="stats-bar" id="statsBar">
        <div class="stat-card"><div class="value" id="statProteins">575,748</div><div class="label">Proteins</div></div>
        <div class="stat-card"><div class="value" id="statOrganisms">14,919</div><div class="label">Organisms</div></div>
        <div class="stat-card"><div class="value" id="statMeanLen">363</div><div class="label">Mean Length (aa)</div></div>
        <div class="stat-card"><div class="value" id="statMaxLen">35,213</div><div class="label">Max Length</div></div>
        <div class="stat-card"><div class="value" id="statMinLen">2</div><div class="label">Min Length</div></div>
    </div>

    <!-- Tabs -->
    <div class="tab-bar">
        <button class="tab-btn active" data-tab="overview">Overview</button>
        <button class="tab-btn" data-tab="organism">Organism</button>
        <button class="tab-btn" data-tab="table">Data Table</button>
    </div>

    <!-- Overview Tab -->
    <div class="tab-view active" id="view-overview">
        <div class="chart-grid">
            <div class="chart-box">
                <h3>Global Amino Acid Composition</h3>
                <canvas id="chartAA"></canvas>
            </div>
            <div class="chart-box">
                <h3>Protein Length Distribution</h3>
                <canvas id="chartLen"></canvas>
            </div>
        </div>
        <div class="chart-grid full">
            <div class="chart-box">
                <h3>Top 20 Organisms by Protein Count</h3>
                <canvas id="chartTopOrg"></canvas>
            </div>
        </div>
    </div>

    <!-- Organism Tab -->
    <div class="tab-view" id="view-organism">
        <div class="controls">
            <select id="orgSelect" style="flex:1; min-width:300px;"></select>
            <button class="btn" id="orgGo">Explore</button>
        </div>
        <div id="orgDetail"></div>
        <div class="chart-grid" id="orgCharts" style="display:none;">
            <div class="chart-box">
                <h3>AA Composition</h3>
                <canvas id="orgAAChart"></canvas>
            </div>
            <div class="chart-box">
                <h3>Length Distribution</h3>
                <canvas id="orgLenChart"></canvas>
            </div>
        </div>
    </div>

    <!-- Table Tab -->
    <div class="tab-view" id="view-table">
        <div id="tableLoading" class="loading">
            <div class="spinner"></div>
            <span>Loading 575K rows&hellip; this may take a moment</span>
        </div>
        <div id="tableControls" style="display:none;">
            <div class="controls">
                <input class="search-box" id="tableSearch" placeholder="Search organism or protein name&hellip;">
                <select id="sortCol">
                    <option value="organism">Sort: Organism</option>
                    <option value="protein">Sort: Protein</option>
                    <option value="length">Sort: Length</option>
                </select>
                <button class="btn secondary" id="sortDir">Asc &uarr;</button>
                <span id="rowCount" style="color:var(--text-dim); font-size:12px;"></span>
            </div>
            <div class="table-wrap">
                <table id="dataTable">
                    <thead><tr id="tableHead"></tr></thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<script>
// ===================== EMBEDDED SAMPLE DATA =====================
const SAMPLE = ''' + sample_json + ''';
const COLUMNS = ''' + header_json + ''';
const AA_COLS = ["A","C","D","E","F","G","H","I","K","L","M","N","P","Q","R","S","T","V","W","Y"];
const AA_COLORS = [
    "#6366f1","#22d3ee","#34d399","#fbbf24","#f87171",
    "#a78bfa","#fb923c","#4ade80","#60a5fa","#f472b6",
    "#2dd4bf","#facc15","#c084fc","#38bdf8","#fb7185",
    "#4ade80","#fbbf24","#e879f9","#60a5fa","#a3e635"
];

let allData = null; // full dataset loaded from TSV
let charts = {};

// ===================== TABS =====================
document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-view").forEach(v => v.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById("view-" + btn.dataset.tab).classList.add("active");
        // Lazy-load full data when table tab is opened
        if (btn.dataset.tab === "table" && !allData) loadFullData();
        // Resize charts when switching tabs
        setTimeout(() => Object.values(charts).forEach(c => c && c.resize()), 50);
    });
});

// ===================== OVERVIEW CHARTS =====================
function buildOverview() {
    // Use sample data for overview (representative)
    const d = SAMPLE;

    // AA composition (sum across sample)
    const aaSums = {};
    AA_COLS.forEach(a => aaSums[a] = 0);
    d.forEach(r => AA_COLS.forEach(a => aaSums[a] += r[a]));

    charts.aa = new Chart(document.getElementById("chartAA"), {
        type: "bar",
        data: {
            labels: AA_COLS,
            datasets: [{
                label: "Residues",
                data: AA_COLS.map(a => aaSums[a]),
                backgroundColor: AA_COLORS,
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: "#8892a8" }, grid: { color: "#2e3348" } },
                y: { ticks: { color: "#8892a8" }, grid: { color: "#2e3348" } }
            }
        }
    });

    // Length distribution (sample)
    const buckets = { "<50": 0, "50-99": 0, "100-199": 0, "200-499": 0, "500-999": 0, "1000-1999": 0, "2000+": 0 };
    d.forEach(r => {
        const l = r.length;
        if (l < 50) buckets["<50"]++;
        else if (l < 100) buckets["50-99"]++;
        else if (l < 200) buckets["100-199"]++;
        else if (l < 500) buckets["200-499"]++;
        else if (l < 1000) buckets["500-999"]++;
        else if (l < 2000) buckets["1000-1999"]++;
        else buckets["2000+"]++;
    });

    charts.len = new Chart(document.getElementById("chartLen"), {
        type: "bar",
        data: {
            labels: Object.keys(buckets),
            datasets: [{
                label: "Proteins",
                data: Object.values(buckets),
                backgroundColor: "#6366f1",
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: "#8892a8" }, grid: { color: "#2e3348" } },
                y: { type: "logarithmic", ticks: { color: "#8892a8" }, grid: { color: "#2e3348" } }
            }
        }
    });

    // Top organisms (from sample, count by organism)
    const orgCount = {};
    d.forEach(r => { orgCount[r.organism] = (orgCount[r.organism] || 0) + 1; });
    const top = Object.entries(orgCount).sort((a,b) => b[1]-a[1]).slice(0, 20);

    charts.topOrg = new Chart(document.getElementById("chartTopOrg"), {
        type: "bar",
        data: {
            labels: top.map(t => t[0].length > 30 ? t[0].slice(0,30)+"..." : t[0]),
            datasets: [{
                label: "Proteins (sample)",
                data: top.map(t => t[1]),
                backgroundColor: "#22d3ee",
                borderRadius: 4,
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: "#8892a8" }, grid: { color: "#2e3348" } },
                y: { ticks: { color: "#e2e8f0", font: { size: 11 } }, grid: { display: false } }
            }
        }
    });
}

// ===================== ORGANISM VIEW =====================
function buildOrgSelect() {
    // Use full data if loaded, else sample
    const d = allData || SAMPLE;
    const orgs = {};
    d.forEach(r => { orgs[r.organism] = (orgs[r.organism] || 0) + 1; });
    const sorted = Object.entries(orgs).sort((a,b) => b[1]-a[1]);

    const sel = document.getElementById("orgSelect");
    sel.innerHTML = "<option value=''>-- Select organism --</option>" +
        sorted.map(([name, count]) =>
            `<option value="${name.replace(/"/g, '&quot;')}">${name} (${count.toLocaleString()})</option>`
        ).join("");
}

document.getElementById("orgGo").addEventListener("click", () => {
    const org = document.getElementById("orgSelect").value;
    if (!org) return;

    const d = (allData || SAMPLE).filter(r => r.organism === org);
    const detail = document.getElementById("orgDetail");
    const chartsDiv = document.getElementById("orgCharts");

    const totalLen = d.reduce((s, r) => s + r.length, 0);
    const avgLen = Math.round(totalLen / d.length);
    const maxLen = Math.max(...d.map(r => r.length));
    const minLen = Math.min(...d.map(r => r.length));

    detail.style.display = "block";
    detail.innerHTML = `
        <h3>${org}</h3>
        <div class="meta">${d.length.toLocaleString()} proteins &middot; Mean length: ${avgLen} aa &middot; Range: ${minLen} &ndash; ${maxLen} aa</div>
    `;
    chartsDiv.style.display = "grid";

    // AA composition
    const aaSums = {};
    AA_COLS.forEach(a => aaSums[a] = 0);
    d.forEach(r => AA_COLS.forEach(a => aaSums[a] += r[a]));
    const aaTotal = AA_COLS.reduce((s, a) => s + aaSums[a], 0);

    if (charts.orgAA) charts.orgAA.destroy();
    charts.orgAA = new Chart(document.getElementById("orgAAChart"), {
        type: "doughnut",
        data: {
            labels: AA_COLS,
            datasets: [{
                data: AA_COLS.map(a => Math.round(aaSums[a] / aaTotal * 1000) / 10),
                backgroundColor: AA_COLORS,
                borderWidth: 1,
                borderColor: "#1a1d27",
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: "right", labels: { color: "#8892a8", font: { size: 11 }, boxWidth: 12 } },
                tooltip: { callbacks: { label: ctx => ctx.label + ": " + ctx.raw + "%" } }
            }
        }
    });

    // Length distribution
    const bins = {};
    d.forEach(r => {
        const b = Math.floor(r.length / 50) * 50;
        bins[b] = (bins[b] || 0) + 1;
    });
    const sortedBins = Object.entries(bins).sort((a,b) => a[0]-b[0]).slice(0, 40);

    if (charts.orgLen) charts.orgLen.destroy();
    charts.orgLen = new Chart(document.getElementById("orgLenChart"), {
        type: "bar",
        data: {
            labels: sortedBins.map(b => b[0] + "-" + (parseInt(b[0])+49)),
            datasets: [{
                label: "Proteins",
                data: sortedBins.map(b => b[1]),
                backgroundColor: "#34d399",
                borderRadius: 3,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: "#8892a8", maxRotation: 45, font: { size: 9 } }, grid: { color: "#2e3348" } },
                y: { ticks: { color: "#8892a8" }, grid: { color: "#2e3348" } }
            }
        }
    });
});

// ===================== FULL DATA TABLE =====================
async function loadFullData() {
    const loading = document.getElementById("tableLoading");
    try {
        const resp = await fetch("protein_summary.tsv");
        const text = await resp.text();
        const lines = text.split("\\n");
        const header = lines[0].split("\\t");
        allData = [];
        for (let i = 1; i < lines.length; i++) {
            const parts = lines[i].split("\\t");
            if (parts.length < header.length) continue;
            const row = {};
            header.forEach((h, j) => {
                row[h] = j >= 2 ? parseInt(parts[j]) : parts[j];
            });
            allData.push(row);
        }
        loading.style.display = "none";
        document.getElementById("tableControls").style.display = "block";
        buildOrgSelect(); // refresh with full data
        renderTable();
        document.getElementById("rowCount").textContent = allData.length.toLocaleString() + " rows loaded";
    } catch (e) {
        loading.innerHTML = `<span style="color:var(--red)">Failed to load protein_summary.tsv: ${e.message}</span>
            <span style="font-size:11px;">Make sure the file is served alongside this HTML (same directory).</span>`;
    }
}

let sortCol = "organism";
let sortAsc = true;
let searchTerm = "";

function renderTable() {
    let data = allData || [];
    if (searchTerm) {
        const q = searchTerm.toLowerCase();
        data = data.filter(r => r.organism.toLowerCase().includes(q) || r.protein.toLowerCase().includes(q));
    }
    data.sort((a, b) => {
        let va = a[sortCol], vb = b[sortCol];
        if (typeof va === "string") { va = va.toLowerCase(); vb = vb.toLowerCase(); }
        if (va < vb) return sortAsc ? -1 : 1;
        if (va > vb) return sortAsc ? 1 : -1;
        return 0;
    });

    // Cap rendered rows for performance
    const capped = data.slice(0, 500);
    document.getElementById("rowCount").textContent =
        capped.length.toLocaleString() + " of " + data.length.toLocaleString() + " rows shown (cap 500)";

    // Header
    const headRow = document.getElementById("tableHead");
    headRow.innerHTML = COLUMNS.map(c =>
        `<th data-col="${c}">${c}${c === sortCol ? '<span class="sort-arrow">' + (sortAsc ? '&uarr;' : '&darr;') + '</span>' : ''}</th>`
    ).join("");
    headRow.querySelectorAll("th").forEach(th => {
        th.addEventListener("click", () => {
            if (sortCol === th.dataset.col) sortAsc = !sortAsc;
            else { sortCol = th.dataset.col; sortAsc = true; }
            document.getElementById("sortCol").value = sortCol;
            document.getElementById("sortDir").textContent = sortAsc ? "Asc \\u2191" : "Desc \\u2193";
            renderTable();
        });
    });

    // Body
    const tbody = document.getElementById("tableBody");
    const aaSet = new Set(AA_COLS);
    tbody.innerHTML = capped.map(r =>
        "<tr>" + COLUMNS.map(c => {
            const v = r[c];
            const cls = aaSet.has(c) ? ' class="num aa-highlight"' : (typeof v === "number" ? ' class="num"' : '');
            return `<td${cls}>${v}</td>`;
        }).join("") + "</tr>"
    ).join("");
}

document.getElementById("tableSearch").addEventListener("input", e => {
    searchTerm = e.target.value;
    renderTable();
});
document.getElementById("sortCol").addEventListener("change", e => {
    sortCol = e.target.value;
    renderTable();
});
document.getElementById("sortDir").addEventListener("click", () => {
    sortAsc = !sortAsc;
    document.getElementById("sortDir").textContent = sortAsc ? "Asc \\u2191" : "Desc \\u2193";
    renderTable();
});

// ===================== INIT =====================
buildOverview();
buildOrgSelect();
</script>
</body>
</html>'''

with open("uniprot-explorer.html", "w") as f:
    f.write(html)

print(f"Wrote uniprot-explorer.html ({len(html):,} bytes, {len(data)} sample rows embedded)")
