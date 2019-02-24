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

from . import logging_format_template

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


def add_libraries(package, folder):
    current_directory = os.getcwd()
    os.chdir(folder)
    files = list(Path('.').glob('**/*'))
    for f in files:
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
    folder = tempfile.mkdtemp('lambda_')
    logger.info(f'Created temporary working directory: {folder}')

    if requirements:
        logger.info(f'Downloading requirements from file: {args.requirement_file.name}')
        download_requirements(requirements, folder)
        logger.info(f'Packaging requirements...')
        add_libraries(package, folder)

    # add the lambda code
    logger.info(f'Adding lambda function: {args.function_file.name}')
    package.write(args.function_file.name)
    package.close()
    logger.info(f'Removing working directory: {folder}')
    shutil.rmtree(folder)


if __name__ == '__main__':
    main()
