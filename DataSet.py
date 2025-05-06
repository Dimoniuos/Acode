import psycopg2
import os
from dotenv import load_dotenv
import csv
from Partners import Partners


def connect():
    load_dotenv()
    return psycopg2.connect(
        dbname=os.getenv("dataBase_name"),
        user=os.getenv("dataBase_user"),
        password=os.getenv("dataBase_password"),
        host=os.getenv("dataBase_host"),
        port="5432"
    )


class UsersData:
    def create_table(self):
        conn = connect()
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            email TEXT,
            username TEXT, 
            subscription BOOLEAN NOT NULL, 
            partner BOOLEAN NOT NULL);
    ''')
        conn.commit()
        cur.close()
        conn.close()

    def insert_user(self, id, email, username, subscription):
        conn = connect()
        cur = conn.cursor()
        cur.execute('INSERT INTO users (id, email, username, subscription, partner) VALUES (%s, %s, %s, %s, %s);', (id, email, username, subscription, False))
        conn.commit()
        cur.close()
        conn.close()

    def update_user(self, id, subscription):
        conn = connect()
        cur = conn.cursor()
        query = """
            UPDATE users
            SET subscription = %s
            WHERE id = %s;
        """
        cur.execute(query, (subscription, id))
        conn.commit()
        cur.close()
        conn.close()

    def UsersList(self) -> list:
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users;")
        Userslist =  [i[0] for i in cur.fetchall()]
        print(Userslist)
        return Userslist

    def get_table(self):
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users;")
        conn.close()
        with open('Users.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow([desc[0] for desc in cur.description])
            for row in cur:
                writer.writerow(row)

    def get_email(self, id : int):
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT email FROM users WHERE id = %s;", (id,))
        email = cur.fetchone()
        conn.close()
        if email is None:
            return None
        else:
            return email[0]

    def update_email(self, id, email):
        conn = connect()
        cur = conn.cursor()
        cur.execute("UPDATE users SET email = %s WHERE id = %s;", (email, id,))
        conn.commit()
        cur.close()
        conn.close()

    def is_partner(self, id):
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT partner FROM users WHERE id = %s;", (id,))
        partner = cur.fetchone()[0]
        conn.close()
        cur.close()
        return partner

    def update_partner(self, id, partner):
        conn = connect()
        cur = conn.cursor()
        cur.execute("UPDATE users SET partner = %s WHERE id = %s;", (partner, id,))
        conn.commit()
        cur.close()
        conn.close()




class Refferals:
    def create_table(self):
        conn = connect()
        cur = conn.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS Refferals (
            id BIGINT PRIMARY KEY,
            username TEXT, 
            from_id TEXT,
            sale INT NOT NULL);
    ''')
        conn.commit()
        cur.close()
        conn.close()

    def insert_user(self, name, username, from_id, sale):
            conn = connect()
            cur = conn.cursor()
            cur.execute('INSERT INTO Refferals (id, username, from_id, sale) VALUES (%s, %s, %s, %s);',
                        (name, username, from_id, sale))
            conn.commit()
            cur.close()
            conn.close()
    def Exist(self, id) -> bool:
        conn = connect()
        cur = conn.cursor()
        query = f"SELECT EXISTS(SELECT 1 FROM Refferals WHERE id = %s);"
        cur.execute(query, (id,))
        return cur.fetchone()[0]

    def get_sale(self, id):
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT sale FROM Refferals WHERE id = %s;",(id,))
        sale = cur.fetchone()[0]
        cur.close()
        conn.close()
        return sale

    def null_sale(self, id):
        conn = connect()
        cur = conn.cursor()
        cur.execute("UPDATE Refferals SET sale = 0 WHERE id = %s;", (id,))
        conn.commit()
        cur.close()
        conn.close()

    def update_sale(self, ref_id):
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT from_id FROM Refferals WHERE id = %s;", (ref_id,))
        id = cur.fetchone()[0]
        cur.execute("UPDATE Refferals SET from_id = %s WHERE id = %s;", ("0", ref_id,))
        if (id != "0"):
            if "P" in id:
                par = Partners()
                par.update_paid(id)
            else:
                Sale = self.get_sale(id)
                if Sale == 100:
                    Sale = 80
                cur.execute("UPDATE Refferals SET sale = %s + 20 WHERE id = %s;", (Sale, id,))
        conn.commit()
        cur.close()
        conn.close()

    def get_table(self):
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Refferals;")
        with open('Refferals.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow([desc[0] for desc in cur.description])
            for row in cur:
                writer.writerow(row)



class Price:
    def get_price(self):
        conn = connect()
        cur = conn.cursor()
        cur.execute("SELECT value FROM Price WHERE key = 'price';")
        price = cur.fetchone()[0]
        cur.close()
        conn.close()
        return price
    def update_price(self, price):
        conn = connect()
        cur = conn.cursor()
        cur.execute("UPDATE Price SET value = %s WHERE key = 'price';", (price,))
        conn.commit()
        cur.close()
        conn.close()


class AllRefferals:
    def create_table(self):
        conn = connect()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS AllRefferals (id BIGINT PRIMARY KEY, from_id TEXT);")
        conn.commit()
        cur.close()
        conn.close()

    def insert_user(self, id, from_id):
        conn = connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO AllRefferals (id,from_id) VALUES (%s,  %s);",(id, from_id,))
        conn.commit()
        cur.close()
        conn.close()



if __name__ == "__main__":
    AllRefferals = AllRefferals()
    AllRefferals.create_table()
