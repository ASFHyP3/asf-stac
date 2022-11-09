# asf-stac

A repository containing code related to the creation and hosting of STAC catalogs by the ASF tools team.

## Developer setup

TODO: document creating conda env and installing developer deps

## STAC API

### Upgrading the database

TODO: document upgrading Postgres, PostGIS, and PgSTAC

Run the following command to list the Postgres versions supported by Amazon RDS:

```
aws rds describe-db-engine-versions --engine postgres --query "DBEngineVersions[].EngineVersion"
```

To upgrade Postgres, change the version specified in the
[database CloudFormation template](apps/database/cloudformation.yml).

When you upgrade Postgres, you should also upgrade the PostGIS extension. Refer to the tables shown
[here](https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-extensions.html)
to determine which version of PostGIS is supported by the database's Postgres version. You can also connect to the
database and run the following query:

```
SELECT * FROM pg_available_extension_versions WHERE name='postgis';
```

To upgrade PostGIS, change the version specified in the [install/upgrade script](install-or-upgrade-postgis.sql).

### Connecting to the database

Confirm you have the `psql` command installed, then run:

```
make psql db_host=<host> db_password=<password>
```

You can find the appropriate value for `<host>` by navigating to the database instance via the CloudFormation or
RDS console and copying the "Endpoint" field.

### Running the API locally

To run the STAC API locally:

```
make run-api db_host=<host> db_password=<password>
```

You should see something like `Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)` in the output; you can
query the API at that URL.

### Ingesting STAC dataset

Run `python ingest_data.py -h` for usage instructions.
