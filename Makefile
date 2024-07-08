install:
	python -m pip install --upgrade pip && \
	python -m pip install -r requirements.txt

install-pypgstac:
	python -m pip install --upgrade pip && \
	python -m pip install $$(grep pypgstac requirements.txt)

install-lambda-deps:
	python -m pip install --upgrade pip && \
	python -m pip install -r requirements-apps-api.txt -t apps/api/src/

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
	      DatabaseAdminPassword=${db_admin_password} \
	      DatabaseReadPassword=${db_read_password} \
	      CidrIp=${cidr_ip} \
	      GithubBranch=${github_branch} \
	      DomainName=${domain_name} \
	      CertificateArn=${certificate_arn}

psql:
	PGHOST=${db_host} PGPORT=5432 PGDATABASE=postgres PGUSER=${db_user} PGPASSWORD=${db_password} psql

configure-database: install-or-upgrade-postgis pypgstac-migrate configure-database-roles

install-or-upgrade-postgis:
	PGHOST=${db_host} PGPORT=5432 PGDATABASE=postgres PGUSER=postgres PGPASSWORD=${db_admin_password} psql \
	    -f install-or-upgrade-postgis.sql

pypgstac-migrate:
	PGHOST=${db_host} PGPORT=5432 PGDATABASE=postgres PGUSER=postgres PGPASSWORD=${db_admin_password} pypgstac migrate

configure-database-roles:
	PGHOST=${db_host} PGPORT=5432 PGDATABASE=postgres PGUSER=postgres PGPASSWORD=${db_admin_password} psql \
	    --set=db_read_password=${db_read_password} \
	    -f configure-database-roles.sql

pypgstac-load:
	PGHOST=${db_host} PGPORT=5432 PGDATABASE=postgres PGUSER=postgres PGPASSWORD=${db_admin_password} \
	    pypgstac load ${table} ${ndjson_file} --method upsert

run-api:
	POSTGRES_HOST_READER=${db_host} POSTGRES_HOST_WRITER=${db_host} POSTGRES_PORT=5432 \
	    POSTGRES_DBNAME=postgres POSTGRES_USER=postgres POSTGRES_PASS=${db_admin_password} \
	    ENABLED_EXTENSIONS=${enabled_extensions} \
	    python -m stac_fastapi.pgstac.app

test:
	PYTHONPATH=${PWD}/collections/sentinel-1-global-coherence/:${PWD}/collections/glo-30-hand/ python -m pytest tests/

static: flake8 cfn-lint

flake8:
	flake8 --max-line-length=120

cfn-lint:
	# Ignore "W1011 Use dynamic references over parameters for secrets" because we store secrets
	# using GitHub Secrets. See https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/rules.md
	cfn-lint --template `find . -name cloudformation.yml` --info --ignore-checks W3002 W1011
