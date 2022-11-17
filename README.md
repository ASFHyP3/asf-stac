# asf-stac

A repository containing code related to the creation and hosting of STAC catalogs by the ASF Tools team.

## Developer setup

Create the environment and install developer dependencies:

```
conda create -n asf-stac python=3.9
conda activate asf-stac
make install
```

## STAC API

TODO: document database URLs and the `/api.html` endpoint for the Swagger UI

### Running the API locally

You can run the STAC API frontend locally (connected to the AWS-hosted database). This is required for accessing
the create/update/delete endpoints (which are provided by the STAC API's Transaction extension), as these
endpoints are disabled for the publicly accessible API.

To run the STAC API locally:

```
make run-api db_host=<host> db_admin_password=<password>
```

You should see something like `Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)` in the output; you can
query the API at that URL.

### Ingesting a STAC dataset

Run `python ingest_data.py -h` for usage instructions. The script only works with an API that supports the
Transaction extension. See [Running the API locally](#running-the-api-locally).

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

PgSTAC upgrades are handled automatically: the deployment pipeline migrates the database to the installed
version of `pypgstac`. See <https://stac-utils.github.io/pgstac/pypgstac> for more information about migrations.

### Connecting to the database

We shouldn't need to manually connect to the database, but we can if we need to.
Confirm you have the `psql` command installed, then run:

```
make psql db_host=<host> db_user=<user> db_password=<password>
```

The database host and database user credentials are available via the AWS Secrets Manager console
in the AWS account where the CloudFormation stack was deployed.
