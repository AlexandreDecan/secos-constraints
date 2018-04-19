"""
This script requires Versions.csv and Dependencies.csv.
It parses them and retrieve the useful data, and generates [ECO]-versions.csv.gz
and [ECO]-dependencies.csv.gz.
"""

import pandas
import subprocess

ECOSYSTEMS = ['cargo', 'packagist', 'npm', 'rubygems']
VERSIONS = {
    'Project Name': 'package',
    'Number': 'version',
    'Published Timestamp': 'date',
}
DEPENDENCIES = {
    'Project Name': 'package',
    'Version Number': 'version',
    'Dependency Name': 'target',
    'Dependency Kind': 'kind',
    'Dependency Requirements': 'constraint',
}
KINDS = {
    'cargo': ['normal', 'runtime'],
    'packagist': ['runtime'],
    'npm': ['runtime'],
    'rubygems': ['runtime']
}


if __name__ == '__main__':
    for ecosystem in ECOSYSTEMS:
        print('Extracting data for {}'.format(ecosystem))
        with open('temp-versions.csv', 'w') as out:
            subprocess.call(['head', '-1', 'Versions.csv'], stdout=out)
            subprocess.call(['grep', '"{}"'.format(ecosystem), 'Versions.csv'], stdout=out)

        with open('temp-dependencies.csv', 'w') as out:
            subprocess.call(['head', '-1', 'Dependencies.csv'], stdout=out)
            subprocess.call(['grep', '"{}"'.format(ecosystem), 'Dependencies.csv'], stdout=out)

        print('Loading data in memory')
        
        df_versions = pandas.read_csv(
            'temp-versions.csv',
            index_col=False,
            usecols=list(VERSIONS.keys() + ['Platform'])
        ).rename(columns=VERSIONS).query('Platform == "{}"'.format(ecosystem))
        
        df_deps = pandas.read_csv(
            'temp-dependencies.csv',
            index_col=False,
            usecols=list(DEPENDENCIES.keys() + ['Platform'])
        ).rename(columns=DEPENDENCIES).query('Platform == "{}"'.format(ecosystem))
        print('.. {} versions and {} dependencies loaded'.format(len(df_versions), len(df_deps)))
        
        print('Filtering dependencies based on "kind"')
        # Filter dependencies based on "kind"
        df_deps = df_deps.query(' or '.join(['kind == "{}"'.Format(kind) for kind in KINDS[ecosystem]]))
        print('.. {} remaining dependencies'.format(len(df_deps)))
        
        print('Removing unknown packages')
        # Only keep known packages
        df_deps = df_deps[df_deps['target'].isin(df_versions['package'])]
        print('.. {} remaining dependencies'.format(len(df_deps)))

        print('Exporting to compressed csv')
        # Export
        df_versions.to_csv(
            '{}-versions.csv.gz',
            index=False,
            compression='gzip',
        )
        
        df_deps.to_csv(
            '{}-dependencies.csv.gz',
            index=False,
            compression='gzip',
        )
        print('Deleting temporary files')
        subprocess.call(['rm', 'temp-versions.csv'])
        subprocess.call(['rm', 'temp-dependencies.csv'])
        print()
