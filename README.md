# asf-stac

A repository containing code related to the creation and hosting of STAC catalogs by the ASF tools team.

## Developer setup

TODO: document creating conda env and installing developer deps

## STAC API

TODO: proofread docs since adding three database users

### Upgrading the database

The initial AWS deployment creates a Postgres database, installs the PostGIS extension, and then installs
[PgSTAC](https://stac-utils.github.io/pgstac). Follow these steps to upgrade the database:

1. Run the following command to list the Postgres versions supported by Amazon RDS:
    ```
    aws rds describe-db-engine-versions --engine postgres
    ```
   Identify the entry that corresponds to the current version of the database.
   Then identify the newest available version from the list of valid upgrade targets for the current version.
   This will be the new version for the database.

2. Change the Postgres version specified in the [database CloudFormation template](apps/database/cloudformation.yml)
   to the new version.

3. Next, refer to the tables shown
   [here](https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-extensions.html)
   to determine which version of the PostGIS extension is supported by the new Postgres version.

4. Change the PostGIS version specified in the [install/upgrade script](install-or-upgrade-postgis.sql).

5. Deploy to AWS.

PgSTAC upgrades are handled automatically: the [deployment workflow](.github/workflows/deploy-stac-api.yml)
migrates the database to the installed version of `pypgstac`. See <https://stac-utils.github.io/pgstac/pypgstac>
for more information about migrations.

### Connecting to the database

Confirm you have the `psql` command installed, then run:

```
make psql db_host=<host> db_user=<user> db_password=<password>
```

You can find the appropriate value for `<host>` by navigating to the database instance via the CloudFormation or
RDS console and copying the "Endpoint" field.

### Running the API locally

To run the STAC API locally:

```
make run-api db_host=<host> db_admin_password=<password>
```

You should see something like `Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)` in the output; you can
query the API at that URL.

### Ingesting STAC dataset

Run `python ingest_data.py -h` for usage instructions.
