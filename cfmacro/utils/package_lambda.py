#!/usr/bin/env python
import argparse
import logging
import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from subprocess import CalledProcessError
import setuptools

from . import logging_format_template
from .. import __version__

__author__ = "Giuseppe Chiesa"
__copyright__ = "Copyright 2017, Giuseppe Chiesa"
__credits__ = ["Giuseppe Chiesa"]
__license__ = "BSD"
__maintainer__ = "Giuseppe Chiesa"
__email__ = "mail@giuseppechiesa.it"
__status__ = "PerpetualBeta"

logging.basicConfig(level=logging.INFO, format=logging_format_template)


def check_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--requirements',
                        help='Requirement file',
                        dest='requirement_file',
                        default='requirements.txt',
                        type=argparse.FileType('r'))
    parser.add_argument('-f', '--function',
                        help='Lambda function',
                        dest='function_file',
                        required=True,
                        type=argparse.FileType('r'))
    parser.add_argument('-o', '--output',
                        help='Package output file',
                        dest='output_file',
                        type=argparse.FileType('wb'),
                        required=True)
    return parser.parse_args()


def download_requirements(requirements, folder):
    data = '\n'.join([line for line in requirements])
    with open(os.path.join(folder, 'requirements.txt'), 'wb') as fp:
        fp.write(data.encode('utf-8'))
    try:
        subprocess.check_call(['pip', 'install', '-r', 'requirements.txt', '--target', '.'], cwd=folder)
    except CalledProcessError:
        raise


def add_libraries(package, folder, query='.', glob_query='**/*'):
    logger = logging.getLogger('add-libraries')
    current_directory = os.getcwd()
    os.chdir(folder)
    files = list(Path(query).glob(glob_query))
    for f in files:
        if str(f).endswith('.pyc'):
            continue
        logger.info(f'adding file {f}')
        package.write(f)
    os.chdir(current_directory)


def main():
    logger = logging.getLogger(__name__)
    args = check_args()

    # read the requirement file
    requirements = [r.strip() for r in args.requirement_file.readlines()]

    # create a zipfile
    logger.info(f'Creating output package: {args.output_file.name}')
    package = zipfile.ZipFile(args.output_file.name, 'w')

    # set a temp folder
    temp_folder = tempfile.mkdtemp('lambda_')
    logger.info(f'Created temporary working directory: {temp_folder}')

    if requirements:
        logger.info(f'Downloading requirements from file: {args.requirement_file.name}')
        download_requirements(requirements, temp_folder)
        logger.info(f'Packaging requirements...')
        add_libraries(package, temp_folder)

    # looking for additional python packages
    function_file_path = os.path.dirname(os.path.realpath(args.function_file.name))
    # save the original folder
    orig_path = os.getcwd()
    # enter the function folder
    os.chdir(function_file_path)
    level_packages = setuptools.find_packages(where=function_file_path)
    if level_packages:
        # in this case we need to create a python package with the lambda inside in order to be usable
        # from AWS lambda
        logger.info(f'Detected lambda sibling packages: {level_packages}\nA package folder will be created')
        # create the folder name
        python_package_path = os.path.join(temp_folder, os.path.basename(args.function_file.name).replace('.py', ''))

        # copy the content of the lambda + sibling packages and files in the python package path
        logger.info('Copying {s} to {d}'.format(s=function_file_path, d=python_package_path))
        shutil.copytree(function_file_path, python_package_path)
        logger.info(f'Folder {function_file_path} added to the lambda package {python_package_path}')

        # add the entire folder to the zip
        logger.info('Adding python package: {p} to the zip'.format(p=python_package_path))
        add_libraries(package, folder=temp_folder, query='.',
                      glob_query='{}/**/*'.format(os.path.basename(python_package_path)))
        logger.warning('** BE AWARE: lambda functions is reachable inside python package now!')
    else:
        # add the lambda code
        logger.info(f'Adding lambda function: {args.function_file.name}')
        package.write(args.function_file.name)

    package.close()
    os.chdir(orig_path)
    logger.info(f'Removing working directory: {temp_folder}')
    shutil.rmtree(temp_folder)


if __name__ == '__main__':
    main()
