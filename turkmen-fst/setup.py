# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="turkmen-fst",
    version="1.0.0",
    description="Türkmen Türkçesi Morfolojik Analiz ve Sentez Sistemi",
    author="TurkmenFST Project",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[],
    extras_require={
        "api": ["fastapi>=0.100.0", "uvicorn>=0.20.0"],
        "web": ["flask>=2.0.0"],
        "dev": ["pytest>=7.0.0", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "turkmen-fst=turkmen_fst.cli:main",
        ],
    },
    package_data={
        "": ["*.txt"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Turkmen",
        "Topic :: Text Processing :: Linguistic",
    ],
)
