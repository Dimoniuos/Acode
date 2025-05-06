import psycopg2
from dotenv import load_dotenv
import os
import csv



def connect():
    load_dotenv()
    return psycopg2.connect(
        dbname=os.getenv("dataBase_name"),
        user=os.getenv("dataBase_user"),
        password=os.getenv("dataBase_password"),
        host=os.getenv("dataBase_host"),
        port="5432"
    )

class Partners:
    def create(self):
        conn = connect()
        cur = conn.cursor()
        cur.execute('''
                CREATE TABLE IF NOT EXISTS Partners (
                    link TEXT PRIMARY KEY,
                    user_id TEXT,
                    started BIGINT, 
                    paid BIGINT);
            ''')
        conn.commit()
        cur.close()
        conn.close()

    def insert(self, link, user_id):
        conn = connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO Partners (link, user_id, started, paid) VALUES (%s, %s, %s, %s);", (link, user_id, 0, 0))
        conn.commit()
        cur.close()
        conn.close()

    def get_statistics(self, id):
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Partners WHERE user_id = %s;", (id,))
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data

    def get_started(self, link):
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT started FROM Partners WHERE link = %s;", (link,))
        data = cur.fetchone()[0]
        cur.close()
        conn.close()
        return data

    def get_paid(self, link):
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT paid FROM Partners WHERE link = %s;", (link,))
        data = cur.fetchone()[0]
        cur.close()
        conn.close()
        return data

    def update_started(self, link):
        conn = connect()
        cur = conn.cursor()
        started = self.get_started(link) + 1
        cur.execute("UPDATE Partners SET started = %s WHERE link = %s;", (started, link,))
        conn.commit()
        cur.close()
        conn.close()

    def update_paid(self, link):
        conn = connect()
        cur = conn.cursor()
        paid = self.get_paid(link) + 1
        cur.execute("UPDATE Partners SET paid = %s WHERE link = %s;", (paid, link,))
        conn.commit()
        cur.close()
        conn.close()

    def Exist(self, id):
        conn = connect()
        cur = conn.cursor()
        query = f"SELECT EXISTS(SELECT 1 FROM Partners WHERE user_id = %s);"
        cur.execute(query, (id,))
        data = cur.fetchall()[0]
        cur.close()
        conn.close()
        return data

    def get_table(self):
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Partners;")
        with open('Partners.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow([desc[0] for desc in cur.description])
            for row in cur:
                writer.writerow(row)





