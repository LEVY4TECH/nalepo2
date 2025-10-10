import os

from flask import Flask,render_template,request,redirect,url_for,session,flash,jsonify

import requests

from requests.auth import HTTPBasicAuth

import base64, datetime

from datetime import datetime

from database import fetch_blogs,fetch_campaigns,fetch_contact,fetch_donation,fetch_eventreg,fetch_events,fetch_payments,fetch_users,fetch_volunteers,insert_volunteers,insert_blogs,insert_campaigns,insert_contact,insert_donations,insert_event_registration,insert_events,insert_payments,insert_users,check_user,conn

from flask_bcrypt import Bcrypt

from functools import wraps

from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('kkjuyuhn') or 'dev-secret'
print("SECRET KEY SET:", bool(app.config['SECRET_KEY']))

# Sandbox credentials from Safaricom Daraja
CONSUMER_KEY = "GvKZ5FuE0pwcFQNQL8Uc9jKjkLy08UHG4AqnAP5of46zGGVD"
CONSUMER_SECRET = "brKiCJnuX1AiAeE5AV56ZXuyAZnypeGYeFAv7SvRn4KIFUEl0NfWETtuyaKXipbd"

# Use your Paybill (shortcode) & passkey from Safaricom
BUSINESS_SHORTCODE = "222111"  # test shortcode for sandbox
PASSKEY = "BCxI7C2O1UMPZY2SjxfU1PyByRjOk7PU9Fetig7AM42T/DW2/48cDr2AwSMmQB8kFh1wwFbQOXweAEnlOkgCJMG5yKJ3qzIyBSFmMROoOT8bjwgKwjDe3BqKhTaxxZQjie1uO00elV1E5cRffAUTzqfmKvPYN6RfoO4D6/hzxo/K67otwL/uwEVTEllu0XQgX/osZK5qPvweoiM+TaQ9FQIFSSN5wrQo9Chw0F8++rPigHGAXANFPMzeIAdO+bjZ5DPzcra0U378ppGLzAIcpcLlnEl7tyGQjIEQsmwRr6Th2blGEzPETfsEl7wh6lK/++ZXGwT0e1LMGQuvqTGp+g=="


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'levy4star@gmail.com'
app.config['MAIL_PASSWORD'] = 'znve iqmn dtln arto'

mail = Mail(app)

bcrypt = Bcrypt(app)

def init_db():
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS blogs (
            blog_id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()

init_db()

def get_access_token():
    url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json()['access_token']

def stk_push(phone, amount):
    access_token = get_access_token()
    url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((BUSINESS_SHORTCODE + PASSKEY + timestamp).encode()).decode('utf-8')

    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {
        "BusinessShortCode": BUSINESS_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": BUSINESS_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": "https://abc123.ngrok.io/callback",
        "AccountReference": "CharityDonation",
        "TransactionDesc": "Donation"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

@app.route("/callback", methods=["POST"])
def callback():
    data = request.get_json()
    print("M-Pesa Callback:", data)
    # TODO: save donation status in DB
    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})

# # --- GET ACCESS TOKEN ---
# def get_access_token():
#     url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  
#     # ↑ Use sandbox for testing, change to api.safaricom.co.ke when live

#     print("🔑 Requesting Access Token...")
#     response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))

#     print("🔎 Response Status Code:", response.status_code)
#     print("🔎 Raw Response:", response.text)

#     try:
#         data = response.json()
#         access_token = data.get("access_token")
#         if not access_token:
#             raise Exception("No access_token in response")
#         print("✅ Access Token Retrieved:", access_token)
#         return access_token
#     except Exception as e:
#         print("❌ Error parsing access token:", e)
#         raise

# # --- STK PUSH ---
# def stk_push(phone, amount):
#     access_token = get_access_token()
#     url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  

#     timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
#     password = base64.b64encode((BUSINESS_SHORTCODE + PASSKEY + timestamp).encode()).decode('utf-8')

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "BusinessShortCode": BUSINESS_SHORTCODE,
#         "Password": password,
#         "Timestamp": timestamp,
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": amount,
#         "PartyA": phone,  # phone number to be charged
#         "PartyB": BUSINESS_SHORTCODE,
#         "PhoneNumber": phone,
#         "CallBackURL": "https://your-ngrok-url/callback",  # replace with real URL
#         "AccountReference": "CharityDonation",
#         "TransactionDesc": "Donation"
#     }

#     print("📤 Sending STK Push Payload:", payload)

#     response = requests.post(url, json=payload, headers=headers)

#     print("🔎 STK Push Status Code:", response.status_code)
#     print("🔎 STK Push Response:", response.text)

#     try:
#         return response.json()
#     except Exception as e:
#         print("❌ Error parsing STK Push response:", e)
#         raise


@app.route('/')
def home():
    cur = conn.cursor()

    # Fetch 3 latest blogs
    cur.execute("""
        SELECT blog_id, title, content, TO_CHAR(published_at, 'Month DD, YYYY') 
        FROM blogs ORDER BY published_at DESC LIMIT 3
    """)
    recent_blogs = cur.fetchall()

    # Fetch 3 upcoming or latest events
    cur.execute("""
        SELECT event_id, title, description, TO_CHAR(created_at, 'Month DD, YYYY') 
        FROM events ORDER BY event_date DESC LIMIT 3
    """)
    recent_events = cur.fetchall()

    # Fetch 3 latest campaigns
    cur.execute("""
        SELECT campaign_id, title, description, TO_CHAR(created_at, 'Month DD, YYYY') 
        FROM campaigns ORDER BY created_at DESC LIMIT 3
    """)
    recent_campaigns = cur.fetchall()

    cur.close()

    return render_template(
        'index.html',
        # blogs=recent_blogs,
        events=recent_events,
        campaigns=recent_campaigns
    )



@app.route('/users')
def users():
    users = fetch_users()
    return render_template('members.html',users = users)



@app.route('/campaigns')
def campaigns():
    campaigns = fetch_campaigns()
    return render_template('campaigns.html',campaigns = campaigns)

@app.route('/add_campaigns', methods = ['GET','POST'])
def add_campaigns():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['desc']
        goal_amount = request.form['goal']
        start_date = request.form['start']
        end_date = request.form['end']
        new_campaign = (title,description,goal_amount,start_date,end_date)
        insert_campaigns(new_campaign)
        flash("Campaign added Successfully","success")
        return redirect(url_for('campaigns'))
    
    return render_template('addcampaign.html')




@app.route('/donations')
def donations():
    donations = fetch_donation()
    return render_template('donations.html',donations = donations)

@app.route('/new_donation', methods = ['GET','POST'])
def new_donations():
    if request.method == 'POST':
        user_id = request.form['uid']
        campaign_id = request.form['cid']
        amount = request.form['amount']
        news_donation = (user_id,campaign_id,amount)
        insert_donations(news_donation)
        flash("Donation Submitted Succesfully","success")
        return redirect(url_for('donations'))


@app.route('/payments')
def payments():
    payments = fetch_payments()
    donations = fetch_donation()
    return render_template('payments.html',payments = payments, donations = donations)

@app.route('/make_payments', methods = ['GET','POST'])
def make_payments():
    if request.method == 'POST':
        donation_id = request.form['did']
        provider = request.form['pname']
        amount = request.form['amount']
        new_payments = (donation_id,provider,amount)
        insert_payments(new_payments)
        flash("Payment made successfully","success")
        return redirect(url_for('payments'))

@app.route('/volunteers')
def volunteers():
    volunteers = fetch_volunteers()
    users = fetch_users()
    return render_template('volunteers.html',volunteers = volunteers, users = users)

@app.route('/add_volunteer', methods = ['GET','POST'])
def add_volunteer():
    if request.method == 'POST':
        user_id = request.form['uid']
        skills = request.form['skills']
        availability = request.form['avail']
        new_volunteer = (user_id,skills,availability)
        insert_volunteers(new_volunteer)
        flash("Volunteer added successfully","success")
        return redirect(url_for('volunteers'))

@app.route('/events')
def events():
    events = fetch_events()
    return render_template('events.html',events = events)

@app.route('/add_event', methods = ['GET','POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['desc']
        event_date = request.form['edate']
        location = request.form['location']
        new_event = (title,description,event_date,location)
        insert_events(new_event)
        flash("Event added successfully","success")
        return redirect(url_for('events'))
    
    return render_template('addevent.html')

# @app.route('/event_registration')
# def event_registration():
#     event_registration = fetch_eventreg()
#     events = fetch_events()
#     users = fetch_users()
#     return render_template('event_registration.html',event_registration = event_registration, events = events, users = users)

@app.route('/blogs')
def blogs():
    blogs = fetch_blogs()
    return render_template('blogs.html',blogs = blogs)

@app.route('/add_blog', methods = ['GET','POST'])
def add_blog():
    if request.method == 'POST':
        user_id = session.get('uid')
        title = request.form['title']
        content = request.form['content']
        new_blog = (user_id,title,content)
        insert_blogs(new_blog)
        flash("Blog added successfully","success")
        return redirect(url_for('blogs')) 
    return render_template('addblog.html')

@app.route('/contact')
def contact():
    contact = fetch_contact()
    return render_template('contact.html',contact = contact)


# conatct us route
@app.route('/give_feedback', methods=['GET', 'POST'])
def give_feedback():
    if request.method =='POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        new_feedback = (name,email,message)
        insert_contact(new_feedback)
        flash("Feedback submitted successfully","success")
        return redirect(url_for('contact'))
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        role = request.form['role']

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = check_user(email)

        if not user:
            # Check if there's already an approved admin
            if role == 'admin' and not admin_exists():
                status = 'approved'  # first admin is auto-approved 
            else:
                status = 'pending'

            new_user = (name, email, hashed_password, role, status)
            insert_users(new_user)

            if role == 'admin' and status == 'pending':
                flash("Admin account created. Pending approval by system administrator.", "info")
            else:
                flash("User registered successfully. Login!", "success")

            return redirect(url_for('login'))

        else:
            flash("User already exists. Please login.", "warning")
            return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']

        user = check_user(email)

        if not user:
            flash("Please register first", "error")
            return redirect(url_for('register'))
        else:
            if bcrypt.check_password_hash(user[3], password):
                role = user[4]
                status = user[5]  # Make sure check_user returns status as index 5

                # Prevent unapproved admins
                if role == 'admin' and status != 'approved':
                    flash("Admin account pending approval by system administrator.", "warning")
                    return redirect(url_for('login'))

                # Allow login
                session['user_id'] = user[0]
                session['email'] = user[2]
                session['role'] = role
                flash("Logged in successfully", "success")
                return redirect(url_for('home'))
            else:
                flash("Wrong password. Try again", "error")
                return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    session.clear()  # 🧹 removes ALL session data: email, role, user_id, etc.
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))


@app.route('/animation')
def animation():
    return render_template('animation.html')

# details route
@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    cur = conn.cursor()
    cur.execute("SELECT title, content, published_at FROM blogs WHERE blog_id = %s", (blog_id,))
    blog = cur.fetchone()
    cur.close()
    return render_template('blog_detail.html', blog=blog)

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    cur = conn.cursor()
    cur.execute("SELECT title, description, event_date, location, created_at FROM events WHERE event_id = %s", (event_id,))
    event = cur.fetchone()
    cur.close()
    return render_template('event_detail.html', event = event)

@app.route('/campaign/<int:campaign_id>')
def campaign_detail(campaign_id):
    cur = conn.cursor()
    cur.execute("SELECT title, description, goal_amount, start_date, end_date, created_at FROM campaigns WHERE campaign_id = %s", (campaign_id,))
    campaign = cur.fetchone()
    cur.close()
    return render_template('campaign_detail.html', campaign = campaign)

# delete routes

@app.route('/delete_blog/<int:blog_id>')
def delete_blog(blog_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM blogs WHERE blog_id = %s", (blog_id,))
    conn.commit()
    cur.close()
    flash("Blog deleted successfully", "warning")
    return redirect(url_for('blogs'))

@app.route('/delete_event/<int:event_id>')
def delete_event(event_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM events WHERE event_id = %s", (event_id,))
    conn.commit()
    cur.close()
    flash("Event deleted succesfully", "warning")
    return redirect(url_for('events'))

@app.route('/delete_campaign/<int:campaign_id>')
def delete_campaign(campaign_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM campaigns WHERE campaign_id = %s", (campaign_id,))
    conn.commit()
    cur.close()
    flash("Campaign deleted successfully", "warning")
    return redirect(url_for('campaigns'))


@app.route('/edit_blog_title/<int:blog_id>', methods=['GET', 'POST'])
def edit_blog_title(blog_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('blogs'))
    ...

@app.route('/edit_event_title/<int:event_id>', methods=['GET', 'POST'])
def edit_event_title(event_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('events'))
    ...

@app.route('/edit_campaign_title/<int:campaign_id>', methods=['GET', 'POST'])
def edit_campaign_title(campaign_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('campaigns'))
    ...


@app.route('/edit_blog/<int:blog_id>', methods=['GET', 'POST'])
def edit_blog(blog_id):
    cur = conn.cursor()

    if request.method == 'POST':
        new_title = request.form['title']
        new_content = request.form['content']
        cur.execute("UPDATE blogs SET title=%s, content=%s WHERE blog_id=%s",
                    (new_title, new_content, blog_id))
        conn.commit()
        cur.close()
        flash("Blog updated successfully", "success")
        return redirect(url_for('blogs'))
    
     # GET - Load blog data into form
    cur.execute("SELECT title, content FROM blogs WHERE blog_id=%s", (blog_id,))
    blog = cur.fetchone()
    cur.close()
    return render_template('edit_blog.html', blog=blog, blog_id=blog_id)
    
@app.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['desc']
        event_date = request.form['edate']
        location = request.form['location']
        cur.execute("UPDATE events SET title=%s, description=%s, event_date=%s, location=%s WHERE event_id=%s",
                    (title, description, event_date, location, event_id))
        conn.commit()
        cur.close()
        flash("Event updated successfully", "success")
        return redirect(url_for('events'))
    
    cur.execute("SELECT title, description, event_date, location FROM events WHERE event_id=%s", (event_id,))
    event = cur.fetchone()
    cur.close()
    return render_template('edit_event.html', event = event, event_id = event_id)

@app.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['desc']
        goal_amount = request.form['goal']
        start_date = request.form['start']
        end_date = request.form['end']
        cur.execute("UPDATE campaigns SET title=%s, description=%s, goal_amount=%s, start_date=%s, end_date=%s WHERE campaign_id=%s",
                    (title, description, campaign_id, goal_amount, start_date, end_date))
        conn.commit()
        cur.close()
        flash("Campaign updated successfully", "success")
        return redirect(url_for('campaigns'))
    
    cur.execute("SELECT title, description, goal_amount, start_date, end_date FROM campaigns WHERE campaign_id=%s", (campaign_id,))
    campaign = cur.fetchone()
    cur.close()
    return render_template('edit_campaign.html', campaign = campaign, campaign_id = campaign_id)


   

# route for manage users

@app.route('/manage_users')
def manage_users():
    if session.get('role') != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('home'))

    cur = conn.cursor()
    # Only show pending ADMIN users
    cur.execute("SELECT user_id, name, email, role FROM users WHERE status = 'pending' AND role = 'admin'")
    users = cur.fetchall()
    cur.close()
    return render_template('manage_users.html', users=users)




# route to approve admin

@app.route('/approve_user/<int:user_id>')
def approve_user(user_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('home'))

    cur = conn.cursor()
    cur.execute("UPDATE users SET status = 'approved' WHERE user_id = %s RETURNING email, name", (user_id,))
    user = cur.fetchone()
    conn.commit()
    cur.close()

    if user:
        # Send email
        msg = Message("Your Admin Account has been Approved",
                      sender='your_email@gmail.com',
                      recipients=[user[0]])
        msg.body = f"Hello {user[1]},\n\nYour admin account has been approved. You can now log in and access the admin panel.\n\nRegards,\nNalepo Team"
        mail.send(msg)

    flash("Admin approved and notified via email.", "success")
    return redirect(url_for('manage_users'))

# rejecting user route

@app.route('/reject_user/<int:user_id>')
def reject_user(user_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('home'))

    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id = %s RETURNING email, name", (user_id,))
    user = cur.fetchone()
    conn.commit()
    cur.close()

    if user:
        msg = Message("Admin Registration Rejected",
                      sender='your_email@gmail.com',
                      recipients=[user[0]])
        msg.body = f"Hello {user[1]},\n\nUnfortunately, your admin account request has been rejected.\nIf this is a mistake, contact the Nalepo admin team.\n\nRegards,\nNalepo Team"
        mail.send(msg)

    flash("Admin rejected and removed from system.", "info")
    return redirect(url_for('manage_users'))



# Auto - approving the first admin if no one exists!
def admin_exists():
    cur = conn.cursor() 
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND status = 'approved'")
    count = cur.fetchone()[0]
    cur.close()
    return count > 0

# DONATE PAGE

# @app.route('/donate')
# def donate():
#     return render_template('donate.html')

@app.route("/donate", methods=["GET", "POST"])
def donate():
    if request.method == "POST":
        phone = request.form["phone"]
        amount = request.form["amount"]

        result = stk_push(phone, amount)

        if result.get("ResponseCode") == "0":
            flash("Payment request sent to your phone. Please complete it.", "success")
        else:
            flash("Payment request failed. Try again.", "danger")

        return redirect(url_for("donate"))

    return render_template("donate.html")


# @app.route('/donate/mpesa', methods=['POST'])
# def donate_mpesa():
#     fullname = request.form['fullname']
#     phone = request.form['phone']
#     amount = request.form['amount']

#     # ✅ Optional: save to database here
#     # ✅ Optional: call M-Pesa STK push here (via Safaricom Daraja API)

#     # Just for now, let’s confirm it worked
#     print(f"Name: {fullname}, Phone: {phone}, Amount: {amount}")

#     flash("Thank you for your donation! We’ll process it shortly. 🙏")
#     return redirect('/donate')


# # Initiate Mpesa Express Request
# @app.route('/pay')
# def mpesaExpress():
#     amount = request.args.get('amount')
#     phone = request.args.get('phone')

#     endpoint = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
#     acces_token = getAccesstoken()
#     headers = {"Authorization": "Bearer %s" % acces_token }
#     timestamp = datetime.now()
#     times = Timestamp.strftime("%Y%m%d%H%M%S")




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


# app.run(debug=True)


    






    
