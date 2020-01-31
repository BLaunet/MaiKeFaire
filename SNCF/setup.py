from setuptools import setup, find_namespace_packages
version = '0.0.1'
packages = find_namespace_packages()
setup(
    name="sncf_crawler",
    packages=packages,
    url='https://github.com/BLaunet/MaiKeFaire',
    version=version,
    include_package_data=False,
    platforms='any',
)
