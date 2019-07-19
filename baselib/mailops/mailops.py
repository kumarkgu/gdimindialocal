from baselib.utils.Logger import Logger
from .mail import MyGmail
from baselib.mailops.gmail import exceptions as ex
from datetime import datetime

log = Logger("GMail Connection").getlog()


class GetMail:
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self._conn = None
        self.mobject = self._set_mobject()

    def _set_mobject(self):
        self._disconnect()
        mail = MyGmail(user=self.user, password=self.password)
        return mail

    def _disconnect(self):
        if self._conn:
            self.mobject.disconnect()

    def _connect_gmail(self):
        if self._conn:
            return
        try:
            self._conn = self.mobject.connect()
        except ex.AuthenticationError as ae:
            log.info(ae)
            raise
        except ex.ConnectionError as ce:
            log.info(ce)
            raise
        except ex.GmailException:
            log.info("Generic Gmail Error")
            raise
        except Exception as e:
            log.info(e)
            raise

    def _reset_user_cred(self, user=None, password=None):
        isreset = False
        if user or password:
            if user.upper() != self.user.upper() or password != self.password:
                self.user = user
                self.password = password
                isreset = True
        if isreset:
            if self._conn:
                self.mobject = self._set_mobject()
                self._connect_gmail()

    def _traverse_mbox(self, mbox=None, sender=None, after=None, unread=True):
        if after:
            maillist = self._conn.mailbox(mbox).mail(
                sender=sender,
                after=datetime.date(after[0], after[1], after[2]),
                unread=unread)
        else:
            maillist = self._conn.mailbox(mbox).mail(
                sender=sender,
                unread=unread
            )
        return maillist

    def connect(self, user=None, password=None):
        self._reset_user_cred(user=user, password=password)

    def disconnect(self):
        self._disconnect()

    def getmails(self, mbox="Inbox", sender=None, user=None, password=None,
                 after=None, ifdisconn=True, unread=True):
        maillist = []
        if user or password:
            self._reset_user_cred(user=user, password=password)
        self._connect_gmail()
        allmails = self._traverse_mbox(mbox=mbox, sender=sender, unread=unread)
        for temail in allmails:
            temail.fetch()
            if not isinstance(temail.body, str):
                mailbody = temail.body.decode('utf-8')
            else:
                mailbody = temail.body
            mailbody = mailbody.strip()
            maillist.append(mailbody)
        if ifdisconn:
            self._disconnect()
        return maillist
