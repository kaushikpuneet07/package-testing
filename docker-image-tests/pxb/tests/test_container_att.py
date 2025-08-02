#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import json
from settings import *


container_name = 'pxb-docker-test-inspect'

@pytest.fixture(scope='module')
def inspect_data():
    docker_id = subprocess.check_output(
        ['docker', 'run', '--name', container_name, '-e', 'PERCONA_TELEMETRY_URL=https://check-dev.percona.com/v1/telemetry/GenericReport', '-d', docker_image]).decode().strip()
    inspect_data = json.loads(subprocess.check_output(['docker','inspect',container_name]))
    yield inspect_data[0]
    subprocess.check_call(['docker', 'rm', '-f', docker_id])


class TestPXBContainerAttributes:
    def test_entrypoint(self, inspect_data):
        assert inspect_data['Config']['Entrypoint'][0] in ['/bin/bash', '/usr/bin/xtrabackup']

    def test_status(self, inspect_data):
        assert inspect_data['State']['Status'] == 'running'
        assert inspect_data['State']['Running'] == True

    def test_image_name(self, inspect_data):
        assert docker_image in inspect_data['Config']['Image']
