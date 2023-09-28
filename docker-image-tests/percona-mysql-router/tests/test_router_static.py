#!/usr/bin/env python3
import pytest
import subprocess
import testinfra
import time
from settings import *
import json
import os
import requests
import docker

container_name = 'mysql-router-test'
network_name = 'innodbnet1'
docker_tag = os.getenv('ROUTER_VERSION')
docker_acc = os.getenv('DOCKER_ACC')
ps_version = os.getenv('PS_VERSION')
router_docker_image = docker_acc + "/" + "percona-mysql-router" + ":" + docker_tag
percona_docker_image = docker_acc + "/" + "percona-server" + ":" + ps_version

def create_network():
    subprocess.run(['sudo', 'docker', 'network', 'create', 'innodbnet'])

def create_mysql_config():
    for N in range(1, 5):
        with open(f'my{N}.cnf', 'w') as file:
            file.write(
                f"[mysqld]\n"
                f"plugin_load_add='group_replication.so'\n"
                f"server_id={(hash(str(time.time()) + str(N))) % 40 + 10}\n"
                f"binlog_checksum=NONE\n"
                f"enforce_gtid_consistency=ON\n"
                f"gtid_mode=ON\n"
                f"relay_log=mysql{N}-relay-bin\n"
                f"innodb_dedicated_server=ON\n"
                f"binlog_transaction_dependency_tracking=WRITESET\n"
                f"slave_preserve_commit_order=ON\n"
                f"slave_parallel_type=LOGICAL_CLOCK\n"
                f"transaction_write_set_extraction=XXHASH64\n"
            )

def start_mysql_containers():
    for N in range(1, 5):
        subprocess.run([
            'sudo', 'docker', 'run', '-d',
            f'--name=mysql{N}',
            f'--hostname=mysql{N}',
            '--net=innodbnet',
            '-v', f'my{N}.cnf:/etc/my.cnf',
            '-e', 'MYSQL_ROOT_PASSWORD=root', percona_docker_image
        ])
    time.sleep(60)

def create_new_user():
    for N in range(1, 5):
        subprocess.run([
            'sudo', 'docker', 'exec', f'mysql{N}',
            'mysql', '-uroot', '-proot',
            '-e', "CREATE USER 'inno'@'%' IDENTIFIED BY 'inno'; GRANT ALL privileges ON *.* TO 'inno'@'%' with grant option; FLUSH PRIVILEGES;"
        ])

def verify_new_user():
    for N in range(1, 5):
        subprocess.run([
            'sudo', 'docker', 'exec', f'mysql{N}',
            'mysql', '-uinno', '-pinno',
            '-e', "SHOW VARIABLES WHERE Variable_name = 'hostname';"
            '-e', "SELECT user FROM mysql.user where user = 'inno';"
        ])
    time.sleep(30)

def docker_restart():
    subprocess.run(['sudo', 'docker', 'restart', 'mysql1', 'mysql2', 'mysql3', 'mysql4'])
    time.sleep(10)

def create_cluster():
    subprocess.run([
        'sudo', 'docker', 'exec', 'mysql1',
        'mysqlsh', '-uinno', '-pinno', '--', 'dba', 'create-cluster', 'testCluster'
    ])

def add_slave():
    subprocess.run([
        'sudo', 'docker', 'exec', 'mysql1',
        'mysqlsh', '-uinno', '-pinno', '--',
        'cluster', 'add-instance', '--uri=inno@mysql3', '--recoveryMethod=incremental'
    ])
    time.sleep(10)
    subprocess.run([
        'sudo', 'docker', 'exec', 'mysql1',
        'mysqlsh', '-uinno', '-pinno', '--',
        'cluster', 'add-instance', '--uri=inno@mysql4', '--recoveryMethod=incremental'
    ])

def router_bootstrap():
    subprocess.run([
        'sudo', 'docker', 'run', '-d',
        '--name', 'mysql-router',
        '--net=innodbnet',
        '-e', 'MYSQL_HOST=mysql1',
        '-e', 'MYSQL_PORT=3306',
        '-e', 'MYSQL_USER=inno',
        '-e', 'MYSQL_PASSWORD=inno',
        '-e', 'MYSQL_INNODB_CLUSTER_MEMBERS=4',
        router_docker_image
    ])

# Get the Docker ID of the running container
docker_id = subprocess.check_output(['sudo', 'docker', 'ps', '-q', '--filter', f'name={container_name}']).decode().strip()

# Define the pytest fixture to provide the host identifier
@pytest.fixture(scope='module')
def host():
    yield docker_id

# Create an instance of the Host class
class Host:
    def check_output(self, command):
        result = subprocess.run(['docker', 'exec', docker_id, 'bash', '-c', command], capture_output=True, text=True)
        return result.stdout.strip()

# Instantiate an instance of the Host class
host = Host()

class TestRouterEnvironment:
    def test_mysqlrouter_version(self, host):
        command = "mysqlrouter --version"
        output = host.check_output(command)
        assert "8.0.33" in output

    def test_mysqlsh_version(self, host):
        command = "mysqlsh --version"
        output = host.check_output(command)
        assert "8.0.33-25" in output

    def test_mysqlrouter_directory_permissions(self, host):
        assert host.file('/var/lib/mysqlrouter').user == 'mysqlrouter'
        assert host.file('/var/lib/mysqlrouter').group == 'mysqlrouter'
        assert oct(host.file('/var/lib/mysqlrouter').mode) == '0o755'

    def test_mysql_user(self, host):
        assert host.user('mysql').exists
        assert host.user('mysql').uid == 1001
        assert host.user('mysql').gid == 1001
        assert 'mysql' in host.user('mysql').groups
 
    def test_mysql_user(self, host):
        mysql_user = host.user('mysql')
        print(f"Username: {mysql_user.name}, UID: {mysql_user.uid}")
        assert mysql_user.exists
        assert mysql_user.uid == 1001
