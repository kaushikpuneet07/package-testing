#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
import os
import shlex
from settings import *

ps_docker_image = "percona/percona-server:8.4"
pxb_docker_image = "percona/percona-xtrabackup:8.4"
docker_network = "doc_net"

class PsNode:
    def __init__(self, node_name):
        self.node_name = node_name
        self.docker_id = subprocess.check_output([
            'docker', 'run', '--name', node_name,
            '-e', f'MYSQL_ROOT_PASSWORD={ps_pwd}',
            '--net', docker_network,
            '-v', f'{test_pwd}/backup:/backup',
            '-d', ps_docker_image
        ]).decode().strip()
        time.sleep(40)
        self.ti_host = testinfra.get_host("docker://root@" + self.docker_id)

    def exec_query(self, query):
        cmd = self.ti_host.run(f'mysql -uroot -p{ps_pwd} -e {shlex.quote(query)}')
        assert cmd.succeeded
        return cmd.stdout

    def stop(self):
        subprocess.call(['docker', 'rm', '-f', self.docker_id])

class XtrabackupNode:
    def __init__(self):
        self.node_name = 'pxb_tester'
        self.docker_id = subprocess.check_output([
            'docker', 'run', '-itd', '--name', self.node_name,
            '--net', docker_network,
            '-v', f'{test_pwd}/backup:/backup',
            pxb_docker_image
        ]).decode().strip()
        self.ti_host = testinfra.get_host("docker://root@" + self.docker_id)

    def run_backup(self, source_host):
        cmd = self.ti_host.run(
            f'xtrabackup --backup --host={source_host} --user=root --password={ps_pwd} --target-dir=/backup'
        )
        assert cmd.succeeded

    def prepare_backup(self):
        cmd = self.ti_host.run('xtrabackup --prepare --target-dir=/backup')
        assert cmd.succeeded

    def stop(self):
        subprocess.call(['docker', 'rm', '-f', self.docker_id])

@pytest.fixture(scope='module')
def ps():
    subprocess.call(['docker', 'pull', ps_docker_image])
    node = PsNode('ps_node')
    yield node
    node.stop()
    subprocess.call(['docker', 'network', 'rm', docker_network])

@pytest.fixture(scope='module')
def pxb():
    subprocess.call(['docker', 'pull', pxb_docker_image])
    node = XtrabackupNode()
    yield node
    node.stop()

def test_backup_and_restore(ps, pxb):
    ps.exec_query('CREATE DATABASE test;')
    ps.exec_query('CREATE TABLE test.t1 (id INT PRIMARY KEY);')
    ps.exec_query('INSERT INTO test.t1 VALUES (1), (2);')

    # Run backup from pxb container
    pxb.run_backup('ps_node')
    pxb.prepare_backup()

    # Validate backup content
    result = pxb.ti_host.run('test -f /backup/ibdata1')
    assert result.succeeded

