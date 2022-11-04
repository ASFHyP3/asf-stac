# asf-stac

A repository containing code related to the creation and hosting of STAC catalogs by the ASF tools team.

## Developer setup

TODO: document creating conda env and installing developer deps

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

### Ingesting STAC dataset

TODO: document using ingest script
