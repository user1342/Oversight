from setuptools import setup, find_packages

setup(
    name='oversight',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'transformers',
        'torch',
        # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'oversight=oversight.app:main',
        ],
    },
)
