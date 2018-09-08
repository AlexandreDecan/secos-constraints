import pandas
import tqdm
import os


ECOSYSTEMS = ['Cargo', 'NPM', 'Packagist', 'Rubygems']

INPUT_PATH = '../data-raw/{}-versions.csv.gz'
OUTPUT_PATH = './{}-versions.csv.gz'

RE_SEMVER = r'^(?:v|V)?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<misc>.*)$'


if __name__ == '__main__':
    
    for ecosystem in ECOSYSTEMS:
        if os.path.isfile(OUTPUT_PATH.format(ecosystem)):
            print('Skipping {}'.format(ecosystem))
            continue
        
        print('Loading data for {}'.format(ecosystem))
        df_versions = pandas.read_csv(INPUT_PATH.format(ecosystem)).dropna()
        
        # Remove funny packages from NPM
        if ecosystem == 'NPM':
            df_versions = (
                df_versions
                # March 2016
                [lambda d: ~d['package'].str.startswith('@ryancavanaugh')]
                [lambda d: ~d['package'].str.startswith('all-packages-')]
                [lambda d: ~d['package'].str.startswith('cool-')]
                [lambda d: ~d['package'].str.startswith('neat-')]
                [lambda d: ~d['package'].str.startswith('wowdude-')]
                
                # April & May 2017
                [lambda d: ~d['package'].str.startswith('npmdoc')]
                [lambda d: ~d['package'].str.startswith('npmtest')]
                [lambda d: ~d['package'].str.startswith('npm-ghost')]
                [lambda d: ~d['package'].str.startswith('ghost-')]
                [lambda d: ~d['package'].str.endswith('-cdn')]
            )
        
        print('Identifying semver components')
        df_versions[['major', 'minor', 'patch', 'misc']] = (
            df_versions['version'].str.extract(RE_SEMVER, expand=True)
        )
        
        print('Converting components')
        for component in ['major', 'minor', 'patch']:
            df_versions[component] = df_versions[component].astype(float)
        
        print('Computing release order and release type')
        data = []
        for name, group in tqdm.tqdm(df_versions.groupby('package', sort=False)):
            group = (
                group
                .sort_values(['major', 'minor', 'patch', 'date'])
                # Remove pre-releases by only keeping the latest "misc".
                .drop_duplicates(['major', 'minor', 'patch'], keep='last')
                .assign(
                    rank=lambda d: d.assign(N=1).N.cumsum(),
                    # previous_date=lambda d: d['date'].shift(1),
                    # next_date=lambda d: d['date'].shift(-1),
                    is_initial=lambda d: d['major'].shift(1).isnull(),
                    is_major=lambda d: (d['major'] - d['major'].shift(1)).clip(0, 1).astype(bool),
                    is_minor=lambda d: (d['minor'] - d['minor'].shift(1)).clip(0, 1).astype(bool),
                    is_patch=lambda d: (d['patch'] - d['patch'].shift(1)).clip(0, 1).astype(bool),
                )
            )
            data.append(group)
        
        print('Grouping results into a dataframe')
        df_semver = (
            pandas.concat(data)
            .assign(type=lambda d: d[['is_initial', 'is_major', 'is_minor', 'is_patch']].idxmax(axis=1))
            .drop(columns=['is_initial', 'is_major', 'is_minor', 'is_patch'])
            .replace({'type': {
                'is_initial': 'initial',
                'is_major': 'major',
                'is_minor': 'minor',
                'is_patch': 'patch',
            }})
            .drop_duplicates()
        )
        
        print('Saving data')
        df_semver.to_csv(
            OUTPUT_PATH.format(ecosystem),
            index=False,
            compression='gzip',
        )
        
        print()
