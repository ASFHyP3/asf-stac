install:
	python -m pip install --upgrade pip && \
	python -m pip install -r requirements.txt

install-lambda-deps:
	python -m pip install --upgrade pip && \
	python -m pip install -r apps/api/requirements.txt -t apps/api/src/

s3_bucket ?= ''
stack_name ?= ''
cloudformation_role_arn ?= ''
new_db_password ?= ''
# TODO allow adding --role-arn option to deploy command, for cicd
deploy:
	aws cloudformation package \
	    --template-file apps/cloudformation.yml \
	    --s3-bucket ${s3_bucket} \
	    --output-template-file packaged.yml \
	&& aws cloudformation deploy \
	    --template-file packaged.yml \
	    --stack-name ${stack_name} \
	    --capabilities CAPABILITY_NAMED_IAM \
	    --role-arn ${cloudformation_role_arn} \
	    --parameter-overrides \
	      DatabasePassword=${new_db_password}

db_host ?= ''
db_password ?= ''
psql:
	PGHOST=${db_host} PGPORT=5432 PGDATABASE=postgres PGUSER=postgres PGPASSWORD=${db_password} psql

migrate:
	PGHOST=${db_host} PGPORT=5432 PGDATABASE=postgres PGUSER=postgres PGPASSWORD=${db_password} pypgstac migrate

run-api:
	POSTGRES_HOST_READER=${db_host} POSTGRES_HOST_WRITER=${db_host} POSTGRES_PORT=5432 POSTGRES_DBNAME=postgres POSTGRES_USER=postgres POSTGRES_PASS=${db_password} python -m stac_fastapi.pgstac.app

static: flake8 cfn-lint

flake8:
	flake8 --max-line-length=120

cfn-lint:
	cfn-lint --template `find . -name cloudformation.yml` --info --ignore-checks W3002
