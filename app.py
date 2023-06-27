from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import mysql.connector

file1 = open('myfile.txt', 'r')
sql_root = file1.readline().strip()
sql_password = file1.readline().strip()
print(sql_root, sql_password)
file1.close()

app = Flask(__name__)

mydb=mysql.connector.connect(host="localhost",user=sql_root, password = sql_password,auth_plugin='mysql_native_password')
my_cursor = mydb.cursor()
qu =('set global max_allowed_packet=67108864')
my_cursor.execute(qu)

@app.route('/',methods=['GET', 'POST'])
def hello_world():
    return render_template('index.html' )

@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method=='POST':
        name = request.form['name']
        password = request.form['password']
        answer = request.form['answer']
        address= request.form['address']
        pincode = request.form['pincode']
        security =  request.form['security']
        mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
        my_cursor = mydb.cursor()
        my_cursor.execute("use gateManagement")
        add_user = ('insert into users (name,password,securityQuestion,answer,addresslines,pincode) values (%s, %s, %s, %s,%s,%s)')
        new_user = (name,password, security, answer, address, pincode)
        my_cursor.execute(add_user, new_user)
        mydb.commit()
        my_cursor.execute('Select * from users order by uid desc')
        row = my_cursor.fetchone()
        uid = row[0]
        new_url = '/user/'+str(uid)
        return redirect(new_url)

@app.route('/log',methods=['GET', 'POST'])
def userlog():
    succesfull=0
    return render_template('log.html',succesfull=succesfull)


@app.route('/userEntry',methods=['GET', 'POST'])
def userEntry():
    userId = request.form['userId']
    mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
    my_cursor = mydb.cursor()
    my_cursor.execute("use gateManagement")
    my_cursor.execute('select * from userentries')
    row_count1 = my_cursor.fetchall()
    my_cursor.callproc('insertintouserentries',(userId,))
    mydb.commit()
    my_cursor.execute('select * from userentries')
    row_count2 = my_cursor.fetchall()
    if(len(row_count1)!=len(row_count2)):
        succesfull =1
        vehicle = request.form.getlist('vehicle1')
        if(vehicle):
            vehicleNo = request.form['vehicleNo']
            my_cursor.execute('select userentryid from userentries order by userentryid desc limit 1')
            userId = my_cursor.fetchone()
            my_cursor.execute('select * from vehicleentries')
            row_count1 = my_cursor.fetchall()
            my_cursor.callproc('insertintovehicleentries',(vehicleNo,userId[0]))
            mydb.commit()
            my_cursor.execute('select * from vehicleentries')
            row_count2 = my_cursor.fetchall()
            if(len(row_count1)!=len(row_count2)):
                succesfull =1
            else:
                succesfull =-2
                my_cursor.execute('delete from userentries where userentryid = %s', (userId[0],) )
                mydb.commit()
    else:
        succesfull =-1
    succesfull_exit=0
    return render_template('log.html',succesfull=succesfull)

@app.route('/userExit',methods=['GET', 'POST'])
def userExit():
    userId = request.form['userId']
    mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
    my_cursor = mydb.cursor()
    my_cursor.execute("use gateManagement")
    my_cursor.execute("select userentryid from userentries where uid=%s order by userentryid desc limit 1", (userId,))
    userDetails = my_cursor.fetchone()
    succesfull=1
    my_cursor.execute('select * from userexits')
    row_count1 = my_cursor.fetchall()
    my_cursor.callproc('insertIntoUserExits',(userDetails[0],))
    mydb.commit()
    my_cursor.execute('select * from userexits')
    row_count2 = my_cursor.fetchall()
    if(len(row_count1)!=len(row_count2)):
        succesfull_exit =1
        vehicle = request.form.getlist('vehicle1')
        if(vehicle):
            vehicleNo = request.form['vehicleNo']
            my_cursor.execute('select userexitid from userexits order by userexitid desc limit 1')
            userId = my_cursor.fetchone()
            my_cursor.execute('select vehicleentryid from vehicleentries where vehicleno = %s order by vehicleentryid desc limit 1' , (vehicleNo,))
            vehicleEntry = my_cursor.fetchone()
            my_cursor.execute('select * from vehicleexits')
            row_count1 = my_cursor.fetchall()
            my_cursor.callproc('insertintovehicleexits',(vehicleEntry[0],userId[0]))
            mydb.commit()
            my_cursor.execute('select * from vehicleexits')
            row_count2 = my_cursor.fetchall()
            if(len(row_count1)!=len(row_count2)):
                succesfull_exit =1
            else:
                succesfull_exit =-2
                my_cursor.execute('delete from userexits where userexitid=%s',(userId[0],))
                mydb.commit()
    else:
        succesfull_exit =-1
    succesfull=0
    return render_template('log.html',succesfull_exit=succesfull_exit, succesfull=succesfull)


@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method == 'GET':
        succesfull =0
        return render_template('login.html', succesfull= succesfull)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
        my_cursor = mydb.cursor()
        my_cursor.execute("use gateManagement")
        my_cursor.execute('Select * from users where uid =%s and password=%s' , (username , password))
        record = my_cursor.fetchone()
        if record:
            return redirect('/user/'+str(record[0]))
    succesfull=-1
    return render_template('login.html', succesfull= succesfull)



@app.route('/loginAdmin', methods =['GET', 'POST'])
def loginAdmin():
    if request.method == 'GET':
        succesfull =0
        return render_template('loginAdmin.html', succesfull=succesfull)
    if request.method =='POST':
        adminId = request.form['adminId']
        password = request.form['password']
        if ((adminId == 0) or (password == 'abcd')):
            return render_template('admin.html')
    succesfull=-1
    return render_template('loginAdmin.html',succesfull=succesfull)

@app.route('/admin', methods =['GET', 'POST'])
def admin():
    return render_template('admin.html')

@app.route('/user/<username>',methods =['GET', 'POST'])
def userProfile(username):
    mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
    my_cursor = mydb.cursor()
    my_cursor.execute("use gateManagement")
    my_cursor.execute('Select * from users where uid = %s' , (username,))
    userDetails = my_cursor.fetchone()
    my_cursor.execute('Select * from vehicles where owner = %s' , (username,))
    vehicleDetails = my_cursor.fetchall()
    my_cursor.execute("""select s3.enteredIn , s3.entrytime, s3.exittime,  
    vehicleentries.vehicleno as exitedIn from vehicleentries right join(select s2.uid , s2.name, 
    s2.userentryid , s2.userexitid, s2.enteredIn , s2.vehicleentryid, s2.exittime, s2.entrytime, 
    vehicleexits.vehicleexitid,vehicleexits.vehicleentryid as vehicleexitKaentryid from vehicleexits 
    right join( select s1.uid , s1.name, s1.userentryid , s1.userexitid, vehicleentries.vehicleno as enteredIn, 
    vehicleentries.vehicleentryid, s1.exittime, s1.entrytime from vehicleentries right join (select users.Uid, 
    name, userentryid, userexitid,entrytime, exittime from users join (select userentries.userentryid, uid, 
    entrytime, userexitid,exittime from userentries left join userexits on userentries.userentryid = userexits.userentryid)s 
    on users.uid = s.uid)s1 on vehicleentries.userentryid = s1.userentryid)s2 on vehicleexits.userexitid = s2.userexitid)s3 on 
    vehicleentries.vehicleentryid = s3.vehicleexitKaentryid  where uid= %s""", (username,))
    userLog = my_cursor.fetchall()
    my_cursor.execute("""select vehicles.owner ,v8.vehicleno, v8.entrytime, v8.exittime, v8.user_entered_Uid, v8.user_entered , v8.user_exited_Uid, 
    v8.user_exited from vehicles right join (
    select v7.vehicleno, v7.entrytime,v7.exittime , v7.uid as user_entered_Uid, v7.who_entered as user_entered , v7.who_exited_uid as user_exited_Uid, 
    users.name as user_exited from users right join ( select v6.vehicleentryid, v6.userentryid, v6.vehicleno, v6.vehicleexitid, v6.userexitid, 
    v6.entrytime, v6.uid, v6.who_entered , v6.who_exited_entryid, userentries.uid as who_exited_uid , v6.exittime from userentries right join 
    (select v5.vehicleentryid, v5.userentryid, v5.vehicleno, v5.vehicleexitid, v5.userexitid, v5.entrytime, v5.uid, v5.who_entered ,
    userexits.userentryid as who_exited_entryid , userexits.exittime from userexits right join ( select  v4.vehicleentryid, v4.userentryid, 
    v4.vehicleno, v4.vehicleexitid, v4.userexitid, v4.entrytime, v4.uid, users.name as who_entered from users right join (
    select v3.vehicleentryid, v3.userentryid, v3.vehicleno, v3.vehicleexitid, v3.userexitid, userentries.entrytime, userentries.uid
    from userentries right join (select v1.vehicleentryid, v1.userentryid, v1.vehicleno, v2.vehicleexitid, v2.userexitid 
    from vehicleentries v1 left join vehicleexits v2 on v1.vehicleentryid = v2.vehicleentryid)v3 
    on v3.userentryid = userentries.userentryid)v4 on v4.uid = users.uid)v5 on v5.userexitid = userexits.userexitid)v6 
    on v6.who_exited_entryid = userentries.userentryid)v7 on v7.who_exited_uid = users.uid)v8 on v8.vehicleno = vehicles.vehicleno 
    where owner = %s""" ,(username,))
    vehicleLog = my_cursor.fetchall()
    print(userLog)
    return render_template('user.html' , userDetails=userDetails, vehicleDetails=vehicleDetails,userLog= userLog, vehicleLog=vehicleLog )

@app.route('/update/<int:username>',methods =['GET', 'POST'])
def updateProfile(username):
    if request.method == 'GET':
        mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
        my_cursor = mydb.cursor()
        my_cursor.execute("use gateManagement")
        userid = (username,)
        my_cursor.execute('Select * from users where uid = %s' , userid)
        row = my_cursor.fetchone()
        succesfull=0
        return render_template('updateUser.html' , userDetails=row,succesfull=succesfull)
    if request.method == 'POST':
        mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
        my_cursor = mydb.cursor()
        my_cursor.execute("use gateManagement")
        answer = request.form['answer']
        new_password = request.form['password']
        new_address = request.form['address']
        new_pincode = request.form['pincode']
        my_cursor.execute('select * from users where uid = %s',(username,))
        user_answer = my_cursor.fetchone()
        if(user_answer[4]==answer):
            if new_password != '':
                my_cursor.callproc('updatePassword', (new_password,answer,username))
                mydb.commit()
                succesfull=1
            if new_address != '':
                my_cursor.callproc('updateAddress', (new_address,answer,username))
                mydb.commit()
                succesfull=1
            if new_pincode != '':
                my_cursor.callproc('updatePincode', (new_pincode,answer,username))
                mydb.commit()
                succesfull=1
        else:
            succesfull=-1
        return render_template('updateUser.html' , userDetails=user_answer,succesfull=succesfull)

@app.route('/addVehicle/<int:username>',methods =['GET', 'POST'])
def addVehicle(username):
    if request.method == 'GET':
        mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
        my_cursor = mydb.cursor()
        succesfull = 0
        my_cursor.execute("use gateManagement")
        my_cursor.execute('select * from users where uid = %s',(username,))
        user_answer = my_cursor.fetchone()
        return render_template("addVehicle.html", userid = username ,succesfull=succesfull, userName=user_answer[1])
    if request.method == 'POST':
        new_vehicle_no = request.form['vehicleNo']
        new_vehicle_type = request.form['vehicle']
        mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
        my_cursor = mydb.cursor()
        my_cursor.execute("use gateManagement")
        my_cursor.execute('select * from users where uid = %s',(username,))
        user_answer = my_cursor.fetchone()
        my_cursor.execute('select * from vehicles where vehicleno = %s', (new_vehicle_no,))
        vehicle_exits = my_cursor.fetchone()
        if vehicle_exits: 
            succesfull = -1;
            return render_template('addVehicle.html', succesfull=succesfull,userid = username, userName = user_answer[1])
        my_cursor.execute("insert into vehicles values (%s, %s,%s)" , (new_vehicle_no , username, new_vehicle_type))
        mydb.commit()
        new_url = '/user/'+str(username)
        return redirect(new_url)

@app.route('/userDetails',methods =['GET', 'POST'])
def userDetail():
    mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
    my_cursor = mydb.cursor()
    my_cursor.execute("use gateManagement")
    my_cursor.execute('select * from users')
    userDetails = my_cursor.fetchall()
    return render_template("userDetails.html", userDetails=userDetails)

@app.route('/vehicleDetails',methods =['GET', 'POST'])
def vehicleDetail():
    mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
    my_cursor = mydb.cursor()
    my_cursor.execute("use gateManagement")
    my_cursor.execute('select * from vehicles')
    vehicleDetails = my_cursor.fetchall()
    return render_template("vehicleDetails.html", vehicleDetails=vehicleDetails)

@app.route('/allLogs',methods =['GET', 'POST'])
def allLogsDetails():
    mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
    my_cursor = mydb.cursor()
    my_cursor.execute("use gateManagement")
    my_cursor.execute("""select s3.uid , s3.name, s3.enteredIn , s3.entrytime, s3.exittime,  
    vehicleentries.vehicleno as exitedIn from vehicleentries right join(select s2.uid , s2.name, 
    s2.userentryid , s2.userexitid, s2.enteredIn , s2.vehicleentryid, s2.exittime, s2.entrytime, 
    vehicleexits.vehicleexitid,vehicleexits.vehicleentryid as vehicleexitKaentryid from vehicleexits 
    right join( select s1.uid , s1.name, s1.userentryid , s1.userexitid, vehicleentries.vehicleno as enteredIn, 
    vehicleentries.vehicleentryid, s1.exittime, s1.entrytime from vehicleentries right join (select users.Uid, 
    name, userentryid, userexitid,entrytime, exittime from users join (select userentries.userentryid, uid, 
    entrytime, userexitid,exittime from userentries left join userexits on userentries.userentryid = userexits.userentryid)s 
    on users.uid = s.uid)s1 on vehicleentries.userentryid = s1.userentryid)s2 on vehicleexits.userexitid = s2.userexitid)s3 on 
    vehicleentries.vehicleentryid = s3.vehicleexitKaentryid""", )
    logDetails = my_cursor.fetchall()
    return render_template("logDetails.html", logDetails=logDetails)

@app.route('/report',methods =['GET', 'POST'])
def report():
    mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
    my_cursor = mydb.cursor()
    my_cursor.execute("use gateManagement")
    my_cursor.execute("""select hour(exittime) as hour_, count(*) from
                        (SELECT userexitid, exittime  from userexits union 
                        SELECT userentryid,entrytime  from userentries)s
                        group by hour_ order by count(*) desc limit 1""")
    peakHours = my_cursor.fetchone()
    my_cursor.execute("select count(*) from vehicles;")
    noOfVehicles = my_cursor.fetchone()
    my_cursor.execute('select count(*) from users')
    noOfUsers = my_cursor.fetchone()
    my_cursor.execute('select type, count(*) from vehicles group by type')
    vehicleTypes = my_cursor.fetchall()
    my_cursor.execute('select count(*) from userentries')
    noOfEntries = my_cursor.fetchone()
    my_cursor.execute('select count(*) from userexits')
    noOfExits = my_cursor.fetchone()
    my_cursor.execute('select count(*) from userentries where date(entrytime)>=curdate()')
    noOfEntriesToday = my_cursor.fetchone()
    my_cursor.execute('select count(*) from userexits where date(exittime)>=curdate();')
    noOfExitsToday = my_cursor.fetchone()
    my_cursor.execute('select count(*) from vehicleentries')
    noOfVehicleEntries = my_cursor.fetchone()
    my_cursor.execute('select count(*) from vehicleexits')
    noOfVehicleExits = my_cursor.fetchone()
    my_cursor.execute('select now()')
    current_time = my_cursor.fetchone()
    my_cursor.execute('select time(entrytime) as time from userentries where date(entrytime)>=curdate() order by time')
    firstEntryTime = my_cursor.fetchall()
    my_cursor.execute('select time(exittime) as time from userexits where date(exittime)>=curdate() order by time')
    firstExitTime = my_cursor.fetchall()
    return render_template('report.html' , peakHours = peakHours, noOfVehicles=noOfVehicles, noOfUsers=noOfUsers,
    vehicleTypes=vehicleTypes, noOfEntries=noOfEntries, noOfExits=noOfExits,noOfEntriesToday=noOfEntriesToday,
    noOfExitsToday=noOfExitsToday, noOfVehicleEntries=noOfVehicleEntries, noOfVehicleExits=noOfVehicleExits,
    current_time=current_time[0], firstEntryTime = firstEntryTime[0], firstExitTime=firstExitTime[0])

@app.route('/updateUserByAdmin/<int:username>',methods =['GET', 'POST'])
def updateProfileByAdmin(username):
    if request.method == 'GET':
        mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
        my_cursor = mydb.cursor()
        my_cursor.execute("use gateManagement")
        userid = (username,)
        my_cursor.execute('Select * from users where uid = %s' , userid)
        row = my_cursor.fetchone()
        succesfull=0
        return render_template('updateUserByAdmin.html' , userDetails=row, succesfull=succesfull)
    if request.method == 'POST':
        mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
        my_cursor = mydb.cursor()
        my_cursor.execute("use gateManagement")
        new_password = request.form['password']
        new_number = request.form['phoneNo']
        my_cursor.execute('Select answer from users where uid = %s', (username,))
        answer = my_cursor.fetchone()
        if new_password != '' :
            my_cursor.callproc('updatePassword', (new_password,answer[0],username))
        mydb.commit()
        if new_number != '':
            pass
        new_url = '/updateUserByAdmin/'+str(username)
        succesfull=1
        my_cursor.execute('Select * from users where uid = %s' , (username,))
        row = my_cursor.fetchone()
        return render_template('updateuserByAdmin.html', successful=succesfull,userDetails=row)

@app.route('/logUsers',methods =['GET', 'POST'])
def userLogs():
    mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
    my_cursor = mydb.cursor()
    my_cursor.execute("use gateManagement")
    my_cursor.execute(""" select users.name ,u3.uid ,u3.entrytime, u3.exittime from users right join (
    select u1.uid ,u1.entrytime, u2.exittime from userentries u1 left join userexits u2 on 
    u1.userentryid = u2.userentryid)u3 on u3.uid = users.uid""" )
    logDetails = my_cursor.fetchall()
    return render_template("logUserDetails.html", logDetails=logDetails)

@app.route('/logVehicles',methods =['GET', 'POST'])
def vehicleLogs():
    if request.method =='GET':
        mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
        my_cursor = mydb.cursor()
        my_cursor.execute("use gateManagement")
        my_cursor.execute(""" select vehicles.owner ,v8.vehicleno, v8.entrytime, v8.exittime, v8.user_entered ,
    v8.user_exited from vehicles right join (
    select v7.vehicleno, v7.entrytime,v7.exittime , v7.uid as user_entered_Uid, v7.who_entered as user_entered , v7.who_exited_uid as user_exited_Uid, 
    users.name as user_exited from users right join ( select v6.vehicleentryid, v6.userentryid, v6.vehicleno, v6.vehicleexitid, v6.userexitid, 
    v6.entrytime, v6.uid, v6.who_entered , v6.who_exited_entryid, userentries.uid as who_exited_uid , v6.exittime from userentries right join 
    (select v5.vehicleentryid, v5.userentryid, v5.vehicleno, v5.vehicleexitid, v5.userexitid, v5.entrytime, v5.uid, v5.who_entered ,
    userexits.userentryid as who_exited_entryid , userexits.exittime from userexits right join ( select  v4.vehicleentryid, v4.userentryid, 
    v4.vehicleno, v4.vehicleexitid, v4.userexitid, v4.entrytime, v4.uid, users.name as who_entered from users right join (
    select v3.vehicleentryid, v3.userentryid, v3.vehicleno, v3.vehicleexitid, v3.userexitid, userentries.entrytime, userentries.uid
    from userentries right join (select v1.vehicleentryid, v1.userentryid, v1.vehicleno, v2.vehicleexitid, v2.userexitid 
    from vehicleentries v1 left join vehicleexits v2 on v1.vehicleentryid = v2.vehicleentryid)v3 
    on v3.userentryid = userentries.userentryid)v4 on v4.uid = users.uid)v5 on v5.userexitid = userexits.userexitid)v6 
    on v6.who_exited_entryid = userentries.userentryid)v7 on v7.who_exited_uid = users.uid)v8 on v8.vehicleno = vehicles.vehicleno  ;""" )
        logDetails = my_cursor.fetchall()
        return render_template("logvehicledetails.html", logDetails=logDetails)

    if request.method=='POST':
        mydb=mysql.connector.connect(host="localhost", user=sql_root, password = sql_password, auth_plugin='mysql_native_password')
        my_cursor = mydb.cursor()
        my_cursor.execute("use gateManagement")
        vehicleNo = request.form['vehicleNo']
        print(vehicleNo)
        my_cursor.execute(""" select vehicles.owner ,v8.vehicleno, v8.entrytime, v8.exittime, v8.user_entered ,
v8.user_exited from vehicles right join (
select v7.vehicleno, v7.entrytime,v7.exittime , v7.uid as user_entered_Uid, v7.who_entered as user_entered , v7.who_exited_uid as user_exited_Uid, 
users.name as user_exited from users right join ( select v6.vehicleentryid, v6.userentryid, v6.vehicleno, v6.vehicleexitid, v6.userexitid, 
v6.entrytime, v6.uid, v6.who_entered , v6.who_exited_entryid, userentries.uid as who_exited_uid , v6.exittime from userentries right join 
(select v5.vehicleentryid, v5.userentryid, v5.vehicleno, v5.vehicleexitid, v5.userexitid, v5.entrytime, v5.uid, v5.who_entered ,
userexits.userentryid as who_exited_entryid , userexits.exittime from userexits right join ( select  v4.vehicleentryid, v4.userentryid, 
v4.vehicleno, v4.vehicleexitid, v4.userexitid, v4.entrytime, v4.uid, users.name as who_entered from users right join (
select v3.vehicleentryid, v3.userentryid, v3.vehicleno, v3.vehicleexitid, v3.userexitid, userentries.entrytime, userentries.uid
from userentries right join (select v1.vehicleentryid, v1.userentryid, v1.vehicleno, v2.vehicleexitid, v2.userexitid 
from vehicleentries v1 left join vehicleexits v2 on v1.vehicleentryid = v2.vehicleentryid)v3 
on v3.userentryid = userentries.userentryid)v4 on v4.uid = users.uid)v5 on v5.userexitid = userexits.userexitid)v6 
on v6.who_exited_entryid = userentries.userentryid)v7 on v7.who_exited_uid = users.uid)v8 on v8.vehicleno = vehicles.vehicleno  where vehicles.vehicleno= %s ;""" , (vehicleNo,) )
        logDetails = my_cursor.fetchall()
        print(logDetails)
        return render_template("logvehicledetails.html", logDetails=logDetails)

if __name__ == "__main__":
    app.run(debug=True,port=8000)