from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from celery.utils.log import get_task_logger
import MySQLdb
import MySQLdb.cursors
from pymongo import MongoClient

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'converter.settings')
app = Celery('converter')
app.config_from_object('django.conf:settings')
app.conf.update(
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
logger = get_task_logger(__name__)


@app.task(bind=True)
def convert_to_mongo(self, data):
    logger.info("Start converting...")
    db = MySQLdb.connect(
        host=data['from']['host'],
        user=data['from']['user'],
        passwd=data['from']['password'],
        db=data['from']['db'],
        cursorclass=MySQLdb.cursors.SSDictCursor
    )

    uri = 'mongodb://'
    if data['to']['user'] != '' and data['to']['password'] != '':  # !!!
        uri += data['to']['user'] + ':' + data['to']['password'] + '@'
    uri += data['to']['host'] + '/' + data['to']['db']

    client = MongoClient(uri)
    mongo_db = client[data['to']['db']]

    cur = db.cursor()

    current_num = [0]

    for t in data['tables']:
        if not t['isEmbedded']:
            convert(self, data['tables'], t, cur, mongo_db, current_num)
            current_num[0] += 1


def convert(self, tables, current_table, cursor, mongo_db, current_num):
    cursor.execute('SELECT COUNT(*) as cnt FROM ' + current_table['name'])
    quantity = cursor.fetchone()
    quantity = quantity['cnt']
    cursor.fetchall()  # free result
    MAX_CHUNK = 10000
    num_done = 0
    for i in range(quantity / MAX_CHUNK + 1):
        cursor.execute(
            'SELECT * FROM ' + current_table['name'] + ' LIMIT ' + str(MAX_CHUNK * i) + ', ' + str(MAX_CHUNK)
        )
        if not current_table['isEmbedded']:
            collection = mongo_db[current_table['name']]
            for row in cursor.fetchall():
                inserted_id = collection.insert_one(row).inserted_id
                # print inserted_id
                num_done += 1
                self.update_state(state='PROGRESS',
                                  meta={'current_table': current_table['name'],
                                        'current': num_done,
                                        'total': quantity,
                                        'tables_num': len(tables),
                                        'current_num': current_num[0]})
                # celery_inspect = celery.current_app.control.inspect()
                # revoked = celery_inspect.revoked()
                # try:
                #     if self.request.id in revoked[self.request.hostname]:
                #         self.update_state(state='REVOKED')
                #         exit()
                # except KeyError:
                #     pass
        else:
            for row in cursor.fetchall():
                mongo_db[current_table['embeddedIn']].find_one_and_update(
                    {current_table['parentKey']: row[current_table['selfKey']]},
                    {
                        '$push': {current_table['name']: row}
                    }
                )
                num_done += 1
                self.update_state(state='PROGRESS',
                                  meta={'current_table': current_table['name'],
                                        'current': num_done,
                                        'total': quantity,
                                        'tables_num': len(tables),
                                        'current_num': current_num[0]})
                # celery_inspect = celery.current_app.control.inspect()
                # revoked = celery_inspect.revoked()
                # try:
                #     if self.request.id in revoked[self.request.hostname]:
                #         self.update_state(state='REVOKED')
                #         exit()
                # except KeyError:
                #     pass

    embed = (t for t in tables if t['isEmbedded'] and t['embeddedIn'] == current_table['name'])

    for t in embed:
        current_num[0] += 1
        convert(self, tables, t, cursor, mongo_db, current_num)


def create_user_mongo(db_data, usr_data):
    uri = 'mongodb://'
    if db_data['user'] != '' and db_data['pass'] != '':  # !!!
        uri += db_data['user'] + ':' + db_data['pass'] + '@'
    uri += db_data['host'] + '/' + db_data['name']

    client = MongoClient(uri)
    mongo_db = client[db_data['name']]
    mongo_db.add_user(usr_data['user_name'], usr_data['pwd'], usr_data['read_only'])
