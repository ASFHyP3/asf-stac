# asf-stac

Creation and hosting of STAC catalogs by the ASF Tools team.

The test API is available at <https://stac-test.asf.alaska.edu>
and the Swagger UI is available at <https://stac-test.asf.alaska.edu/api.html>.

TODO: document prod URL

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

## Working with the database from an EC2 instance

As explained in [Requirements for connecting to the database](#requirements-for-connecting-to-the-database),
the database only accepts connections from particular sources. If you want to work with the database
from an EC2 instance (e.g. because your local internet speed is insufficient for ingesting a large dataset),
follow the steps below:

1. Follow the
   [Working from an EC2 instance](https://github.com/ASFHyP3/.github-private/wiki/Working-from-an-EC2-instance)
   Tools Team Wiki article to create an EC2 instance in the same AWS account as the database:
   * Instead of the default VPC, select the VPC that corresponds to the appropriate ASF STAC deployment
     (this should be obvious from the name of the VPC in the drop-down list).
   * After launching the instance, add an additional security group as described in the article;
     in the list of available security groups, select the one whose name identifies it as the ASF STAC
     database client security group.

2. After SSHing into your instance and running tmux as described in the wiki article, follow
   [Developer setup](#developer-setup) to clone and set up this repo on the EC2 instance.

3. If you want to run the API on the EC2 instance (e.g. for ingesting a dataset), you can run the API as described in
   [Running the API locally](#running-the-API-locally). After the API is running, you can create a new tmux
   window to accomplish more work, such as running the ingest script.

4. If you're ingesting a dataset that is stored in S3, you can use the AWS CLI to download the S3 object
   to the EC2 instance before running the ingest script.

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
