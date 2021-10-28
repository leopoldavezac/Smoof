from pandas import DataFrame, read_csv

from dash import Dash

SAMPLE_SIZE = 10000

def get_df(path_to_df:str, cache:Dash) -> DataFrame:

    @cache.memoize()
    def cache_df(path_to_df:str) -> DataFrame:

        df = read_csv(path_to_df)

        if df.shape[0] > SAMPLE_SIZE:
            df = df.sample(SAMPLE_SIZE)
        
        return df

    return cache_df(path_to_df)

    
