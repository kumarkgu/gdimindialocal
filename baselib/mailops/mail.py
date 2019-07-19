from baselib.mailops.gmail import gmail as gm


class MailInitialize:
    def __init__(self, user=None, password=None, ask_credential=False):
        self._user = user
        self._password = password
        self.ask_credential = ask_credential

    @property
    def user(self):
        if self.ask_credential and self._user is None:
            user_input = input("Username: ?")
            self._user = user_input
        return self._user

    @property
    def password(self):
        if self.ask_credential and self._password is None:
            pwd_input = input("Password: ?")
            self._password = pwd_input
        return self._password


class MyGmail(MailInitialize):
    def __init__(self, user=None, password=None, ask_credential=False):
        super(MyGmail, self).__init__(user, password, ask_credential)
        self.conn = None

    def connect(self):
        if not self.conn:
            try:
                self.conn = gm.login(self.user, self.password)
                return self.conn
            except gm.AuthenticationError:
                raise

    def disconnect(self):
        if self.conn:
            self.conn.logout()
