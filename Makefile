# TODO create target for installing dependencies

template_path ?= '' # TODO
s3_bucket ?= '' # TODO
stack_name ?= '' # TODO
# TODO allow adding --role-arn option to deploy command, for cicd
deploy:
	aws cloudformation package \
	    --template-file ${template_path} \
	    --s3-bucket ${s3_bucket} \
	    --output-template-file packaged.yml \
	&& aws cloudformation deploy \
	    --template-file packaged.yml \
	    --stack-name ${stack_name} \
	    --capabilities CAPABILITY_NAMED_IAM

static: flake8 cfn-lint

flake8:
	flake8 --max-line-length=120

cfn-lint:
	cfn-lint --template `find . -name cloudformation.yml` --info
