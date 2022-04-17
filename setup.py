from setuptools import setup, find_namespace_packages
import shutil
import glob


setup(name='py-drive-client',
      version='1.0',
      author='jmv74211',
      author_email='jmv74211@gmail.com',
      license='GPLv3',
      python_requires=">=3.6",
      url='https://github.com/jmv74211/py-drive-client',
      description='App to manage files in Google drive from local console.',
      long_description=open('README.md').read(),
      entry_points={'console_scripts': ['py-drive-client=py_drive_client.py_drive_client:main']},
      install_requires=["PyDrive==1.3.1"],
      package_dir={"": "src/"},
      packages=find_namespace_packages(where="src"),
      include_package_data=True,
      package_data={'py_drive_client': ['credentials/client_secrets.json']},
      zip_safe=False)


# Clean build files
shutil.rmtree('dist')
shutil.rmtree('build')
shutil.rmtree(glob.glob('src/*.egg-info')[0])
