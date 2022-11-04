# asf-stac

A repository containing code related to the creation and hosting of STAC catalogs by the ASF tools team.

## Developer setup

TODO: document installing developer deps

## STAC API

### Manual deployment

TODO: document deploying with `make`

### Connecting to the database

Confirm you have the `psql` command installed, then run:

```
make psql db_host=<host> db_password=<password>
```

You can find the appropriate value for `<host>` by navigating to the database instance via the CloudFormation or
RDS console and copying the "Endpoint" field.

### Installing the PostGIS extension

TODO: automate this step

After deploying the database for the first time, connect to the database with `psql` as described above, then run:

```
CREATE EXTENSION postgis;
```

### Installing PGStac

TODO: automate this step (installation and upgrades)

Next, install PGStac into the database:

```
make migrate db_host=<host> db_password=<password>
```

After upgrading `pypgstac`, you can re-run the above command to upgrade the version of PGStac installed to the database.

For more information about migrations, see <https://stac-utils.github.io/pgstac/pypgstac/>.

### Ingesting STAC dataset

TODO: document using ingest script