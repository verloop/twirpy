from setuptools import setup

with open('version.txt') as f:
    version = f.read().strip()

setup(name="twirp",
      version=version,
      description="Twirp server and client lib",
      licesnse='unlicense',
      packages=['twirp'],
      install_requires=[
            'requests',
            'structlog',
            'protobuf'
      ],
      test_requires=[
      ],
      zip_safe=False)
