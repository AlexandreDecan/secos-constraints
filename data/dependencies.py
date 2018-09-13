import pandas
import tqdm
import os
import sys

sys.path.append('..')

from constraints.parser import (
    CargoParser, NPMParser, PackagistParser, RubyGemsParser,
    parse_or_empty,
)
from constraints import constraints as analyzer

ECOSYSTEMS = ['Cargo', 'NPM', 'Packagist', 'Rubygems']
PARSERS = {
    'Cargo': CargoParser(),
    'NPM': NPMParser(),
    'Packagist': PackagistParser(),
    'Rubygems': RubyGemsParser(),
}
VERSIONS_INPUT_PATH = '{}-versions.csv.gz'
DEPS_INPUT_PATH = '../data-raw/{}-dependencies.csv.gz'
OUTPUT_PATH = './{}-dependencies.csv.gz'


if __name__ == '__main__':
    
    for ecosystem in ECOSYSTEMS:
        if os.path.isfile(OUTPUT_PATH.format(ecosystem)):
            print('Skipping {}'.format(ecosystem))
            continue

        print('Loading versions for {}'.format(ecosystem))
        df_versions = pandas.read_csv(VERSIONS_INPUT_PATH.format(ecosystem))

        print('Loading dependencies data for {}'.format(ecosystem))
        df_dependencies = pandas.read_csv(DEPS_INPUT_PATH.format(ecosystem))
                
        print('Filtering dependencies')

        df_dependencies = (
            df_dependencies
            .merge(
                df_versions[['package', 'version']],
                how='inner',
                on=['package', 'version'],
            )
        )

        print('Converting constraints to intervals')
        print('.. drop duplicates')
        df_constraints = df_dependencies[['constraint']].drop_duplicates()
        
        print('.. convert constraints')
        
        def _func(c): return parse_or_empty(PARSERS[ecosystem], c)
        df_constraints['interval'] = df_constraints['constraint'].apply(_func)
        
        print('.. analyse intervals')
        for label in ['empty', 'dev', 'allows_major', 'allows_minor', 'allows_patch', 'allows_compatible', 'allows_incompatible', 'allows_all_compatible', 'allows_compatible_only', 'allows_all_compatible_only', 'upper_bounded', 'lower_bounded', 'strict']:
            df_constraints[label] = df_constraints['interval'].apply(getattr(analyzer, label))
        
        print('.. merge results')
        df_dependencies = (
            df_dependencies
            .merge(
                df_constraints,
                how='left',
                on=['constraint']
            )
        )
        
        print('Saving data')
        df_dependencies.to_csv(
            OUTPUT_PATH.format(ecosystem),
            index=False,
            compression='gzip',
        )
        
        print()
