import os
import typing

def base_requirements() -> typing.List[str]:
    return list(_load_dependencies_from_file("requirements.txt"))

def dev_requirements() -> typing.List[str]:
    return list(_load_dependencies_from_file("dev-requirements.txt"))

def extra_requirements() -> typing.Dict[str, typing.List[str]]:
    extras_require = {
    }
    return extras_require

def _is_ignored(line: str) -> bool:
    line = line.strip()
    return (not line) or (line[0] == "#") or line.startswith("git+")

def _extract_package_from_egg(line: str) -> str:
    if "#egg=" in line:
        _, package = line.split("#egg=")
        return f"{package} @ {line}"
    return line

def _load_dependencies_from_file(path: str, parent_dir: str = None) -> typing.List[str]:
    parent_dir = parent_dir or os.path.dirname(__file__)
    with open(f"{parent_dir}/{path}") as fp:
        return [
            _extract_package_from_egg(line.strip())
            for line in fp
            if not _is_ignored(line)
        ]

def _get_extra_dependencies(
    include: typing.List[str] = None,
    exclude: typing.List[str] = None,
    base_deps: typing.List[str] = None,
    extras_require: typing.Dict[str, typing.List[str]] = None,
) -> typing.List[str]:
    include = include or []
    exclude = exclude or []
    base_deps = base_deps or []
    extras_require = extras_require or {}
    extra_deps = set(base_deps)
    for extra_key, requirement_list in extras_require.items():
        if extra_key not in exclude and (not include or extra_key in include):
            extra_deps.update(requirement_list)
    return list(sorted(extra_deps))
