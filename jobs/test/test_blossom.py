from baselib.database.sqlserver import SQLServer
from baselib.utils.Logger import Logger
import time
import datetime
import pandas

_LOG = Logger("Blossom Process").getlog()


def _get_query():
    query = """
        SELECT
            DISTINCT
            Client_Id,
            Client_Type,
            Client_Name,
            Client_Name_Uni,
            ContactName,
            ClientCategory,
            ContactPhone,
            ContactCity,
            ContactEmail,
            ResultType,
            ClientIndustry
        FROM
            dbo.{0}('{1}', '{2}', '{3}', '{4}', {5})
        ORDER BY
            ResultType,
            Client_Name,
            Client_Name_Uni,
            Client_Type,
            Client_Id,
            ContactName,
            ClientCategory,
            ContactPhone,
            ContactCity,
            ContactEmail
    """
    return query


def execute_blossom(procname, section, username, clientname, optype,
                    nametype, limit=None):
    passphrase = "This is my message"
    # procname = "GK_Tst1_GetClientsForUser"
    query = _get_query().format(
        procname,
        username,
        clientname,
        optype,
        nametype,
        limit
    )
    with SQLServer(log=_LOG) as dbhandler:
        alldata = dbhandler.sql_to_df_timed(
            query=query,
            sectionname=section,
            passphrase=passphrase
        )
    df = alldata[0]
    starttime = alldata[1]
    endtime = alldata[2]
    deltatime = alldata[3]
    print(df.to_string())
    time.sleep(1)
    elapsed = int(deltatime.total_seconds() * 1000)
    _LOG.info("Start Time: {}".format(str(starttime)))
    _LOG.info("End Time: {}".format(str(endtime)))
    _LOG.info("Total Elapsed Time: {} milliseconds".format(str(elapsed)))


def test_blossom_time(procname):
    username = "jerry.majewski"
    # clientname = "Accent"
    clientname = "Black"
    # clientname = "Hew"
    optype = "add"
    nametype = "en"
    limit = 100
    section = "BLOSSOM_DATABASE"
    _LOG.info("*****Executing Function : {}".format(procname))
    execute_blossom(
        procname=procname, section=section, username=username,
        clientname=clientname, optype=optype, nametype=nametype,
        limit=limit
    )
    _LOG.info("*************************************************")
    _LOG.info("\n")
    _LOG.info("\n")


test_blossom_time("GK_Tst1_GetClientsForUser")
test_blossom_time("GK_Test_GetClientsForUser")
test_blossom_time("GetClientsForUser")
