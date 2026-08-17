# Reproduce the Patched Smoke

Build and install:

```bash
source /opt/rh/devtoolset-11/enable
cd /opt/opentenbase/src/OpenTenBase
./configure --prefix=/opt/opentenbase/install \
  CFLAGS="-O2 -g -fno-omit-frame-pointer" \
  --enable-thread-safety --with-zstd --with-lz4 --with-libxml \
  --disable-license
make -j2
make install
make -C contrib/pgvector install
```

Run the targeted regression:

```bash
cd /opt/opentenbase/src/OpenTenBase/contrib/pgvector
export PATH=/opt/opentenbase/install/bin:/usr/bin:/bin
export LD_LIBRARY_PATH=/opt/opentenbase/install/lib
export PGHOST=127.0.0.1 PGPORT=22201 PGUSER=otbtest
export MY_LOCAL_CN1PORT=22201
make installcheck REGRESS=ivfflat_vector
```

Run the fixed-seed Datanode RSS smoke after creating `ivfflat_test` and the vector extension through the Coordinator:

```bash
export PGHOST=127.0.0.1 PGPORT=22301 PGUSER=otbtest
DBNAME=ivfflat_test CREATE_EXTENSION=false OPENTENBASE_CN_PORT=22201 \
  ITEM_ROWS=1000 DIMS=128 RESCANS=1000 LISTS=20 PROBES=1 \
  RUN_ID=ivfflat_rescan_patched_smoke_dn \
  RESULT_DIR=/opt/opentenbase/artifacts/ivfflat_rescan_patched_smoke_dn \
  bench/run_ivfflat_rescan_memory.sh
```
