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

conda env create -f environment.yml
conda activate asf-stac
```

If you ever see the following warning from `gdal`...

```
Warning 1: PROJ: proj_create_from_database: Open of /home/.../miniconda3/envs/asf-stac/share/proj failed
```

...you can run the following command and then re-activate your Conda environment:

```
conda env config vars set PROJ_LIB=${CONDA_PREFIX}/share/proj
```

## Requirements for connecting to the database

The database only accepts connections from within the ASF Full VPN or from clients
with the client security group attached. See the ingress rules for the database security group in the
[database CloudFormation template](apps/database/cloudformation.yml).

The database host and database user credentials are available via the AWS Secrets Manager console
in the AWS account where the CloudFormation stack was deployed.

## Creating and ingesting the coherence dataset

We must create and ingest the coherence dataset after running a new STAC API deployment. We must also
re-create and re-ingest the dataset after making changes to how the STAC items are structured.

Fetch the list of S3 objects:

```
cd collections/sentinel-1-global-coherence/
./list-coherence-objects
wc -l coherence-s3-objects.txt
```

Confirm that the number of lines is `1033388` (one per object).

Next, create the dataset:

TODO: why don't we have to set `AWS_PROFILE` for this command? (for getting the bucket region)
```
python create_coherence_items.py coherence-s3-objects.txt
wc -l sentinel-1-global-coherence.ndjson
```

Again, confirm that the number of lines is the same as in the previous step.

Finally, ingest the dataset:

```
cd ../../
make pypgstac-load db_host=<host> db_admin_password=<password> table=items ndjson_file=collections/sentinel-1-global-coherence/sentinel-1-global-coherence.ndjson
```

## Creating and ingesting the HAND dataset

We must create and ingest the HAND dataset after running a new STAC API deployment. We must also
re-create and re-ingest the dataset after making changes to how the STAC items are structured.

Fetch the list of S3 objects:

```
cd collections/glo-30-hand/
./list-hand-objects
wc -l hand-s3-objects.txt
```

Confirm that the number of lines is `26450` (one per object).

Next, create the dataset:

```
AWS_PROFILE=opendata python create_hand_items.py hand-s3-objects.txt
wc -l glo-30-hand.ndjson
```

Again, confirm that the number of lines is the same as in the previous step.

Finally, ingest the dataset:

```
cd ../../
make pypgstac-load db_host=<host> db_admin_password=<password> table=items ndjson_file=collections/glo-30-hand/glo-30-hand.ndjson
```

## Manually connecting to the database

We shouldn't need to manually connect to the database during normal operations, but we can if we need to
(e.g. for debugging purposes).

Confirm that you have [PostgreSQL](https://www.postgresql.org/download/) installed, then run:

```
make psql db_host=<host> db_user=<user> db_password=<password>
```

## Running the API locally

You can run the STAC API frontend locally and it will automatically connect to the AWS-hosted database.
We shouldn't need to run the API locally during normal operations, but we can if we need to
(e.g. for debugging purposes).

The local API provides access to the Transaction extension (which provides create/update/delete endpoints),
while the publicly available API does not. We shouldn't need access to the Transaction endpoints during
normal operations, but they may be useful for making one-off edits in a sandbox or test deployment.

Run:

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
