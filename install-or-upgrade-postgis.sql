postgis_version CONSTANT string := '3.1.5';
CREATE EXTENSION IF NOT EXISTS postgis WITH VERSION postgis_version;
ALTER EXTENSION postgis UPDATE TO postgis_version;
