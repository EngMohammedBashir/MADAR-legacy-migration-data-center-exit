#!/bin/bash
set -euo pipefail

OUTPUT_DIR="/home/madaradmin/madar-legacy-data/reports"
LOG_DIR="/home/madaradmin/madar-legacy-data/logs"
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')

mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

psql \
    -h localhost \
    -U madar_app \
    -d madar_legacy \
    -c "\copy (
        SELECT status, COUNT(*) AS shipment_count
        FROM shipments
        GROUP BY status
        ORDER BY status
    ) TO '$OUTPUT_DIR/operations_${TIMESTAMP}.csv' WITH CSV HEADER"

echo "$(date '+%Y-%m-%d %H:%M:%S') SUCCESS: operations_${TIMESTAMP}.csv generated" \
    >> "$LOG_DIR/background-job.log"
