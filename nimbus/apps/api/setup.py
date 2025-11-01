"""Setup configuration for nimbus-analytics."""
from setuptools import setup, find_packages

# Read README for long description
with open("README_PYPI.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nimbus-analytics",
    version="0.1.0b1",  # Beta version
    author="Bahagh",
    author_email="baha.ghrissi@esprit.tn",
    description="Open-source alternative to Segment & Mixpanel - High-performance event analytics backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bahagh/nimbus",
    project_urls={
        "Bug Tracker": "https://github.com/bahagh/nimbus/issues",
        "Documentation": "https://github.com/bahagh/nimbus#readme",
        "Source Code": "https://github.com/bahagh/nimbus",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Database",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn>=0.30.0",
        "sqlalchemy>=2.0.32",
        "asyncpg>=0.29.0",
        "pydantic>=2.8.2",
        "pydantic-settings>=2.4.0",
        "pyjwt>=2.8.0",
        "bcrypt>=4.1.3",
        "redis>=5.0.7",
        "structlog>=24.1.0",
        "slowapi>=0.1.9",
        "alembic>=1.13.2",
        "python-multipart>=0.0.9",
        "cryptography>=43.0.0",
        "python-jose>=3.3.0",
        "requests>=2.32.3",
        "email-validator>=2.1.0",
        "httpx>=0.27.0",
    ],
    keywords="analytics fastapi events metrics postgresql redis async segment mixpanel alternative",
    license="MIT",
)
