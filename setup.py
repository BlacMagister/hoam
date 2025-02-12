from setuptools import setup, find_packages

setup(
    name="blockchain-pro",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'cryptography>=41.0.3',
        'python-dotenv>=1.0.0',
        'fastapi>=0.95.0',
        'uvicorn>=0.21.1',
        'libp2p>=0.5.1',
        'pydantic>=2.0'
    ],
    entry_points={
        'console_scripts': [
            'blockchain-node=blockchain.main:main',
            'blockchain-cli=blockchain.cli:main'
        ]
    }
)
