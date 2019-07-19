import configparser


class TDIMConfig:
    def __init__(self, configfile):
        self.configfile = configfile

    def get_config(self, sectionname):
        config = configparser.ConfigParser()
        config.read(self.configfile)
        try:
            config = config[sectionname]
            retdict = dict(config.items())
        except configparser.NoSectionError:
            raise configparser.NoSectionError(sectionname)
        return retdict

    def merge_config(self, sectionname, sections, runmethod='new'):
        config = configparser.ConfigParser()
        fileexistflag = 1
        sectionexistflag = 1
        try:
            with open(self.configfile) as cfgfile:
                config.read_file(cfgfile)
        except IOError:
            fileexistflag = 0
            sectionexistflag = 0
        # Now check if section exists
        if fileexistflag == 1:
            try:
                config = config[sectionname]
            except configparser.NoSectionError:
                sectionexistflag = 0
            except KeyError:
                sectionexistflag = 0
            if sectionexistflag == 0:
                for section in config.sections():
                    config.remove_section(section)
        else:
            sectionexistflag = 0
        if runmethod.upper() == 'NEW':
            if sectionexistflag == 1:
                raise configparser.DuplicateSectionError(sectionname)
            else:
                config.add_section(sectionname)
                for key, value in sections.items():
                    config.set(sectionname, key, value)
        elif runmethod.upper() == 'UPDATE':
            if fileexistflag == 0:
                raise IOError
            if sectionexistflag == 0:
                raise configparser.NoSectionError(sectionname)
            else:
                for key, value in sections.items():
                    config.set(sectionname, key, value)
        modeflag = 'w' if fileexistflag == 0 else 'a'
        with open(self.configfile, modeflag) as cfgfile:
            config.write(cfgfile)
