from pathlib import Path

from setuptools import setup, find_packages

requirements = Path("requirements.txt").read_text().splitlines()
version = Path("src/covid19_dashboard/__version__.py").read_text().split(" ")[-1].strip('"')

setup(
    name="covid19_dashboard",
    version=version,
    package_dir={"": "src"},
    packages=find_packages(where='src'),
    package_data={"covid19_dashboard": ["py.typed"]},
    include_package_data=True,
    python_requires=">=3.6.*",
    zip_safe=False,
    install_requires=requirements,
)
