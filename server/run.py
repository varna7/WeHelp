from flask import Flask, render_template,request,session,redirect,url_for
from flaskext.mysql import MySQL
import os
from werkzeug.utils import secure_filename

import datetime
app=Flask (__name__)

app.secret_key='56tf645fg6f676hg66'

mysql = MySQL()
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']='root'
app.config['MYSQL_DATABASE_DB']='wehelp'
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['path']="D:/wehelp/server/static/uploads/"
mysql.init_app(app)

ALLOWED_EXTENSIONS = {'png','jpg','jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# UPLOAD_FOLDER = 'server/static/uploads/'

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# def allowed_file(filename):
#     return '.' in filename and \
#         filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html',message=request.args.get('message'),)


@app.route('/test')
def test():
    return redirect(url_for('index',message="Hi"))



@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        conn = mysql.connect()
        curser = conn.cursor()
        query ="select * from login where username=%s and password=%s"
        curser.execute(query, (request.form['username'],request.form['password']))
        conn.commit()
        account = curser.fetchone()
        if account:
            print(account)
            session['loggedin'] = True
            session['id'] = account[0]
            session['user_id']=account[4]
            session['username'] = account[1]
            if account[3] == 'admin':
                return redirect(url_for('admin_home'))
            elif account[3] == 'user':
                return redirect(url_for('user_home'))
            elif account[3] == 'donar':
                print(account[3])
                return redirect(url_for('donar_home'))
            elif account[3] == 'volunteer':
                print(account[3])
                return redirect(url_for('volunteer_home'))    
            else:
                return 'Please Register' 
        else:
            msg = "Incorrect Username or Password"
            return render_template("login.html",msg=msg)




@app.route('/logout', methods =['GET'])
def logout():
    if session['loggedin']:
        session['loggedin'] = False
        session.pop('id',None)
        session.pop('username',None)
        return redirect(url_for('login'))
    else:
        print("login first")
            

@app.route('/user_registration',methods=['GET','POST'])
def user_registration():
    if request.method=='GET':  
        if request.args.get('head') is not None:
            head = request.args.get('head')
        else:
            head = 'Warning'

        if request.args.get('message') is not None:
            message = request.args.get('message')
        else:
            message = 'Fill Carefully'
        return render_template('user_registration.html',heading=head,message=message)
    if request.method=='POST':
        data=request.form
        conn=mysql.connect()
        cursor=conn.cursor()
        query="insert into registration(f_name,l_name,adrs,phone,dob,b_grp,type) values(%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query,(data['f_name'],data['l_name'],data['adrs'],data['phone'],data['dob'],data['b_grp'],'user'))
        conn.commit()
        query="insert into login(username,password,type,user_id) values (%s,%s,%s,%s)"
        cursor.execute(query,(data['username'],data['password'],'user',cursor.lastrowid))
        conn.commit()
        conn.close()
        return redirect(url_for('user_registration',head="Successfull", message="Registered successfully"))

@app.route('/donar_registration',methods=['GET','POST'])
def donar_registration():
    if request.method=='GET':  
        if request.args.get('head') is not None:
            head = request.args.get('head')
        else:
            head = 'Warning'

        if request.args.get('message') is not None:
            message = request.args.get('message')
        else:
            message = 'Fill Carefully'
        return render_template('donar_registration.html',heading=head,message=message)
    if request.method=='POST':
        data=request.form
        conn=mysql.connect()
        cursor=conn.cursor()
       
        query="insert into registration(f_name,l_name,adrs,phone,dob,b_grp,type) values(%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query,(data['f_name'],data['l_name'],data['adrs'],data['phone'],data['dob'],data['b_grp'],'donar'))
        conn.commit()
        query="insert into login(username,password,type,user_id) values (%s,%s,%s,%s)"
        cursor.execute(query,(data['username'],data['password'],'donar',cursor.lastrowid))
        conn.commit()
        conn.close()
        return redirect(url_for('donar_registration',head="Successfull", message="Registered successfully"))

@app.route('/admin_view_doctors',methods=['GET','POST'])
def admin_view_doctors():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()        
        query = "SELECT * FROM doctors;"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('admin_view_doctors.html',result=data)
    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete from doctors where id=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn = mysql.connect()
        cursor = conn.cursor()
        query="select * from doctors"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('admin_view_doctors.html',result=data)

@app.route('/product_registration',methods=['GET','POST'])
def product_registration():
    if request.method == 'GET':
        if request.args.get('head') is not None:
            head = request.args.get('head')
        else:
            head = ' '

        if request.args.get('message') is not None:
            message = request.args.get('message')
        else:
            message = ' '
        return render_template('donar_add_donations.html',heading=head,message=message)
    if request.method == 'POST':
        # try:
        data = request.form

        # file = request.files['image']
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
         
        img = request.files['file']
        filename = secure_filename(img.filename)
        print(os.path.join(app.config['path'] +  filename))
        img.save(os.path.join(app.config['path'] +filename))

        conn= mysql.connect()
        cursor = conn.cursor()
        s = session['id']
        d1=data['desc']
        query = "INSERT INTO pro_registration(`pname`,`image`,`desc`,`user_id`) values(%s,%s,%s,%s)"
        cursor.execute(query,(data['pname'],filename,d1,s))
        conn.commit()
        conn.close()
        return redirect(url_for('product_registration',head="Successfull", message="donated successfully"))





@app.route('/admin_home')
def admin_home():
    return render_template('admin_home.html')


@app.route('/donar_home')
def donar_home():
    return render_template('donar_home.html')

@app.route('/user_home')
def user_home():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "select * from pro_registration"
        cursor.execute(query)
        data = cursor.fetchall()
        print(len(data))
        conn.close()
        return render_template('user_home.html')


@app.route('/volunteer_home')
def volunteer_home():
    return render_template('volunteer_home.html')

@app.route('/admin_view_user',methods=['GET','POST'])
def admin_view_user():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "select * from registration where type='user'"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('admin_view_user.html',result=data)
    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete from login where user_id=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete from donation_request_map where userId=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete from notification_for_user where userId=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete from registration where id=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn=mysql.connect()
        cursor= conn.cursor()
        query="select * from registration where type='user'"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('admin_view_user.html',result=data)

@app.route('/admin_view_donar',methods=['GET','POST'])
def admin_view_donar():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "select * from registration where type='donar'"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('admin_view_donar.html',result=data)
    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete from login where user_id=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete d from donation_request_map d left join pro_registration p ON p.id = d.donationId where p.user_id=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete from notification_for_user where userId=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete from pro_registration where user_id=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete from registration where id=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn=mysql.connect()
        cursor= conn.cursor()
        query="select * from registration where type='donar'"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('admin_view_donar.html',result=data)

@app.route('/admin_view_volunteer',methods=['GET','POST'])
def admin_view_volunteer():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "select * from registration where type='volunteer'"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('admin_view_volunteer.html',result=data)
    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete from login where user_id=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete from registration where id=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn=mysql.connect()
        cursor= conn.cursor()
        query="select * from registration where type='volunteer'"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('admin_view_volunteer.html',result=data)

@app.route('/admin_view_donations',methods=['GET','POST'])
def admin_view_donations():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "select * from pro_registration"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('admin_view_donations.html',result=data)
    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete from donation_request_map where donationId=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "delete from pro_registration where id=%s"
        cursor.execute(query, request.form.get('delete_by_id'))
        conn.commit()
        conn.close()
        conn=mysql.connect()
        cursor= conn.cursor()
        query="select * from pro_registration"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('admin_view_donations.html',result=data)

@app.route('/admin_add_notification',methods=['GET','POST'])
def admin_add_notification():
    if request.method=='GET':  
        return render_template('admin_add_notification.html')
    if request.method=='POST':
        data=request.form
        today = datetime.datetime.now()
        conn=mysql.connect()
        cursor=conn.cursor()
        query="insert into notification(notification,date,type) values(%s,%s,%s)"
        cursor.execute(query,(data['notification'],today.strftime("%x"),'public'))
        conn.commit()
        conn.close()
        return render_template('admin_home.html')


@app.route('/admin_add_doctors',methods=['GET','POST'])
def admin_add_doctors():
    if request.method=='GET':  
        if request.args.get('head') is not None:
            head = request.args.get('head')
        else:
            head = 'Warning'

        if request.args.get('message') is not None:
            message = request.args.get('message')
        else:
            message = 'Fill Carefully'
        return render_template('admin_add_doctors.html',heading=head,message=message)
    if request.method=='POST':
        data=request.form
        conn=mysql.connect()
        cursor=conn.cursor()
        query="insert into doctors(dname,spl,phone,email,hname) values(%s,%s,%s,%s,%s)"
        cursor.execute(query,(data['dname'],data['spl'],data['phone'],data['email'],data['hname']))
        conn.commit()
        conn.close()
        return render_template('admin_add_doctors.html',heading='Successfull',message='Registered successfully')


@app.route('/user_add_request',methods=['GET','POST'])
def user_add_request():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()

        query = "select donationId from donation_request_map where userId=%s"
        cursor.execute(query,session['user_id'])
        alread_requested = cursor.fetchall()
        ot = []
        for item in alread_requested:
            ot.append(item[0])
        print(str(tuple(ot)))
        if len(ot)==0: # Run now ! 
            query = "select * from pro_registration"
            cursor.execute(query)
            data = cursor.fetchall()
            conn.close()
            print(len(data))
            return render_template('user_add_request.html',result=data)
        elif len(ot)==1: # Run now ! 
            query = "select * from pro_registration where id not in ("+str(ot[0])+")"
            cursor.execute(query)
            data = cursor.fetchall()
            conn.close()
            print(len(data))
            return render_template('user_add_request.html',result=data)
        else:
            query = "select * from pro_registration where id NOT IN "+str(tuple(ot))
            cursor.execute(query)
            data = cursor.fetchall()
            conn.close()
            print(len(data))
            return render_template('user_add_request.html',result=data)



@app.route('/already_requested',methods=['GET'])
def already_requested():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "select donationId from donation_request_map where userId=%s"
        cursor.execute(query,session['user_id'])
        alread_requested = cursor.fetchall()
        ot = []
        for item in alread_requested:
            ot.append(item[0])
        print(str(tuple(ot)))
        if len(ot) == 0:
            return render_template('empty_list.html')        
        elif len(ot)==1: # Run now ! 
            query = "select * from pro_registration p, donation_request_map d where d.donationId=p.id and p.id IN  ("+str(ot[0])+")"
            cursor.execute(query)
            data = cursor.fetchall()
            conn.close()
            print(len(data))
            return render_template('user_add_request.html',result=data)
        else :            
            query = "select * from pro_registration p, donation_request_map d where d.donationId=p.id and p.id IN "+str(tuple(ot))
            cursor.execute(query)
            data = cursor.fetchall()
            conn.close()
            print(len(data))
            return render_template('already_requested.html',result=data)


@app.route('/user_view_donations',methods=['GET','POST'])
def user_view_donations():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "select * from pro_registration"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('user_view_donations.html',result=data)

@app.route('/new_request',methods=['GET','POST'])
def new_request(): 
    if request.method == 'POST':
        print('here')
        print(request.args.get('pid'))
        product_id=request.args.get('pid')
        conn = mysql.connect()
        cursor = conn.cursor()
        query="select user_id from pro_registration where id="+product_id
        cursor.execute(query)
        data = cursor.fetchone()
        today = datetime.datetime.now()
        cursor.close()
        conn.close()
        conn = mysql.connect()
        cursor = conn.cursor()

        req_query = "insert into donation_request_map (`userId`,`donationId`,`created_on`) values(%s,%s,%s)"
        cursor.execute(req_query,(session['user_id'],product_id,today))
        # order_query = "INSERT INTO orders(p_id,c_id,date,status,d_id) values(%s,%s,%s,%s,%s)"
        # cursor.execute(order_query,(product_id,session['user_id'],today.strftime("%x"),'pending',data[0]))
        conn.commit()
        conn.close()
        return redirect(url_for('user_add_request'))

@app.route('/order',methods = ['GET','POST'])
def order():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "select * from donation_request_map o, pro_registration p,registration r where o.donationId=p.id and o.userId=r.id and o.status='pending'"
        cursor.execute(query)
        data = cursor.fetchall()
        print(data)
        conn.close()
        return render_template('donar_view_request.html',result=data)
    if request.method == 'POST':
        data=request.form
        print(data['id'])
        conn = mysql.connect()
        cursor = conn.cursor()
        q = "update donation_request_map set status='{}' where id='{}'"
        query = q.format('Approved',request.form.get("id"))
        print(query)
        cursor.execute(query)
        conn.commit() 
        dt = "select userId from donation_request_map where id='{}'"
        query = dt.format(request.form.get("id"))
        cursor.execute(query)
        data = cursor.fetchone()

        today = datetime.datetime.now()
        conn=mysql.connect()
        cursor=conn.cursor()
        query="insert into notification_for_user(userId,Message,date) values(%s,%s,%s)"
        cursor.execute(query,(data[0],'Your request for item accepted...',today))
        conn.commit()
        today = datetime.datetime.now()
        conn=mysql.connect()
        cursor=conn.cursor()
        query="insert into notification(notification,date,type) values(%s,%s,%s)"
        cursor.execute(query,('Item aproved',today.strftime("%x"),'volunteer'))
        conn.commit()

        return redirect(url_for('order'))

@app.route('/volunteerreg',methods = ['GET','POST'])
def volunteerreg():
    if request.method=='GET':  
        if request.args.get('head') is not None:
            head = request.args.get('head')
        else:
            head = 'Warning'

        if request.args.get('message') is not None:
            message = request.args.get('message')
        else:
            message = 'Fill Carefully'
        return render_template('volunteer_reg.html',heading=head,message=message)
    if request.method == 'POST':    
        data=request.form
        conn=mysql.connect()
        cursor=conn.cursor()   
        query="insert into registration(f_name,l_name,adrs,phone,dob,b_grp,type) values(%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query,(data['f_name'],data['l_name'],data['adrs'],data['phone'],data['dob'],'','volunteer'))
        conn.commit()
        query="insert into login(username,password,type,user_id) values (%s,%s,%s,%s)"
        cursor.execute(query,(data['username'],data['password'],'volunteer',cursor.lastrowid))
        conn.commit()
        conn.close()
        return redirect(url_for('volunteerreg',head="Successfull", message="Registered successfully"))

@app.route('/volunteer_approved_donations',methods=['GET','POST'])
def volunteer_approved_donations():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "select * from donation_request_map o, pro_registration p,registration r where o.donationId=p.id and o.userId=r.id and o.status='Ready to Deliver'"
        cursor.execute(query)
        data = cursor.fetchall()
        print(data)
        conn.close()
        return render_template('volunteer_aproved.html',result=data)




@app.route('/volunteer_view_donations',methods=['GET','POST'])
def volunteer_view_donations():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "select * from donation_request_map o, pro_registration p,registration r where o.donationId=p.id and o.userId=r.id and o.status='Approved'"
        cursor.execute(query)
        data = cursor.fetchall()
        print(data)
        conn.close()
        return render_template('volunteer_view_donation.html',result=data)
        # return render_template('volunteer_view_donation.html',result=data)       
    if request.method == "POST":
        data=request.form
        print(data['id'])
        conn = mysql.connect()
        cursor = conn.cursor()
        q = "update donation_request_map set status='{}' where id='{}'"
        query = q.format('Ready to Deliver',request.form.get("id"))
        print(query)
        cursor.execute(query)
        conn.commit() 
        dt = "select userId,donationId from donation_request_map where id='{}'"
        query = dt.format(request.form.get("id"))
        cursor.execute(query)
        data = cursor.fetchone()

        dt = "select user_id from pro_registration where id='{}'"
        query = dt.format(data[1])
        cursor.execute(query)
        datas = cursor.fetchone()



        today = datetime.datetime.now()
        conn=mysql.connect()
        cursor=conn.cursor()
        query="insert into notification_for_user(userId,Message,date) values(%s,%s,%s)"
        cursor.execute(query,(data[0],'Your Item will reach you soon...',today))
        conn.commit()


        conn=mysql.connect()
        cursor=conn.cursor()
        query="insert into notification_for_user(userId,Message,date) values(%s,%s,%s)"
        cursor.execute(query,(datas[0],'Your Item will picked up soon...',today))
        conn.commit()


        return redirect(url_for('volunteer_view_donations'))
        
@app.route('/admin_view_donation',methods=['GET','POST'])
def admin_view_donation():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "select * from orders o, pro_registration p,registration r where o.p_id=p.id and o.d_id=r.id and o.status='pending'"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('admin_view_donation.html',result=data)       
    # if request.method == "POST":
    #     data=request.form
    #     print(data['id'])
    #     conn = mysql.connect()
    #     cursor = conn.cursor()
    #     q = "update orders set status='{}' where id='{}'"
    #     query = q.format('ok',request.form.get("id"))
    #     print(query)
    #     cursor.execute(query)
    #     conn.commit() 
    #     return redirect(url_for('admin_view_donations'))
@app.route('/userviewnotification',methods=['GET','POST'])
def userviewnotification():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        print(session['user_id'])
        query = "SELECT * FROM notification_for_user where userId=%s;"
        cursor.execute(query,session['user_id'])
        data = cursor.fetchall()
        conn.close()
        return render_template('viewnotification.html',result=data)    

@app.route('/donar_view_notification',methods=['GET','POST'])
def donar_view_notification():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        print(session['user_id'])
        query = "SELECT * FROM notification_for_user where userId=%s;"
        cursor.execute(query,session['user_id'])
        data = cursor.fetchall()
        conn.close()
        return render_template('donar_view_notification.html',result=data)    


@app.route('/publicnotification',methods=['GET','POST'])
def publicnotification():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM notification where type='public'"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('public_notifications.html',result=data)    

@app.route('/userviewdoctor',methods=['GET','POST'])
def userviewdoctor():
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM doctors;"
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()
        return render_template('viewdoctor.html',result=data)    
    
if __name__=='__main__':
    app.run(debug=True,port=8000,host="localhost")
