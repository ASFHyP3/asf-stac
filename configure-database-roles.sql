\set ON_ERROR_STOP TRUE

ALTER ROLE pgstac_ingest LOGIN PASSWORD :'db_ingest_password';
ALTER ROLE pgstac_read LOGIN PASSWORD :'db_read_password';

-- TODO this will no longer be needed after the pgstac_read permissions bug is fixed: https://github.com/stac-utils/pgstac/issues/146
GRANT SELECT ON pgstac.collections TO pgstac_read;
