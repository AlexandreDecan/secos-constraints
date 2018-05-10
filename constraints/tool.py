import requests
import os
import time
import logging
import sys
import math
import argparse

import tqdm

from urllib.parse import quote_plus
from datetime import datetime
from itertools import cycle
from collections import OrderedDict

from . import parser
from . import constraints

PARSER = {
    'Cargo': parser.CargoParser(),
    'NPM': parser.NPMParser(),
    'Packagist': parser.PackagistParser(),
    'Rubygems': parser.RubyGemsParser(),
}

PKG_URL = 'https://libraries.io/api/{platform}/{package}'
DEPS_URL = 'https://libraries.io/api/{platform}/{package}/{version}/dependencies'
REV_DEPS_URL = 'https://libraries.io/api/{platform}/{package}/dependents'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
PER_PAGE = 100

logging.basicConfig(
    level=logging.CRITICAL,
    format='[%(levelname)-8s] %(asctime)s :: %(message)s'
)
logger = logging.getLogger(__name__)


def get_url(url, params=None):
    params = {} if params is None else params
    
    logger.debug('get: {} ({})'.format(url, params))
    
    status_code = 403
    while status_code in [403, 429]:
        r = requests.get(url, params=params)
        status_code = r.status_code
        logger.debug('x-ratelimit-remaining: {}'.format(r.headers.get('x-ratelimit-remaining', None)))
        
        if status_code == 200:
            logger.debug('hit!')
            return r
        elif status_code == 404:
            return None
        elif status_code in [403, 429]:
            # Check header
            ratelimit = r.headers.get('x-ratelimit-remaining', None)
            
            if ratelimit is None or ratelimit > 0:
                logger.warning('403/429 with x-ratelimit-remaining set to {}'.format(ratelimit))
                time.sleep(5)
            
            time.sleep(1)
        else:
            raise ValueError('"{}" returns code {}'.format(url, status_code))


def main(platform, package_name, key, verbose):
    # Check that package exists
    r = get_url(PKG_URL.format(platform=platform, package=quote_plus(package_name)), {'key': key})
    if r is None:
        sys.exit('Aborting: package {} not found for {}'.format(package_name, platform))
    
    package = r.json()
    print('Package {} found on {}'.format(package['name'], package['platform']))
    
    # Retrieve dependents
    if package['dependents_count'] == 0:
        sys.exit('Aborting: package has no dependent')
    print('Found {} potential dependents'.format(package['dependents_count']))
    
    dependents = []
    nb_pages = math.ceil(package['dependents_count'] / PER_PAGE)
    logger.info('nb page: {}'.format(nb_pages))
    
    try:
        for page in tqdm.tqdm(range(1, nb_pages + 1), leave=False):
            logger.info('page {}'.format(page))
            r = get_url(
                REV_DEPS_URL.format(platform=platform, package=quote_plus(package_name)),
                {'key': key, 'per_page': PER_PAGE, 'page': page}
            )
            
            for dependent in r.json():
                if dependent['platform'] == package['platform']:
                    for version in dependent['versions']:
                        try:
                            published_at = datetime.strptime(version['published_at'], DATE_FORMAT)
                        except ValueError as e:
                            logger.warning('Unable to parse {}'.format(version['published_at']))
                            continue
                            
                        dependents.append((
                            dependent['name'],
                            version['number'],
                            published_at
                        ))
                else:
                    logger.info('Dependent {} not on {} (is on {})'.format(dependent['name'], package['platform'], dependent['platform']))
    except KeyboardInterrupt:
        print('Aborting')
        
    # Group by month
    dependents.sort(key=lambda t: t[2], reverse=True)
    months = OrderedDict()
    
    for name, version, date in dependents:
        current = months.setdefault((date.year, date.month), {})
        # Take last release of each dependents
        current[name] = version
    
    try:
        for (year, month), dependent in months.items():
            
            dependencies = []
            for name, version in tqdm.tqdm(dependent.items(), leave=False):
                version_data = get_url(DEPS_URL.format(platform=platform, package=quote_plus(name), version=version), {'key': key})
                
                if version_data is None:
                    logger.warning('Unknown package {}@{}'.format(name, version))
                    continue
                    
                for dependency in version_data.json()['dependencies']:
                    if dependency['name'] == package_name and dependency['platform'] == package['platform']:
                        dependencies.append(dependency['requirements'])
            
            # Convert & display summary
            if len(dependencies) == 0:
                print('None collected')
                
            dependencies = [parser.parse_or_empty(PARSER[platform], x) for x in dependencies]
            
            total = M = m = p = o = 0
            for dep in dependencies:
                aM = constraints.allows_major(dep)
                am = constraints.allows_minor(dep)
                ap = constraints.allows_patch(dep)
                total += 1
                M += int(aM)
                m += int(am)
                p += int(ap)
                o += 1 - int(aM or am or ap)
            
            if total == 0:
                print('None collected')
                continue
            
            def f(v): return '*' * round(v / 0.2)
            if verbose:
                print('[{}-{:0>2}] ({:3} cons.)\tM {:<5}\tm {:<5}\tp {:<5}\to {:<5}'.format(
                    year, month,
                    total,
                    f(M / total), f(m / total), f(p / total), f(o / total)
                ))
            else:
                print('[{}-{:0>2}] ({:3} cons.)\tm {:<5}\tp {:<5}'.format(
                    year, month,
                    total,
                    f(m / total), f(p / total)
                ))
            logger.info(' / '.join([str(d) for d in dependencies]))
            
    except KeyboardInterrupt:
        sys.exit('Aborting')


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Version constraint usage')
    argparser.add_argument('package_name', type=str, nargs=1, help='Name of the package')
    argparser.add_argument('--platform', choices=['NPM', 'Cargo', 'Packagist', 'Rubygems'], required=True, help='platform where package is hosted')
    argparser.add_argument('--key', type=str, required=True, help='API key for libraries.io')
    argparser.add_argument('-v', '--verbose', action='store_true', required=False, help='Verbose mode')
    argparser.add_argument('--debug', action='store_true', required=False, help='Display debug information')
    
    args = argparser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    main(args.platform, args.package_name[0], args.key, args.verbose)
