# asf-stac

Creation and hosting of STAC catalogs by the ASF Tools team.

**Production API:** <https://stac.asf.alaska.edu>
* *Swagger UI:* <https://stac.asf.alaska.edu/api.html>

**Test API:** <https://stac-test.asf.alaska.edu>
* *Swagger UI:* <https://stac-test.asf.alaska.edu/api.html>

## Developer setup

Clone the repository, create the environment, and install the developer dependencies:

```
git clone git@github.com:ASFHyP3/asf-stac.git
cd asf-stac

conda create -c conda-forge -n asf-stac python=3.9 postgresql
conda activate asf-stac

make install
```

## Requirements for connecting to the database

Refer to this section when manually connecting to the database or when running the API locally.

The database only accepts connections from within the ASF Full VPN or from clients
with the client security group attached. See the ingress rules for the database security group in the
[database CloudFormation template](apps/database/cloudformation.yml).

The database host and database user credentials are available via the AWS Secrets Manager console
in the AWS account where the CloudFormation stack was deployed.

## Manually connecting to the database

We shouldn't need to manually connect to the database during normal operations,
as the API will connect automatically, but we can if we need to (e.g. for debugging purposes).

Confirm that you have [PostgreSQL](https://www.postgresql.org/download/) installed, then run:

```
make psql db_host=<host> db_user=<user> db_password=<password>
```

## Running the API locally

You can run the STAC API frontend locally and it will automatically connect to the AWS-hosted database.

The local API provides access to the Transaction extension (which provides create/update/delete endpoints),
while the publicly available API does not. Therefore, if you need access to the Transaction endpoints, you
must run the API locally:

```
make run-api db_host=<host> db_admin_password=<password>
```

You should see something like `Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)` in the output; you can
query the API at that URL.

You can confirm that the Transaction extension is enabled by opening the local API URL in a web browser
and appending `/api.html` to open the Swagger UI. You should see various create/update/delete endpoints
under the "Transaction Extension" heading. You should be able to successfully query these endpoints via
the local API, but not via the publicly available API. (TODO: after removing those endpoints completely
from the public API, update this paragraph to reflect that they will no longer appear in the Swagger UI.)

## Ingesting a STAC dataset

Run `python ingest_data.py -h` for usage instructions. You must run the ingest script against
a locally running API, as the script requires access to the Transaction endpoints.

## Upgrading the database

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
