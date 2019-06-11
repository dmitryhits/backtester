from backtrader.feeds import PandasData

class MyPandasData(PandasData):
    '''
        The ``dataname`` parameter inherited from ``backtraer.feeds -> PandasData`` is the pandas
        DataFrame
        '''

    params = (
        #PandasData.params,
        # Possible values for datetime (must always be present)
        #  None : datetime is the "index" in the Pandas Dataframe
        #  -1 : autodetect position or case-wise equal name
        #  >= 0 : numeric index to the colum in the pandas dataframe
        #  string : column name (as index) in the pandas dataframe
        ('datetime', None),

        # Possible values below:
        #  None : column not present
        #  -1 : autodetect position or case-wise equal name
        #  >= 0 : numeric index to the colum in the pandas dataframe
        #  string : column name (as index) in the pandas dataframe
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
        ('openinterest', -1),
        ('count',- 1),
        ('wap', -1),
    )

    datafields = [
        'datetime', 'open', 'high', 'low', 'close', 'volume', 'openinterest', 'count', 'wap'
    ]
