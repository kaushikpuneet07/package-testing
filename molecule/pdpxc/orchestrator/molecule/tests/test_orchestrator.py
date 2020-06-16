import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


DEBPACKAGES = ['percona-orchestrator-cli', 'percona-orchestrator-client', 'percona-orchestrator']


@pytest.mark.parametrize("package", DEBPACKAGES)
def test_check_deb_package(host, package):
    dist = host.system_info.distribution
    if dist.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed
    assert '3.1.4' in pkg.version, pkg.version


def test_check_rpm_package(host):
    dist = host.system_info.distribution
    if dist.lower() in ["debian", "ubuntu"]:
        pytest.skip("This test only for RHEL based platforms")
    pkg = host.package('percona-orchestrator')
    assert pkg.is_installed
    assert '3.1.4' in pkg.version, pkg.version

def test_orchestrator_binary(host):
    pass
