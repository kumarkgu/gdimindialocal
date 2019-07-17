import pandas as pd
from . import dictops as do


def convertdicttodf(objs, isfill=True, **kwargs):
    if isfill:
        cols = kwargs.get("columns", None)
        dtype = kwargs.get("dtypes", "String")
        dictop = do.DictOps(clist=objs)
        tobjs = dictop.fillarrayofdict(cols=cols, dtype=dtype)
        # tobjs = completedict(objs=objs, cols=cols, isscalar=isscalar)
    else:
        tobjs = objs
    retdf = pd.concat(pd.DataFrame(l) for l in tobjs)
    return retdf


def df_expand(basedf, expandkeys, caxis=1):
    try:
        assert isinstance(expandkeys, list)
        return pd.concat(
            ([basedf.drop([key], axis=caxis),
              basedf[key].apply(pd.Series)] for key in expandkeys),
            axis=caxis
        )
        # return pd.concat(
        #     [basedf.drop(expandkeys, axis=caxis),
        #      basedf[expandkeys].apply(pd.Series)],
        #     axis=1
        # )
    except AssertionError:
        return pd.concat(
            [basedf.drop([expandkeys], axis=caxis),
             basedf[expandkeys].apply(pd.Series)],
            axis=1
        )


def df_dropcolumns(df, **kwargs):
    tempdf = df
    dropcolumn = kwargs.get("dropcolumn", None)
    dedupcols = kwargs.get("dedupcolumns", None)
    caxis = kwargs.get("axis", 1)
    ckeep = kwargs.get("keep", "first")
    if dropcolumn:
        tempdf = df.drop(dropcolumn, axis=caxis)
    try:
        if dedupcols:
            tdf = tempdf.drop_duplicates(subset=dedupcols, keep=ckeep)
        else:
            raise TypeError
    except TypeError or ValueError:
        tdf = tempdf.drop_duplicates(keep=ckeep)
    return tdf


def df_addemptycols(df, addcolumns, dtypes=None):
    exist_cols = list(df.columns)
    for idx, col in enumerate(addcolumns):
        if df[col] not in exist_cols:
            df[col] = None
        if dtypes is not None:
            dtype = dtypes[idx]
            df[col] = df[col].astype(dtype)
    return df



