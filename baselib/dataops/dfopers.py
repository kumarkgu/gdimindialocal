import pandas as pd
import numpy as np
import datetime
from . import dictops as do
from baselib.utils import stringops as sops


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


def df_fromdict(objs, orient="columns", dtype=None, columns=None):
    """
    This function converts a dictionary passed to a pandas dataframe
    :param objs: dict
        data as dictionary to be converted to dataframe
    :param orient: str, default: 'columns' ('columns', 'index')
        The orientation of data.  If the keys of the passed dict should be the
        columns of the resulting DataFrame, pass 'columns' (default). Otherwise
        if the keys should be rows, pass 'index'.
    :param dtype: dbtype, default: None
        Data type to force. Otherwise infer
    :param columns: list, default: None
        Column labels to use when orient='index'. Raises a ValueError if used
        with orient='columns'.
    :return: Dataframe
    """
    if orient.lower() == "columns" and not columns:
        columns = None
    orient = orient.lower()
    df = pd.DataFrame.from_dict(data=objs, orient=orient, dtype=dtype,
                                columns=columns)
    return df


def _build_colname(data, cols=None):
    collist = cols if cols else []
    counter = len(cols) if cols else 0
    for cntr in range(counter, len(data)):
        collist.append("col{}".format(str(cntr)))
    return collist


def convertlistdf(objs, cols=None):
    hassub = any(isinstance(subl, list) for subl in objs)
    if cols:
        collist = sops.listify_data(cols, islist=True, issplit=True)
    else:
        if hassub:
            collist = _build_colname(objs)
    if len(objs) > len(collist):
        collist = _build_colname(objs, cols=collist)
    t_dict = {}
    for cntr in range(len(objs)):
        t_dict[collist[cntr]] = objs[cntr]
    df = pd.DataFrame(t_dict)


def df_expand(basedf, expandkeys, caxis=1):
    try:
        assert isinstance(expandkeys, list)
        return pd.concat(
            ([basedf.drop([key], axis=caxis),
              basedf[key].apply(pd.Series)] for key in expandkeys),
            axis=caxis
        )
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


def df_addemptycols(df, addcolumns, dtypes=None, default=None):
    exist_cols = list(df.columns)
    for idx, col in enumerate(addcolumns):
        if col not in exist_cols:
            df[col] = default
        if dtypes is not None:
            dtype = dtypes[idx]
            df[col] = df[col].astype(dtype)
    return df


def df_convert_to_df(datalist):
    dflist = []
    for row in datalist:
        tdict = dict(row._asdict())
        # dflist.append(pd.Series(tdict).to_frame())
        _tfrm = pd.Series(tdict).to_frame()
        tframe = _tfrm.transpose()
        dflist.append(tframe)
    return dflist


def df_append(datalist, isitertup=False):
    if isitertup:
        datalist = df_convert_to_df(datalist=datalist)
    df = pd.concat(l for l in datalist)
    return df


def df_append_list(datalist, ignore_index=False):
    try:
        assert isinstance(datalist, list)
    except AssertionError:
        return datalist
    if len(datalist) <= 0:
        return None
    df = datalist[0]
    if len(datalist) < 2:
        return df
    for t_df in datalist[1:]:
        df = df.append(t_df, ignore_index=ignore_index)
    return df


def ddf_difference(df1, df2):
    df1 = df1.replace([None], '', regex=True).replace(np.NaN, '', regex=True)
    df2 = df2.replace([None], '', regex=True).replace(np.NaN, '', regex=True)
    missdf = df1.merge(
        df2, indicator=True, how='left'
    ).query("_merge != 'both'").drop('_merge',axis=1)
    # .loc[lambda x: x['_merge'] != 'both']
    # missdf.drop(['_merge'])
    return missdf


def df_rename(df, cols=None, islower=False, isupper=False):
    if cols:
        try:
            assert isinstance(cols, dict)
        except AssertionError:
            raise Exception("Column Names to rename is not a dict")
        df = df.rename(columns=cols)
        if islower or isupper:
            ctype = "Lower" if islower else "Upper"
            df = df_rename_case(df, ctype=ctype)
    return df


def df_rename_case(df, ctype="Lower"):
    if ctype.lower() == "lower":
        df.columns = [x.lower().strip() for x in df.columns]
    elif ctype.lower() == "upper":
        df.columns = [x.upper().strip() for x in df.columns]
    return df


def df_merge(leftdf, rightdf, how='left', on=None, left_on=None, right_on=None,
             left_index=False, right_index=False, keep_left_index=True,
             no_prints=False, ignore_conflicts=False, suffixes=None, log=None,
             log_pre=None,
             ):
    """
    Merge 2 data frames
    :param leftdf: Dataframe,
        left dataframe as input
    :param rightdf: dataframe,
        left dataframe as input
    :param how: str, default: 'left' (left, right, innner)
    :param on: str, optional,
        column name to merge on from both input DataFrames
    :param left_on: str, optional,
        column name to merge on from the left DataFrame
    :param right_on: str, optional,
        column name to merge on from the right DataFrame
    :param left_index: bool, default: False,
        flag whether to use the index of the left DataFrame (if it exists) in
        merging
    :param right_index: bool, default: False,
        flag whether to use the index of the right DataFrame (if it exists) in
        merging
    :param keep_left_index: bool, default: True,
        flag to control whether to retain the indices of the left DataFrame if
        it exists
    :param no_prints: bool, default: False,
        flag to control not to print any logging lines
    :param ignore_conflicts: bool, default: False,
        flag to control whether to ignore overlapping non-joining columns
        from the left DataFrame (right DataFrame columns will remain)
    :param suffix: list(str), default: None
        In case of left and right dataframe have the same column and do not wish
        to drop column, then send suffix
    :param log: Logger, default: None
        if need logging of the process then sends logger
    :param log_pre: str, default: None
        In case of logging, if needs to prepend
    :return: DataFrame,
        merged using input DataFrames
    """
    log_pre = "" if log_pre is None else log_pre
    if not no_prints and log is not None:
        log.info("{}Merging Dataframes".format(log_pre))
    if on is not None:
        try:
            assert isinstance(on, str)
        except AssertionError:
            assert isinstance(on, list)
    if left_on is not None:
        assert isinstance(left_on, str)
    if right_on is not None:
        assert isinstance(right_on, str)

    if rightdf.empty:
        if log is not None:
            log.info(
                "{}Right dataframe is empty, returning left dataframe".format(
                    log_pre
                )
            )
        return leftdf
    if suffixes is None:
        bad_right_cols = [
            c for c in list(rightdf.columns) if c not in (left_on, right_on, on)
            and c in list(leftdf.columns)
        ]
        if bad_right_cols:
            if ignore_conflicts:
                for bad_right_col in bad_right_cols:
                    del leftdf[bad_right_col]
            else:
                raise Exception(
                    "Conflicting columns for merge: {}".format(bad_right_cols)
                )
        left_index_name = leftdf.index.name
        join_key = on or right_on if on or right_on else None
        right_new = rightdf[rightdf[join_key].notnull()] if join_key else rightdf

        if keep_left_index and left_index_name and (on or left_on or right_on):
            left_new = leftdf.reset_index().merge(
                right_new, on=on, left_on=left_on,
                right_on=right_on,
                left_index=left_index, right_index=right_index, how=how
            )
            left_new.set_index(left_index_name, inplace=True)
            return left_new

        return leftdf.merge(
            right_new, on=on, left_on=left_on, right_on=right_on,
            left_index=left_index, right_index=right_index, how=how
        )
    else:
        return leftdf.merge(rightdf, on=on, left_on=left_on, right_on=right_on,
                            left_index=left_index, right_index=right_index,
                            how=how, suffixes=suffixes
                            )


def df_append_df(df1, df2):
    df = pd.concat([df1, df2]).drop_duplicates().reset_index(drop=True)
    return df


def df_sort(df, by, ascending=True, axis=0, na_position='first'):
    df = df.sort_values(by=by, ascending=ascending, axis=axis,
                        na_position=na_position)
    return df


def df_remove_dupl(df, subset=None, keep='first', resetidx=True, drop=False):
    df = df.drop_duplicates(subset=subset, keep=keep, inplace=False)
    if resetidx:
        return df.reset_index(drop=drop)
    else:
        return df


def df_groupby_transform(df, groupby, transform):
    for oper, column in transform.items():
        n_cols = {"{}_{}".format(x, oper): x for x in column}
        t_cols = ["{}_{}".format(x, oper) for x in column]
        df[t_cols] = df.groupby(groupby)[column].transform(oper)
        df.drop(column, axis=1, inplace=True)
        df.rename(columns=n_cols, inplace=True)
    return df


def df_fillna(df, dtdef='19000101', numdef=0, objdef='.', isreverse=False,
              **kwargs):
    if dtdef is not None:
        t_cols = kwargs.get("datecol", None)
        if t_cols is None:
            t_cols = df.select_dtypes(include=[np.datetime64]).columns
        year = int(dtdef[0:4])
        month = int(dtdef[4:6])
        day = int(dtdef[6:])
        t_date = datetime.datetime(year, month, day)
        # if isreverse:
        df[t_cols] = df[t_cols].replace(
            t_date, value=np.datetime64('NaT')
        ) if isreverse else df[t_cols].fillna(t_date)
        # else:
        #     df[t_cols] = df[t_cols].fillna(t_date)
    if numdef is not None:
        t_cols = kwargs.get("numcol", None)
        if t_cols is None:
            t_cols = df.select_dtypes(include=[np.number]).columns
        df[t_cols] = df[t_cols].replace(
            numdef, value=np.NaN
        ) if isreverse else df[t_cols].fillna(numdef)
    if objdef is not None:
        t_cols = kwargs.get("strcol", None)
        if t_cols is None:
            t_cols = df.select_dtypes(include=[np.object]).columns
        df[t_cols] = df[t_cols].replace(
            objdef, ''
        ) if isreverse else df[t_cols].fillna(objdef)
    return df


def df_filter(df1, df2, keycols=None, onlycols=None, reset_index=False,
              drop=False, rename=None):
    keycols = keycols if keycols else list(df2.columns.values)
    if rename[0] is not None:
        df1 = df1[list(rename[0].keys())].rename(columns=rename[0])
    idx1 = df1.set_index(keycols).index
    if rename[1] is not None:
        df2 = df2[list(rename[1].keys())].rename(columns=rename[1])
    idx2 = df2.set_index(keycols).index
    df = df1[~idx1.isin(idx2)]
    if onlycols:
        df = df[onlycols]
    if reset_index:
        df = df.reset_index(drop=drop)
    return df


def df_to_dict(df, orient='dict'):
    """
    Converts a dataframe to dictionary
    :param df: Dataframe
        Dataframe to convert
    :param orient: str, default: 'dict' ('dict', 'list', 'series', 'split',
                                 'records', 'index'
        Orientation
    :return:
    """
    return df.to_dict(orient=orient)


def df_to_sql(df, sectionname, table, passphrase=None, **kwargs):
    """
    Load the dataframe to the SQL table
    :param df: Daatframe
        dataframe to load
    :param sectionname: String
        Defines the database connectivity details in the
    :param table:
    :param passphrase:
    :param kwargs:
    :return:
    """
    from baselib.database.sqlserver import SQLServer
    log = kwargs.get("log", None)
    with SQLServer(log=log) as sqlobj:
        sqlobj.alchemy_engine(sectionname=sectionname, passphrase=passphrase)
        df.to_sql(name=table, con=sqlobj.engine, **kwargs)
