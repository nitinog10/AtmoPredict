"""Check if required packages are installed"""

import sys
print(f"Python version: {sys.version}")
print("-" * 60)

packages = [
    'numpy',
    'pandas', 
    'sklearn',
    'xgboost',
    'lightgbm',
    'joblib',
    'matplotlib',
    'seaborn',
    'plotly'
]

missing = []
installed = []

for package in packages:
    try:
        if package == 'sklearn':
            import sklearn
            print(f"✓ scikit-learn {sklearn.__version__}")
            installed.append('scikit-learn')
        else:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            print(f"✓ {package} {version}")
            installed.append(package)
    except ImportError:
        print(f"✗ {package} NOT INSTALLED")
        missing.append(package)
    except Exception as e:
        print(f"✗ {package} ERROR: {str(e)}")
        missing.append(package)

print("-" * 60)
print(f"\nInstalled: {len(installed)} packages")
print(f"Missing: {len(missing)} packages")

if missing:
    print("\nTo install missing packages, run:")
    print(f"pip install {' '.join(missing)}")
else:
    print("\n✓ All required packages are installed!")
    print("\nYou can now run: python src\\train_models.py")
