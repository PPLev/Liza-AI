import datetime

import peewee as pw

db = pw.SqliteDatabase('notice.db')

class Base(pw.Model):
    class Meta:
        database = db


class Notice(Base):
    id = pw.IntegerField(primary_key=True)
    value = pw.TextField(null=True)
    create_date = pw.DateTimeField(default=datetime.datetime.now)
    remind_date = pw.DateTimeField(null=True)


    @staticmethod
    def get_next_day_notice():
        notises = Notice.select().were(Notice.create_date.day)

    @staticmethod
    def get_next_week_notice():
        notises = Notice.select().were(Notice.create_date.day)

    @staticmethod
    def new_notice():
        notises = Notice.select().were(Notice.create_date.day)


db.connect()
db.create_tables([Notice])
