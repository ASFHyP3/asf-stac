import os
import sys
import time

import boto3

CLIENT = boto3.client('codebuild')


def main() -> None:
    project_name = os.environ['CODEBUILD_PROJECT']
    print(f'Starting CodeBuild for project {project_name}')
    response = CLIENT.start_build(projectName=project_name)

    build_id = response['build']['id']
    print(f'Build ID: {build_id}')

    build_status = response['build']['buildStatus']
    print(f'Build status: {build_status}')

    while build_status == 'IN_PROGRESS':
        time.sleep(5)

        response = CLIENT.batch_get_builds(ids=[build_id])
        assert len(response['builds']) == 1

        build_status = response['builds'][0]['buildStatus']
        print(f'Build status: {build_status}')

    if build_status != 'SUCCEEDED':
        sys.exit(f'CodeBuild failed with status {build_status}')


if __name__ == '__main__':
    main()
