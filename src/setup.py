from setuptools import setup, find_packages

setup(
    name='dbterd',
    version='0.0.1',    
    description='A simple package that can generate dbml file and erd diagrams for dbt',
    url='https://github.com/intellishore/dbt-erdiagram-generator',
    author='Oliver Rise Thomsen, Anders Boje Hertz',
    author_email='oliver.thomsen@intellishore.dk',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['pyyaml', 'Click'],
    
    entry_points='''
        [console_scripts]
        dbterd=dbterd.terminal:cli
    ''',
)
