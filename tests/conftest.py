from pathlib import Path

import tomllib


def _parse_repositories(test_config):
    return (
        test_config["location"],
        test_config.get("files", []),
        test_config.get("ignored_files", []),
        test_config.get("dh_kwargs", {}),
    )


def pytest_addoption(parser):
    parser.addoption("--service", action="store", default=None, help="Service to test")


def pytest_generate_tests(metafunc):
    with open(Path("tests", "test_repositories.toml"), "rb") as f:
        test_repos = tomllib.load(f)

    if "location" in metafunc.fixturenames:
        if service_value := metafunc.config.option.service:
            metafunc.parametrize(
                "location,files,ignored_files,dh_kwargs",
                map(_parse_repositories, test_repos[service_value]),
            )
        else:
            if service_value and service_value not in test_repos:
                raise ValueError(f"Unknown service {service_value}")

            metafunc.parametrize(
                "location,files,ignored_files,dh_kwargs",
                map(
                    _parse_repositories,
                    [v for _, service_v in test_repos.items() for v in service_v],
                ),
            )
