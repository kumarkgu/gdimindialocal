import re
from baselib.utils import stringops as stro
from baselib.utils import Logger as lgr


class QueryParser:
    def __init__(self, schemaname, sep=",", lang="SQL", log=None, **kwargs):
        self.viewname = self._get_schemaname(schemaname=schemaname, sep=sep)
        # r"[\s\[]*([^\s\]]*)([\s\]]*|$)", re.IGNORECASE
        self.regex = re.compile(
            r"[\[\s]*(" + self.viewname + r")[\]\s]*\." +
            r"(\[([^\]]+)(\])|([^\s\(\)\[\.]+)([\s\(\)\.]+|$))", re.IGNORECASE
        )
        self.noschregex = re.compile(
            r"[\[\s]*(\S+)[\]\s]*\.\.[\s\[]*([^\s\]]*)([\s\]]*|$)"
        )
        igncomm = r"proc|procedure|function|view|trigger|table|sequence"
        self.ignoreregex = re.compile(
            r"(^|\s+)(create|alter)\s+(" + igncomm + r")(\s+|$)",
            re.IGNORECASE|re.MULTILINE
        )
        self.regobname = re.compile(r"([^\.]+)(\.[^\.]+)", re.IGNORECASE)
        self.commentobj = stro.StripComments(lang=lang)
        self.regsingle = self.commentobj.regsingle
        self.regmulti = self.commentobj.regmulti
        if log is None:
            self.log = lgr.Logger("Query Parser").getlog()
        else:
            self.log = log
        self.k_schema = kwargs.get("k_schema", "Schema Name")
        self.k_object = kwargs.get("k_object", "Object Name")
        self.k_database = kwargs.get("k_database", "Database Name")
        self.preprend = kwargs.get("prepend", "....")

    @staticmethod
    def _get_schemaname(schemaname, sep=","):
        try:
            assert isinstance(schemaname, str)
            schname = re.sub("\s*,\s*", ",", schemaname)
            regstr = "|".join(schemaname.split(sep=sep))
        except AssertionError:
            regstr = "|".join([x.strip() for x in schemaname])
        return regstr

    def append_objectname(self, schemaname, objectname, objlist=None,
                          dbname=None):

        def _ret_dict(sch, ob, db=None, qt=None):
            match = self.regobname.match(ob)
            if match:
                ob = match.group(1)
            if db:
                return dict(
                    {self.k_schema: sch.lower(),
                     self.k_object: ob.lower(),
                     self.k_database: db.lower()
                     }
                )
            else:
                return dict({self.k_schema: sch.lower(),
                             self.k_object: ob.lower()})

        if objlist and len(objlist) > 0:
            match = 0
            for objs in objlist:
                counter = 0
                for key, value in objs.items():
                    if key == self.k_schema and \
                            value.lower() == schemaname.lower():
                        counter += 1
                    if key == self.k_object and \
                            value.lower() == objectname.lower():
                        counter += 1
                if counter == 2:
                    match = 1
                    break
            if match == 0:
                objlist.append(_ret_dict(schemaname, objectname, db=dbname))
        else:
            objlist.append(_ret_dict(schemaname, objectname, db=dbname))
        return objlist

    def clean_query(self, query):
        string = query
        if self.regmulti:
            self.log.info(
                "{}Stripping Multiple Line Comments From String".format(
                    self.preprend
                )
            )
            string = self.commentobj.remove_string(string=string,
                                                   regex=self.regmulti)
        if self.regsingle:
            self.log.info(
                "{}Stripping Single Line Comments From String".format(
                    self.preprend
                )
            )
            string = self.commentobj.remove_string(string=string,
                                                   regex=self.regsingle,
                                                   method="Line")
        return string

    def filter_query(self, query):
        regmatch = self.ignoreregex.search(query)
        if regmatch:
            return None
        else:
            return query

    def get_views(self, query, dbname=None):
        viewdict = []
        self.log.info("{}Getting All Query Data".format(self.preprend))
        for matched in self.regex.finditer(string=query):
            t_schema = matched.group(1)
            t_object = matched.group(3 if matched.group(3) else 5)
            viewdict = self.append_objectname(t_schema, t_object, viewdict,
                                              dbname=dbname)
        for (t_db, t_object, ending) in self.noschregex.findall(string=query):
            viewdict = self.append_objectname("dbo", t_object, viewdict,
                                              dbname=t_db)
        return viewdict

    def main_proc(self, query, dbname=None):
        string = self.clean_query(query=query)
        string = self.filter_query(query=string)
        if string is None:
            return None
        viewlist = self.get_views(query=string, dbname=dbname)
        return viewlist
