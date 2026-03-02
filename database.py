import os
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)

def get_conn():
    global conn
    try:
        conn.cursor()
    except (psycopg2.InterfaceError, psycopg2.OperationalError):
        conn = psycopg2.connect(DATABASE_URL)
    return conn

cur = get_conn().cursor()

def fetch_users():
    with get_conn().cursor() as cur:
        cur.execute('SELECT * FROM users;')
        return cur.fetchall()

def fetch_campaigns():
    cur = get_conn().cursor()
    cur.execute("""
            SELECT campaign_id, title,description,goal_amount,start_date,end_date,
            TO_CHAR(created_at, 'Month DD, YYYY')
            FROM campaigns ORDER BY created_at DESC
            """)
    campaigns = cur.fetchall()
    cur.close()
    return campaigns

def fetch_donation():
    cur.execute('select * from donations;')
    donations = cur.fetchall()
    cur.close()
    return donations

def fetch_payments():
    cur.execute('select * from payments;')
    payments = cur.fetchall()
    cur.close()
    return payments

# def fetch_volunteers():
#     cur.execute('select * from volunteers;')
#     volunteers = cur.fetchall()
#     cur.close()
#     return volunteers

def fetch_volunteers():
    with get_conn().cursor() as cur:
        cur.execute('SELECT * FROM volunteers;')
        return cur.fetchall()

def fetch_events():
    cur = get_conn().cursor()
    cur.execute("""
                SELECT event_id,title,description,event_date,location,
                TO_CHAR(created_at, 'Month DD, YYYY')
                FROM events ORDER BY created_at DESC
            """)
    events = cur.fetchall()
    cur.close()
    return events

def fetch_eventreg():
    cur.execute('select * from eventreg;')
    eventreg = cur.fetchall()
    cur.close()
    return eventreg

def fetch_blogs():
    cur = get_conn().cursor()
    cur.execute("""
        SELECT blog_id, user_id, title, content, 
        TO_CHAR(published_at, 'Month DD, YYYY') 
        FROM blogs ORDER BY published_at DESC
    """)
    blogs = cur.fetchall()
    cur.close()
    return blogs



# def fetch_contact():
#     cur.execute('select * from contact;')
#     contact = cur.fetchall()
#     cur.close()
#     return contact

def fetch_contact():
    with get_conn().cursor() as cur:
        cur.execute('SELECT * FROM contact;')
        return cur.fetchall()


# inserting data
def insert_users(values):
    insert = "insert into users(name,email,password,role,status)values(%s,%s,%s,%s,%s)"
    with get_conn().cursor() as cur:
        cur.execute(insert,values)
    conn.commit()
    

# def insert_campaigns(values):
#     insert = "insert into campaigns(title,description,goal_amount,start_date,end_date)values(%s,%s,%s,%s,%s)"
#     cur.execute(insert,values)
#     conn.commit()
#     cur.close()

def insert_campaigns(values):
    with get_conn().cursor() as cur:
        insert = """
            INSERT INTO campaigns (title, description, goal_amount, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(insert, values)
        conn.commit()


   

def insert_donations(values):
    insert = "insert into donations(user_id,campaign_id,amount)values(%s,%s,%s)"
    cur.execute(insert,values)
    conn.commit()
    cur.close()

def insert_payments(values):
    insert = "insert into payments(donation_id,provider,amount)values(%s,%s,%s)"
    cur.execute(insert,values)
    conn.commit()
    cur.close()

def insert_volunteers(values):
    insert = "insert into volunteers(user_id,skills,availability)values(%s,%s,%s)"
    cur.execute(insert,values)
    conn.commit()
    cur.close()

# def insert_events(values):
#     insert = "insert into events(title,description,event_date,location)values(%s,%s,%s,%s)"
#     cur.execute(insert,values)
#     conn.commit()
#     cur.close()

def insert_events(values):
    with get_conn().cursor() as cur:
        insert = """
            INSERT INTO events (title, description, event_date, location)
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(insert, values)
        conn.commit()

def insert_event_registration(values):
    insert = "insert into event_registration(event_id,user_id)values(%s,%s)"
    cur.execute(insert,values)
    conn.commit()
    cur.close()

# def insert_blogs(values):
#     insert = "insert into blogs(user_id,title,content)values(%s,%s,%s)"
#     cur.execute(insert,values)
#     conn.commit()
#     cur.close()

def insert_blogs(values):
    insert = "INSERT INTO blogs (user_id, title, content) VALUES (%s, %s, %s)"

    with get_conn().cursor() as cur:
        cur.execute(insert, values)
        conn.commit()


def insert_contact(values):
    insert = "insert into contact(name,email,message)values(%s,%s,%s)"
    cur.execute(insert,values)
    conn.commit()
    cur.close()

# def check_user(email):
#     query="select * from users where email = %s"
#     cur.execute(query,(email,))
#     user=cur.fetchone()
#     cur.close()
#     return user

def check_user(email):
    query = "select * from users where email = %s"
    with get_conn().cursor() as cur:
        cur.execute(query, (email,))
        user = cur.fetchone()
    return user

