from setuptools import setup, find_packages

setup(
    name='aemet-wind',
    version='0.0.1',
    url='https://github.com/lanecodes/aemet-wind.git',
    author='Andrew Lane',
    author_email='ajlane50@gmail.com',
    description='Download Spanish climate data from AEMET\'s REST API',
    packages=find_packages(),
    install_requires=['requests'],
)
