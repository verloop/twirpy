from setuptools import setup

with open('version.txt') as f:
    version = f.read().strip()

with open('README.md', encoding='utf-8') as f:
      long_description = f.read().strip()

setup(name="twirp",
      version=version,
      description="Twirp server and client lib",
      long_description=long_description,
      long_description_content_type='text/markdown',
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
