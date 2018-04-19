"""
This script requires Versions.csv and Dependencies.csv.
It parses them and retrieve the useful data, and generates [ECO]-versions.csv.gz
and [ECO]-dependencies.csv.gz.
"""

import pandas
import subprocess
import os


ECOSYSTEMS = ['Cargo', 'Packagist', 'NPM', 'Rubygems']
VERSIONS = {
    'Platform': 'platform',
    'Project Name': 'package',
    'Number': 'version',
    'Published Timestamp': 'date',
}
DEPENDENCIES = {
    'Platform': 'platform',
    'Project Name': 'package',
    'Version Number': 'version',
    'Dependency Name': 'target',
    'Dependency Kind': 'kind',
    'Dependency Requirements': 'constraint',
    'Dependency Platform': 'target_platform',
}
KINDS = {
    'Cargo': ['normal', 'runtime'],
    'Packagist': ['runtime'],
    'NPM': ['runtime'],
    'Rubygems': ['runtime']
}


if __name__ == '__main__':
    for ecosystem in ECOSYSTEMS:
        if os.path.isfile('{}-versions.csv.gz'.format(ecosystem)) and os.path.isfile('{}-dependencies.csv.gz'.format(ecosystem)):
            print('Skipping {}'.format(ecosystem))
            continue
            
        print('Extracting data for {}'.format(ecosystem))
        with open('temp-versions.csv', 'w') as out:
            subprocess.call(['head', '-1', 'versions.csv'], stdout=out)
            subprocess.call(['grep', ',{},'.format(ecosystem), 'versions.csv'], stdout=out)

        with open('temp-dependencies.csv', 'w') as out:
            subprocess.call(['head', '-1', 'dependencies.csv'], stdout=out)
            subprocess.call(['grep', ',{},'.format(ecosystem), 'dependencies.csv'], stdout=out)

        print('Loading data in memory')
        df_versions = pandas.read_csv(
            'temp-versions.csv',
            index_col=False,
            engine='c',
            low_memory=False,
            usecols=list(VERSIONS.keys())
        ).rename(columns=VERSIONS).query('platform == "{}"'.format(ecosystem))
        
        df_deps = pandas.read_csv(
            'temp-dependencies.csv',
            index_col=False,
            engine='c',
            low_memory=False,
            usecols=list(DEPENDENCIES.keys())
        ).rename(columns=DEPENDENCIES).query('platform == "{0}" and target_platform == "{0}"'.format(ecosystem))
        print('.. {} versions and {} dependencies loaded'.format(len(df_versions), len(df_deps)))
        
        print('Filtering dependencies based on "kind"')
        df_deps = df_deps.query(' or '.join(['kind == "{}"'.format(kind) for kind in KINDS[ecosystem]]))
        print('.. {} remaining dependencies'.format(len(df_deps)))
        
        print('Removing unknown packages')
        packages = df_versions['package'].drop_duplicates()
        print('.. {} known packages'.format(len(packages)))
        df_deps = df_deps[df_deps['target'].isin(packages)]
        print('.. {} remaining dependencies'.format(len(df_deps)))

        print('Exporting to compressed csv')
        df_versions[['package', 'version', 'date']].to_csv(
            '{}-versions.csv.gz'.format(ecosystem),
            index=False,
            compression='gzip',
        )
        
        df_deps[['package', 'version', 'target', 'constraint']].to_csv(
            '{}-dependencies.csv.gz'.format(ecosystem),
            index=False,
            compression='gzip',
        )
        print('Deleting temporary files')
        subprocess.call(['rm', 'temp-versions.csv'])
        subprocess.call(['rm', 'temp-dependencies.csv'])
        print()
