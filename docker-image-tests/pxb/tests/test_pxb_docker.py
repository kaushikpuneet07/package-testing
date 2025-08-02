import pytest
import subprocess
import time
import os
import shutil
from settings import *

container_name = "mysql-test-container"
mount_dir = "-v /tmp/mysql_data:/var/lib/mysql -v /var/run/mysqld:/var/run/mysqld"
pxb_backup_dir = "/tmp/pxb_backup"
target_backup_dir = pxb_backup_dir
mysql_password = "mysql"
pxb_docker_image = "percona/percona-xtrabackup:8.4.0-3"
ps_docker_image = "percona/percona-server:8.4"

@pytest.fixture(scope="module", autouse=True)
def setup_mysql_container():
    os.makedirs("/tmp/mysql_data", exist_ok=True)
    os.makedirs(pxb_backup_dir, exist_ok=True)
    subprocess.run(["sudo", "chmod", "-R", "777", "/tmp/mysql_data", "/var/run/mysqld"], check=True)

    start_cmd = [
        "sudo", "docker", "run", "--name", container_name,
        *mount_dir.split(),
        "-p", "3306:3306",
        "-e", "PERCONA_TELEMETRY_DISABLE=1",
        "-e", "MYSQL_ROOT_HOST=%",
        "-e", f"MYSQL_ROOT_PASSWORD={mysql_password}",
        "-d", ps_docker_image
    ]
    subprocess.run(start_cmd, check=True)

    # Wait for MySQL to come up
    for i in range(180):
        result = subprocess.run(["sudo", "docker", "ps", "-a"], capture_output=True, text=True)
        if container_name in result.stdout and "Up" in result.stdout:
            break
        time.sleep(1)
    else:
        pytest.fail("MySQL did not start in Docker container")

    time.sleep(20)
    yield
    subprocess.run(["sudo", "docker", "rm", "-f", container_name], check=False)
    shutil.rmtree("/tmp/mysql_data", ignore_errors=True)
    shutil.rmtree(pxb_backup_dir, ignore_errors=True)

def test_mysql_and_pxb_backup_restore():
    # Confirm MySQL is up
    output = subprocess.check_output([
        "sudo", "docker", "exec", container_name,
        "mysql", "-uroot", f"-p{mysql_password}", "-Bse", "SELECT @@version;"
    ]).decode().strip()
    assert "8.0" in output

    # Create test data
    cmds = [
        "CREATE DATABASE IF NOT EXISTS test;",
        "CREATE TABLE test.t1(i INT);",
        "INSERT INTO test.t1 VALUES (1), (2), (3), (4), (5);"
    ]
    for cmd in cmds:
        subprocess.run([
            "sudo", "docker", "exec", container_name,
            "mysql", "-uroot", f"-p{mysql_password}", "-e", cmd
        ], check=True)

    # Run backup and prepare
    backup_cmd = (
        f"rm -rf {target_backup_dir}/* ; "
        f"xtrabackup --backup --datadir=/var/lib/mysql/ --target-dir={target_backup_dir} "
        f"--user=root --password={mysql_password} ; "
        f"xtrabackup --prepare --target-dir={target_backup_dir}"
    )
    subprocess.run([
        "sudo", "docker", "run", "--volumes-from", container_name,
        "-v", f"{pxb_backup_dir}:{pxb_backup_dir}", "-it", "--rm", "--user", "root",
        pxb_docker_image, "/bin/bash", "-c", backup_cmd
    ], check=True)

    # Stop container
    subprocess.run(["sudo", "docker", "stop", container_name], check=True)

    # Restore backup
    restore_cmd = f"xtrabackup --copy-back --datadir=/var/lib/mysql/ --target-dir={target_backup_dir}"
    subprocess.run([
        "sudo", "docker", "run", "--volumes-from", container_name,
        "-v", f"{pxb_backup_dir}:{pxb_backup_dir}", "-it", "--rm", "--user", "root",
        percona/percona-xtrabackup:8.4.0-3, "/bin/bash", "-c", restore_cmd
    ], check=True)

    subprocess.run(["sudo", "chmod", "-R", "777", "/tmp/mysql_data"], check=True)

    # Start MySQL again
    subprocess.run(["sudo", "docker", "start", container_name], check=True)

    for i in range(180):
        result = subprocess.run(["sudo", "docker", "ps", "-a"], capture_output=True, text=True)
        if container_name in result.stdout:
            break
        time.sleep(1)
    else:
        pytest.fail("MySQL failed to start after restore")

    time.sleep(20)

    # Verify data restored
    output = subprocess.check_output([
        "sudo", "docker", "exec", container_name,
        "mysql", "-uroot", f"-p{mysql_password}", "-Bse", "SELECT COUNT(*) FROM test.t1;"
    ]).decode().strip()
    assert output == "5"

