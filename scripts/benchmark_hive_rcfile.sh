#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${HADOOP_HOME:?Set HADOOP_HOME}"
: "${HIVE_HOME:?Set HIVE_HOME}"

database=${1:?Usage: benchmark_hive_rcfile.sh DATABASE HDFS_CLEAN_INPUT HDFS_RCFILE_OUTPUT LOCAL_RESULTS_DIR}
input_dir=${2:?Specify HDFS clean input directory (daily_text location)}
rc_dir=${3:?Specify HDFS RCFile output directory (daily_rcfile location)}
results_dir=${4:?Specify local results directory}

[[ $(hdfs getconf -confKey fs.defaultFS) == hdfs://* ]] || {
  echo 'An HDFS cluster is required' >&2
  exit 1
}

mkdir -p "$results_dir"
build_dir=$(mktemp -d)
trap 'rm -rf "$build_dir"' EXIT

javac -cp "$(hadoop classpath)" -d "$build_dir" hadoop/StorageSummary.java

hive_url=${HIVE_JDBC_URL:-jdbc:hive2://localhost:10000}
beeline_cmd=(beeline -u "$hive_url" -n "${HIVE_USER:-root}" --silent=true --showHeader=false --outputformat=tsv2)

"${beeline_cmd[@]}" \
  --hivevar DATABASE="$database" \
  --hivevar INPUT="$input_dir" \
  --hivevar RC_OUTPUT="$rc_dir" \
  -f hive/tables.hql

text_out="$results_dir/hive_text_summary.tsv"
rc_out="$results_dir/hive_rcfile_summary.tsv"

text_start=$(python3 -c 'import time; print(time.monotonic())')
"${beeline_cmd[@]}" --hivevar DATABASE="$database" --hivevar TABLE=daily_text -f hive/annual_seller_summary.hql > "$text_out"
text_end=$(python3 -c 'import time; print(time.monotonic())')

rc_start=$(python3 -c 'import time; print(time.monotonic())')
"${beeline_cmd[@]}" --hivevar DATABASE="$database" --hivevar TABLE=daily_rcfile -f hive/annual_seller_summary.hql > "$rc_out"
rc_end=$(python3 -c 'import time; print(time.monotonic())')

diff -u "$text_out" "$rc_out"

text_storage=$(HADOOP_CLASSPATH="$build_dir" hadoop StorageSummary "$input_dir")
rc_storage=$(HADOOP_CLASSPATH="$build_dir" hadoop StorageSummary "$rc_dir")

python3 - "$text_start" "$text_end" "$rc_start" "$rc_end" "$text_storage" "$rc_storage" "$results_dir/hive_rcfile_benchmark.json" <<'PY'
import json
import sys
from pathlib import Path

t_text = float(sys.argv[2]) - float(sys.argv[1])
t_rc = float(sys.argv[4]) - float(sys.argv[3])
text_store = json.loads(sys.argv[5])
rc_store = json.loads(sys.argv[6])

text_bytes = text_store["logical_bytes"]
rc_bytes = rc_store["logical_bytes"]
compression_ratio = round(text_bytes / rc_bytes, 3) if rc_bytes else None
space_savings_pct = round((1.0 - rc_bytes / text_bytes) * 100.0, 2) if text_bytes else None

report = {
    "daily_text": {
        "execution_seconds": round(t_text, 3),
        **text_store,
    },
    "daily_rcfile": {
        "execution_seconds": round(t_rc, 3),
        **rc_store,
    },
    "comparison": {
        "outputs_identical": True,
        "compression_ratio_text_over_rcfile": compression_ratio,
        "space_savings_percent": space_savings_pct,
        "query_speedup_text_over_rcfile": round(t_text / t_rc, 3) if t_rc else None,
    },
}
Path(sys.argv[7]).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
PY

