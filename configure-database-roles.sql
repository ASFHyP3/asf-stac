\set ON_ERROR_STOP TRUE

ALTER ROLE pgstac_ingest LOGIN PASSWORD :'db_ingest_password';
ALTER ROLE pgstac_read LOGIN PASSWORD :'db_read_password';
