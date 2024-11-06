from setuptools import setup, find_packages

setup(
    name='oversight',
    version='0.10',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        req.strip() for req in open('requirements.txt').readlines()
    ],
    entry_points={
        'console_scripts': [
            'oversight=oversight.app:main',  # Update this line to the correct module path
        ],
    },
)
