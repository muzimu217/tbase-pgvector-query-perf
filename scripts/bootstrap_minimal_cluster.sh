#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-/opt/opentenbase/install}"
CLUSTER_ROOT="${CLUSTER_ROOT:-/data/otb/ivfflat-v1}"
OS_USER="${OS_USER:-otbtest}"
GTM_PORT="${GTM_PORT:-22101}"
CN_PORT="${CN_PORT:-22201}"
CN_FORWARD_PORT="${CN_FORWARD_PORT:-22202}"
CN_POOLER_PORT="${CN_POOLER_PORT:-22211}"
DN_PORT="${DN_PORT:-22301}"
DN_FORWARD_PORT="${DN_FORWARD_PORT:-22302}"
DN_POOLER_PORT="${DN_POOLER_PORT:-22311}"

GTM_DIR="${CLUSTER_ROOT}/gtm"
CN_DIR="${CLUSTER_ROOT}/cn1"
DN_DIR="${CLUSTER_ROOT}/dn1"

if [ "$(id -u)" -ne 0 ]; then
	echo "run this bootstrap script as root" >&2
	exit 1
fi

for program in postgres initdb initgtm gtm_ctl pg_ctl psql; do
	if [ ! -x "${INSTALL_DIR}/bin/${program}" ]; then
		echo "missing OpenTenBase program: ${INSTALL_DIR}/bin/${program}" >&2
		exit 1
	fi
done

if [ -e "$CLUSTER_ROOT" ]; then
	echo "cluster root already exists; refusing to overwrite: ${CLUSTER_ROOT}" >&2
	exit 1
fi

port_in_use() {
	local port="$1"
	ss -ltnH | awk '{ print $4 }' | grep -Eq "[:.]${port}$"
}

for port in \
	"$GTM_PORT" \
	"$CN_PORT" \
	"$CN_FORWARD_PORT" \
	"$CN_POOLER_PORT" \
	"$DN_PORT" \
	"$DN_FORWARD_PORT" \
	"$DN_POOLER_PORT"
do
	if port_in_use "$port"; then
		echo "port is already in use: ${port}" >&2
		exit 1
	fi
done

if ! id "$OS_USER" >/dev/null 2>&1; then
	useradd --create-home --home-dir "/data/${OS_USER}" --shell /bin/bash "$OS_USER"
fi

install -d -o "$OS_USER" -g "$OS_USER" "$CLUSTER_ROOT"

as_cluster_user() {
	runuser -u "$OS_USER" -- env \
		HOME="/data/${OS_USER}" \
		LANG=C \
		LC_ALL=C \
		PATH="${INSTALL_DIR}/bin:/usr/bin:/bin" \
		LD_LIBRARY_PATH="${INSTALL_DIR}/lib" \
		"$@"
}

append_postgres_config() {
	local data_dir="$1"
	local port="$2"
	local forward_port="$3"
	local pooler_port="$4"

	printf '%s\n' \
		"listen_addresses = '127.0.0.1'" \
		"port = ${port}" \
		"forward_port = ${forward_port}" \
		"pooler_port = ${pooler_port}" \
		"max_connections = 50" \
		"max_wal_senders = 10" \
		"max_worker_processes = 16" \
		"max_parallel_workers = 8" \
		"max_prepared_transactions = 100" \
		"shared_buffers = '128MB'" \
		"fn_shared_buffers = 160" \
		"work_mem = '4MB'" \
		"pg_workfile_max_entries = 128" \
		"space_budget_limit = 100" \
		"logging_collector = on" \
		"log_directory = 'log'" \
		>> "${data_dir}/postgresql.conf"
}

cleanup_on_error() {
	local status="$?"
	trap - ERR

	echo "bootstrap failed; stopping processes and preserving ${CLUSTER_ROOT} for diagnosis" >&2
	if [ -f "${CN_DIR}/postmaster.pid" ]; then
		as_cluster_user pg_ctl stop -m fast -Z coordinator -D "$CN_DIR" >/dev/null 2>&1 || true
	fi
	if [ -f "${DN_DIR}/postmaster.pid" ]; then
		as_cluster_user pg_ctl stop -m fast -Z datanode -D "$DN_DIR" >/dev/null 2>&1 || true
	fi
	if [ -d "$GTM_DIR" ]; then
		as_cluster_user gtm_ctl stop -Z gtm -D "$GTM_DIR" -P "$GTM_PORT" >/dev/null 2>&1 || true
	fi

	exit "$status"
}

trap cleanup_on_error ERR

as_cluster_user initgtm -Z gtm -D "$GTM_DIR"
printf '%s\n' \
	"listen_addresses = '127.0.0.1'" \
	"port = ${GTM_PORT}" \
	"nodename = 'gtm'" \
	"startup = ACT" \
	>> "${GTM_DIR}/gtm.conf"
as_cluster_user gtm_ctl start -Z gtm -D "$GTM_DIR" -l "${GTM_DIR}/startup.log"

as_cluster_user initdb \
	--nodename cn1 \
	--nodetype coordinator \
	--master_gtm_nodename gtm \
	--master_gtm_ip 127.0.0.1 \
	--master_gtm_port "$GTM_PORT" \
	-D "$CN_DIR"
append_postgres_config "$CN_DIR" "$CN_PORT" "$CN_FORWARD_PORT" "$CN_POOLER_PORT"

as_cluster_user initdb \
	--nodename dn1 \
	--nodetype datanode \
	--master_gtm_nodename gtm \
	--master_gtm_ip 127.0.0.1 \
	--master_gtm_port "$GTM_PORT" \
	-D "$DN_DIR"
append_postgres_config "$DN_DIR" "$DN_PORT" "$DN_FORWARD_PORT" "$DN_POOLER_PORT"

as_cluster_user pg_ctl start -w -Z datanode -D "$DN_DIR" -l "${DN_DIR}/startup.log"
as_cluster_user pg_ctl start -w -Z coordinator -D "$CN_DIR" -l "${CN_DIR}/startup.log"

as_cluster_user psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p "$CN_PORT" -d postgres <<SQL
ALTER NODE cn1 WITH (
    TYPE = 'coordinator',
    HOST = '127.0.0.1',
    PORT = ${CN_PORT},
    FORWARD = ${CN_FORWARD_PORT}
);
CREATE NODE dn1 WITH (
    TYPE = 'datanode',
    HOST = '127.0.0.1',
    PORT = ${DN_PORT},
    FORWARD = ${DN_FORWARD_PORT},
    PRIMARY,
    PREFERRED
);
SELECT pgxc_pool_reload();
EXECUTE DIRECT ON (dn1)
    'CREATE NODE cn1 WITH (TYPE=''coordinator'', HOST=''127.0.0.1'', PORT=${CN_PORT}, FORWARD=${CN_FORWARD_PORT})';
EXECUTE DIRECT ON (dn1)
    'ALTER NODE dn1 WITH (TYPE=''datanode'', HOST=''127.0.0.1'', PORT=${DN_PORT}, FORWARD=${DN_FORWARD_PORT}, PRIMARY, PREFERRED)';
EXECUTE DIRECT ON (dn1) 'SELECT pgxc_pool_reload()';
CREATE DEFAULT NODE GROUP default_group WITH (dn1);
CREATE SHARDING GROUP TO GROUP default_group;
SELECT pgxc_pool_reload();
SQL

as_cluster_user psql -X -v ON_ERROR_STOP=1 -h 127.0.0.1 -p "$CN_PORT" -d postgres \
	-c "SELECT node_name, node_type, node_host, node_port FROM pgxc_node ORDER BY node_name;"

as_cluster_user gtm_ctl status -Z gtm -D "$GTM_DIR" -P "$GTM_PORT"
as_cluster_user pg_ctl status -Z coordinator -D "$CN_DIR"
as_cluster_user pg_ctl status -Z datanode -D "$DN_DIR"

trap - ERR
