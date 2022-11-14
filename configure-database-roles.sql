\set ON_ERROR_STOP TRUE

ALTER ROLE pgstac_read LOGIN PASSWORD :'db_read_password';
GRANT SELECT ON pgstac.collections TO pgstac_read;
