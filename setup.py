from setuptools import setup, find_packages

setup(
    name="chat_app",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'pandas',
        'apscheduler',
        'langchain-community',
        'langchain-huggingface',
        'fuzzywuzzy',
        'python-dotenv',
        'requests',
        'chromadb',
        'sentence-transformers',
    ],
    entry_points={
        'console_scripts': [
            'your_package=your_package.app:main',
        ],
    },
)