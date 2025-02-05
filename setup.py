import os
from setuptools import setup, find_packages

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Read requirements.txt
with open(os.path.join(BASE_DIR, "requirements.txt")) as f:
    install_requires = f.read().splitlines()

setup(
    name="ss-scrapping",
    version="0.2",
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "topuniversities = ss_scrapping.topuniversities.topuniversities:main",
            "usnews = ss_scrapping.usnews.usnews:main",
            "niche = ss_scrapping.niche.niche:main",
            "whed = ss_scrapping.whed.whed:main",
        ],
    },
    author="Parijat Srivastava",
    description="A Python package for top 500 universities",
)
