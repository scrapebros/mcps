from setuptools import setup, find_packages

setup(
    name="joycaption-mcp",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "mcp>=0.9.0",
        "torch>=2.0.0",
        "torchvision",
        "transformers>=4.36.0",
        "Pillow>=10.0.0",
        "accelerate>=0.25.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "joycaption-mcp=joycaption_mcp:main",
        ],
    },
)