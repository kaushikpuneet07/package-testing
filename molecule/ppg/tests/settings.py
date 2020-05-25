import molecule.ppg.tests.settings_pg11 as pg11
import molecule.ppg.tests.settings_pg12 as pg12


versions = {"ppg-11.7": {"version": "11.7",
                         "deb_pkg_ver": pg11.DEB117_PKG_VERSIONS,
                         "deb_packages": pg11.DEB116_PACKAGES,
                         "percona-postgresql-common": '214',
                         "percona-postgresql-client-common": "214",
                         "libpq_version": "110007",
                         "pgaudit": pg11.pgaudit['ppg-11.7'],
                         "pgbackrest": pg11.pgbackrest['ppg-11.7'],
                         "patroni": pg11.patroni['ppg-11.7'],
                         "pgrepack": pg11.pgrepack['ppg-11.7'],
                         "libpq": "Version of libpq: 110007",
                         "deb_provides": pg11.DEB_PROVIDES,
                         "rpm7_provides": pg11.RPM7_PROVIDES,
                         'rpm_provides': pg11.RPM_PROVIDES,
                         "rpm_packages": pg11.RPM_PACKAGES,
                         "rpm7_packages": pg11.RPM7_PACKAGES,
                         "rhel_files": pg11.RHEL_FILES,
                         "deb_files": pg11.DEB_FILES,
                         "extensions": pg11.EXTENSIONS,
                         "languages": pg11.EXTENSIONS
                         },
            "ppg-11.6": {"version": "11.6",
                         "deb_pkg_ver": pg11.DEB116_PKG_VERSIONS,
                         "deb_packages": pg11.DEB116_PACKAGES,
                         "percona-postgresql-common": '210',
                         "percona-postgresql-client-common": "210",
                         "libpq_version": "110006",
                         "pgaudit": pg11.pgaudit['ppg-11.6'],
                         "pgbackrest": pg11.pgbackrest['ppg-11.6'],
                         "patroni": pg11.patroni['ppg-11.6'],
                         "pgrepack": pg11.pgrepack['ppg-11.6'],
                         "libpq": "Version of libpq: 110006",
                         "deb_provides": pg11.DEB_PROVIDES,
                         "rpm7_provides": pg11.RPM7_PROVIDES,
                         'rpm_provides': pg11.RPM_PROVIDES,
                         "rpm_packages": pg11.RPM_PACKAGES,
                         "rpm7_packages": pg11.RPM7_PACKAGES,
                         "rhel_files": pg11.RHEL_FILES,
                         "deb_files": pg11.DEB_FILES,
                         "extensions": pg11.EXTENSIONS,
                         "languages": pg11.EXTENSIONS
                         },
            "ppg-11.5": {"version": "11.5", "deb_pkg_ver": pg11.DEB_PKG_VERSIONS,
                         "deb_packages": pg11.DEB_PACKAGES,
                         "percona-postgresql-common": '204',
                         "percona-postgresql-client-common": "204",
                         "libpq_version": "110005",
                         "deb_provides": pg11.DEB_PROVIDES,
                         "rpm7_provides": pg11.RPM7_PROVIDES,
                         'rpm_provides': pg11.RPM_PROVIDES,
                         "pgaudit": pg11.pgaudit['ppg-11.5'],
                         "pgbackrest": pg11.pgbackrest['ppg-11.5'],
                         "patroni": pg11.patroni['ppg-11.5'],
                         "pgrepack": pg11.pgrepack['ppg-11.5'],
                         "libpq": "Version of libpq: 110005"
                         },
            "ppg-12.2": {"version": "12.2", "deb_pkg_ver": pg12.DEB116_PKG_VERSIONS,
                         "deb_packages": pg12.DEB116_PACKAGES,
                         "percona-postgresql-common": '214',
                         "percona-postgresql-client-common": "214",
                         "libpq_version": "120002",
                         "pgaudit": pg12.pgaudit['ppg-12.2'],
                         "pgbackrest": pg12.pgbackrest['ppg-12.2'],
                         "patroni": pg12.patroni['ppg-12.2'],
                         "pgrepack": pg12.pgrepack['ppg-12.2'], "libpq": "Version of libpq: 120002",
                         "deb_provides": pg12.DEB_PROVIDES,
                         "rpm7_provides": pg12.RPM7_PROVIDES,
                         'rpm_provides': pg12.RPM_PROVIDES,
                         "rpm_packages": pg12.RPM_PACKAGES,
                         "rpm7_packages": pg12.RPM7_PACKAGES,
                         "rhel_files": pg12.RHEL_FILES,
                         "deb_files": pg12.DEB_FILES,
                         "extensions": pg12.EXTENSIONS,
                         "languages": pg12.EXTENSIONS
                         }
            }
