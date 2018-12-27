from base.basejira import jiraops as jo
from base.utils.Logger import Logger
from base.utils import fileobjects as fo
from base.utils import base_util as bu
from base.dataops import dfopers as do
import pandas as pd
import datetime
import configparser
import os


class JiraOperations:
    def __init__(self, projectname, log=None, **kwargs):
        t_date = datetime.datetime.now().strftime("%Y%m%d")
        self.projectname = projectname
        self.inputfile = kwargs.get("inputfile", None)
        self.basedir = kwargs.get(
            "basedir",
            self._get_def_basedir(projectname=projectname)
        )
        self.templatefile = kwargs.get(
            "templatefile",
            "{0}/{1}_jira_template.xlsx".format(
                self.basedir,
                self.projectname
            )
        )
        self.outputfile = kwargs.get(
            "outputfile",
            "{0}/Data/{1}_data_{2}.xlsx".format(
                self.basedir,
                self.projectname,
                t_date
            )
        )
        self.cfgfile = "{0}/jira_config.cfg".format(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.csvfile = kwargs.get(
            "csvfile",
            "{0}/Data/summary_jira_data_{1}.csv".format(
                self.basedir,
                t_date
            )
        )
        self.log = kwargs.get("log", Logger("TestJIRA").getlog())

    @staticmethod
    def _get_def_basedir(projectname):
        t_base = "C:/Users/{}/Documents".format(bu.current_user())
        t_base = "{0}/JLL/CoE/{1}/Reports".format(t_base,
                                                  projectname)
        return t_base

    @staticmethod
    def _make_base_dir(dirname):
        if os.path.isdir(dirname):
            return
        fo.create_dir(dirname=dirname)

    def copy_template(self):
        fo.copy_file(self.templatefile, self.outputfile)

    def _get_config_item(self):
        cfgkey = "Project {}".format(self.projectname)
        config = configparser.ConfigParser()
        config.read(self.cfgfile)
        try:
            config = config[cfgkey]
            curritem = dict(config.items())
        except configparser.NoSectionError:
            raise configparser.NoSectionError(cfgkey)
        return curritem

    def get_jira_items(self, limit=None, dropcolumn=None, removedupcols=None,
                       *args):
        try:
            cfgkeys = self._get_config_item()
        except configparser.NoSectionError:
            raise
        url = cfgkeys["path"]
        usernm = cfgkeys["username"]
        passwd = cfgkeys["passkey"]
        query = "project={}".format(
            cfgkeys["project"]
        )
        if args:
            for argv in args:
                query += " and {}".format(argv)
        dropkey = 'Worklog'
        with jo.JiraBase(url, log=self.log,
                         username=usernm, passwd=passwd) as _ojira:
            # _ojira.get_issue_details(query)
            issuelist = _ojira.get_all_issues(query, limit=limit)
            if issuelist is None:
                return None
            issuedf = do.convertdicttodf(issuelist, isfill=True,
                                         columns=[dropkey], dtypes="list")
            tdf = do.df_expand(issuedf, expandkeys=dropkey)
            finaldf = do.df_dropcolumns(tdf, keep="first")
        if finaldf is not None:
            tdf = do.df_dropcolumns(finaldf, dropcolumn=dropcolumn,
                                    dedupcolumns=removedupcols,
                                    axis=1, keep="first")
            nonreptdf = self.add_df_columns(tdf)
        else:
            return [None, None]
        return [finaldf, nonreptdf]

    @staticmethod
    def add_df_columns(df):
        pd.options.mode.chained_assignment = None
        df['CreateDate'] = pd.to_datetime(df['IssueCreated']).dt.date
        df['UpdateDate'] = pd.to_datetime(df['IssueUpdated']).dt.date
        df['NumDays'] = datetime.datetime.now().date() - df['UpdateDate']
        df['AverageDays'] = (pd.to_datetime(df['IssueUpdated']).dt.date -
                             pd.to_datetime(df['IssueCreated']).dt.date).dt.days
        return df

    @staticmethod
    def read_excel(infile, shtname=None, dropcolumn=None,
                   removedupcols=None):
        shtname = "Sheet1" if shtname is None else shtname
        df = pd.read_excel(infile, shtname)
        dedupdf = do.df_dropcolumns(df, dropcolumn=dropcolumn,
                                    dedupcolumns=removedupcols,
                                    axis=1, keep="first")
        # dedupdf = self.clean_up_df(df, dropcolumn=dropcolumn,
        #                            removedupcols=removedupcols)
        return [df, dedupdf]

    def write_to_excel(self, excel=None, sheetdf=None):
        from base.dataops import dftoexcel as dte
        output = self.outputfile if excel is None else excel
        excelwrite = dte.DFtoExcel(close=True)
        excelwrite.write_to_excel(filename=output, sheets=sheetdf)
        # excelwrite.write_df_excel(output, sheetdf=sheetdf, replace=True)
        # excelwrite.write_df_to_excel_new(sheetdf=sheetdf, filename=output)

    def write_to_csv(self, csvfile=None, sheetdf=None):
        from base.dataops import dftocsv as dfcs
        csv = self.csvfile if csvfile is None else csvfile
        basecsv = "{}.csv".format("_".join(csv.split("_")[:-1]))
        csvwrite = dfcs.DFToCSV()
        csvwrite.savetocsv(csv, sheetdf)
        csvwrite.savetocsv(basecsv, sheetdf)


def run_jira(limit=None, removecol=None):
    prjname = "Red"
    basedr = "C:/Users/gunjan.kumar/Documents"
    basedr = "{0}/JLL/CoE/{1}/Reports".format(basedr, prjname.upper())
    template = "{}/{}_jira_template.xlsx".format(basedr, prjname.lower())
    _removecol = ['CreateTime', 'Name', 'TimeSpent',
                  'TimeSpentSecond', 'UpdateTime']
    rmvcolumn = _removecol if removecol is None else removecol
    jiraobj = JiraOperations(projectname=prjname, basedir=basedr,
                             templatefile=template)
    retdf = jiraobj.get_jira_items(limit=limit, dropcolumn=rmvcolumn)
    if retdf:
        detaildf = retdf[0]
        summarydf = retdf[1]
        jiraobj.copy_template()
        odict = {
            "Summary": summarydf,
            "Detail": detaildf
        }
        jiraobj.write_to_excel(sheetdf=odict)
        jiraobj.write_to_csv(sheetdf=summarydf)


def test_jira():
    from base.dataops import dftoexcel as dfte
    from base.dataops import dftocsv as dfcs
    prjname = "Red"
    basedr = "C:/Users/gunjan.kumar/Documents"
    basedr = "{0}/JLL/CoE/{1}/Reports".format(basedr, prjname.upper())
    datadir = "{0}/Data".format(basedr)
    inputfile = "{0}/{1}".format(datadir, "Red_data_20181213.xlsx")
    outcsv = "{0}/{1}".format(datadir, "summary_jira_data_1.csv")
    xlsobj = dfte.DFtoExcel()
    retobj = xlsobj.readexcel(inputfile)
    csvobj = dfcs.DFToCSV()
    csvobj.savetocsv(outcsv, retobj["Summary"])


# run_jira(limit=5)
run_jira()
# test_jira()

# def test_jira(isjira=True, infile=None, outfile=None):
#     template = "{0}/red_template.xlsx".format(basedr)
#     output = "{0}/red{1}.xlsx".format(
#         basedr,
#         datetime.datetime.now().strftime("%Y%m%d")
#     )
#     output1 = "{0}/red{1}_output.xlsx".format(
#         basedr,
#         datetime.datetime.now().strftime("%Y%m%d")
#     )
#     if isjira:
#         output = outfile if outfile is None else outfile
#         bothdf = get_jira_items(project="Red", dropcolumn=removecol)
#     else:
#         infile = output if infile is None else infile
#         output = output1 if outfile is None else outfile
#         sheetname = "Sheet1"
#         bothdf = read_excel(infile=infile, shtname=sheetname,
#                             dropcolumn=removecol)
#     jiradf = bothdf[0]
#     dedupdf = bothdf[1]
#     # jiradf = get_jira_items(project="Red", limit=10)
#     if jiradf is None:
#         return
#     write_to_excel(jiradf, output, sheetname="Sheet1", issave=False)
#     write_to_excel(dedupdf, output, sheetname="Sheet2", issave=True)
#     print("Completed")


# test_jira(isjira=False)
# issuedf = pd.concat(pd.DataFrame(l) for l in issuelist)
# newissue = []
# for l in issuelist:
#     if not l['Worklog']:
#         l['Worklog'] = [None]
#     newissue.append(l)
# issuedf = pd.concat(pd.DataFrame(l) for l in newissue)
# _finldf = pd.concat(
#     [issuedf.drop([dropkey], axis=1),
#      issuedf[dropkey].apply(pd.Series)],
#     axis=1
# )
# finaldf = _finldf.drop_duplicates(keep='first')

# @staticmethod
# def clean_up_df(df, dropcolumn=None, removedupcols=None):
#     try:
#         if dropcolumn:
#             tempdf = df.drop(dropcolumn, axis=1)
#         else:
#             raise TypeError
#     except TypeError or ValueError:
#         tempdf = df
#     try:
#         if removedupcols:
#             tdf = tempdf.drop_duplicates(subset=removedupcols, keep='first')
#         else:
#             raise TypeError
#     except TypeError or ValueError:
#         tdf = tempdf.drop_duplicates(keep='first')
#     pd.options.mode.chained_assignment = None
#     tdf['CreateDate'] = pd.to_datetime(tdf['IssueCreated']).dt.date
#     tdf['UpdateDate'] = pd.to_datetime(tdf['IssueUpdated']).dt.date
#     tdf['NumDays'] = datetime.datetime.now().date() - tdf['UpdateDate']
#     tdf['AverageDays'] = (pd.to_datetime(tdf['IssueUpdated']).dt.date -
#                           pd.to_datetime(tdf['IssueCreated']).dt.date).dt.days
#     return tdf
