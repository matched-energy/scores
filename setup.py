from setuptools import setup, find_packages

setup(
    name="scores",
    version="0.1.0",
    url="https://github.com/matched-energy/scores",
    author="Matched Energy",
    author_email="info@matched.energy",
    description="",
    packages=find_packages(include=["scores", "scores.*"]),
    install_requires=[
        "pandas >= 2.0.0",
    ],
)
