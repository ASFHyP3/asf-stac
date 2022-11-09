\set ON_ERROR_STOP TRUE
\set postgis_version '3.1.4'

CREATE EXTENSION IF NOT EXISTS postgis WITH VERSION :'postgis_version';
ALTER EXTENSION postgis UPDATE TO :'postgis_version';
