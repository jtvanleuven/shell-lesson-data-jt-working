#!/bin/bash
# fasta_summary.sh — Parse a UniProt/SProt FASTA file and produce a TSV table
# with organism, protein name, sequence length, and count of each amino acid.
#
# Usage:
#   ./fasta_summary.sh input.fasta [output.tsv]
#
# Example:
#   ./fasta_summary.sh uniprot_sprot.fasta protein_summary.tsv
#
# Output columns:
#   organism  protein  length  A C D E F G H I K L M N P Q R S T V W Y X

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <fasta_file> [output_file]" >&2
    exit 1
fi

INPUT="$1"
OUTPUT="${2:-/dev/stdout}"

if [ ! -f "$INPUT" ]; then
    echo "Error: file '$INPUT' not found" >&2
    exit 2
fi

echo "Processing $INPUT ..." >&2

awk '
BEGIN {
    # 20 standard amino acids in canonical order
    split("A C D E F G H I K L M N P Q R S T V W Y", aa, " ")
    N = 20
}

# --- Helper: flush current record ---
function flush(    i, line, c) {
    if (gene == "") return
    delete cnt
    for (i = 1; i <= N; i++) cnt[aa[i]] = 0
    cnt["X"] = 0

    len = length(seq)
    for (i = 1; i <= len; i++) {
        c = substr(seq, i, 1)
        if (c in cnt) cnt[c]++
        else cnt["X"]++
    }

    line = organism "\t" protein "\t" len
    for (i = 1; i <= N; i++) line = line "\t" cnt[aa[i]]
    line = line "\t" cnt["X"]
    print line
    gene = ""
}

# --- Helper: extract multi-word field between two keys ---
function extract_between(hd, start_key, end_key,    pos, rest, endpos) {
    pos = index(hd, start_key "=")
    if (pos == 0) return ""
    rest = substr(hd, pos + length(start_key) + 1)
    if (end_key != "") {
        endpos = index(rest, " " end_key "=")
        if (endpos > 0) return substr(rest, 1, endpos - 1)
    }
    return rest
}

# --- Helper: extract single-word field ---
function extract_word(hd, key,    pos, rest, sp) {
    pos = index(hd, key "=")
    if (pos == 0) return ""
    rest = substr(hd, pos + length(key) + 1)
    sp = index(rest, " ")
    if (sp > 0) return substr(rest, 1, sp - 1)
    return rest
}

# --- Print header on first record ---
NR == 1 && /^>/ {
    hdr = "organism\tprotein\tlength"
    for (i = 1; i <= N; i++) hdr = hdr "\t" aa[i]
    hdr = hdr "\tX"
    print hdr
}

# --- FASTA header line ---
/^>/ {
    flush()
    hd = substr($0, 2)
    # Protein: everything between the 2nd field and " OS="
    pos_os = index(hd, " OS=")
    if (pos_os > 0) {
        # Find end of first field (accession like sp|Q6GZX4|001R_FRG3G)
        sp1 = index(hd, " ")
        protein = substr(hd, sp1 + 1, pos_os - sp1 - 2)
    } else {
        protein = hd
    }

    # Organism: everything between OS= and OX= (handles multi-word names)
    organism = extract_between(hd, "OS", "OX")
    if (organism == "") organism = "unknown"

    # Use GN field as a marker so flush knows there is a record
    gene = extract_word(hd, "GN")
    if (gene == "") gene = "unknown"

    seq = ""
    next
}

# --- Sequence line ---
{
    # Remove whitespace and carriage returns
    gsub(/[ \t\r\n]/, "", $0)
    seq = seq $0
}

END {
    flush()
}
' "$INPUT" > "$OUTPUT"

if [ "$OUTPUT" != "/dev/stdout" ]; then
    echo "Done. Wrote $(($(wc -l < "$OUTPUT") - 1)) records to $OUTPUT" >&2
fi
