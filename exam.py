from flask import Flask,redirect,render_template,url_for,request,jsonify,session
from flask_mysqldb import MySQL
from datetime import date
from flask_session import Session
app=Flask(__name__)
app.secret_key='#'
app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']='root'
app.config['MYSQL_DB']='exam'
app.config["SESSION_TYPE"] = "filesystem"
mysql=MySQL(app)
@app.route('/')
def home():
    return render_template('homepage.html')
@app.route('/viewstudent')
def studentinfo():
    return render_template('studentclick.html')
@app.route('/viewadmin')
def admininfo():
    return render_template('adminclick.html')
@app.route('/studentsignin',methods=['GET','POST'])
def studentsignin():
    if request.method=='POST':
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        mobilenumber=request.form['mobile']
        emailaddress=request.form['email']
        studentid=request.form['studentid']
        username=request.form['username']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('insert into student(firstname,lastname,contactnumber,emailaddress,studentid,username,password) values(%s,%s,%s,%s,%s,%s,%s)',[firstname,lastname,mobilenumber,emailaddress,studentid,username,password])
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('studentlogin'))
    return render_template('studentsignin.html')
@app.route('/adminsignin',methods=['GET','POST'])
def adminsignin():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT count(*) from admin')
    result=int(cursor.fetchone()[0])
    cursor.close()
    if result>0:
        return render_template('noadmin.html')
    else:
        if request.method=='POST':
            firstname=request.form['firstname']
            lastname=request.form['lastname']
            mobilenumber=request.form['mobile']
            emailaddress=request.form['email']
            username=request.form['username']
            password=request.form['password']
            cursor=mysql.connection.cursor()
            cursor.execute('insert into admin(firstname,lastname,mobilenumber,emailaddress,username,password) values(%s,%s,%s,%s,%s,%s)',[firstname,lastname,mobilenumber,emailaddress,username,password])
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('adminlogin'))
    return render_template('adminsignin.html')
@app.route('/studentlogin',methods=['GET','POST'])
def studentlogin():
    return render_template('studentlogin.html')
@app.route('/studentbase')
def studentbase():
    user=session['user']
    return render_template('studentbase.html')
@app.route('/studentvalidate',methods=['POST'])
def studentvalidate():
    user=request.form['user']
    password=request.form['password']
    students=request.form['studentid']
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT studentid,username,PASSWORD from student where studentid=%s',[students])
    data=cursor.fetchone()
    print(data)
    userid=data[1]
    print(userid)
    student_password=data[2]
    cursor.close()
    if user==userid and password==student_password:
        session['user']=user
        session['studentid']=students
        return redirect(url_for('studentbase'))
    else:
        return redirect(url_for('studentsignin'))
@app.route('/studentdashboard')
def studentdashboard():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT count(*) from courses')
    data=cursor.fetchone()[0]
    #total_courses=a[0]
    cursor.close()
    return render_template('studentdashboard.html',data=data)
@app.route('/coursedetails')
def studentcoursedetails():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * from courses')
    courselist=cursor.fetchall()    
    cursor.close()
    return render_template('studentcoursedetails.html',courselist=courselist)
@app.route('/studentexam')
def studentexam():
    cursor=mysql.connection.cursor()   
    cursor.execute('SELECT course_name from courses')
    data=cursor.fetchall()
    #data1=data[0]
    #print(data)
    #print(a)
    cursor.close()
    return render_template('studentexam.html',coursename=data)
@app.route('/examinstructions/<coursename>')
def takeexam(coursename):
    return render_template('takeexam.html',coursename=coursename)
@app.route('/attempts/<coursename>')
def attempt(coursename):
    students=session['studentid']
    cursor=mysql.connection.cursor()
    cursor.execute('select course_id from courses where course_name=%s',[coursename]);
    course_id=cursor.fetchone()[0]
    cursor.execute('select count(*) from submit where studentid=%s and course_id=%s',[students,course_id])
    result=int(cursor.fetchone()[0])
    if result>0:
        return render_template('noattempt.html')
    else:
        return redirect(url_for('takeexam',coursename=coursename))
@app.route('/submission')
def submit():
    return render_template('examsubmit.html')
@app.route('/startexam/<coursename>',methods=['GET','POST'])
def startexam(coursename):
    cursor=mysql.connection.cursor()
    cursor.execute('select course_id from courses where course_name=%s',[coursename]);
    course_id=cursor.fetchone()[0]
    cursor.execute('SELECT question_id,question,course_id,option1,option2,option3,option4,marks from questions where course_id=%s',[course_id])
    data=cursor.fetchall()
    cursor.close()
    if request.method=='POST':
        selectedoption=request.form.getlist('options')
        print(selectedoption)
        students=session['studentid']
        course_id=course_id
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT question_id from questions where course_id=%s',[course_id])
        question_id=cursor.fetchall()
        #print(course_id)
        #print( question_id)
        for i,j in zip(selectedoption,question_id):
                cursor=mysql.connection.cursor()
                cursor.execute('insert into submit (optionselected,studentid,course_id,question_id) values(%s,%s,%s,%s)',[i,students,course_id,j])
                mysql.connection.commit()
                cursor.close()
        return redirect(url_for('submit'))
    
    #print(a)
    #print(data)                        
    return render_template('startexam.html',data=data,course_id=course_id)
@app.route('/studentmarks')
def studentmarks():
    students=session['studentid']
    #print(students)
    cursor=mysql.connection.cursor()
    cursor.execute('select distinct(course_id) from submit where studentid=%s',[students]);
    courseid=cursor.fetchall()
    #print(courseid)
    cursor.close()
    return render_template('studentmarks.html',courseid=courseid)    
@app.route('/checkmarks/<courseid>',methods=['GET'])
def checkmarks(courseid):
    students=session['studentid']
    #print(students)
    cursor=mysql.connection.cursor()
    cursor.execute('select distinct(question_id) from submit where course_id=%s',[courseid])
    question_id=cursor.fetchall()
    cursor.execute('select count(question_id) from questions where course_id=%s',[courseid])
    data=cursor.fetchone()[0]
    cursor.execute('select sum(marks) from questions where course_id=%s',[courseid])
    data1=cursor.fetchone()[0]
    #print(question_id)
    cursor.execute('select optionselected from submit where studentid=%s and course_id=%s',[students,courseid])
    selectedoption=cursor.fetchall()
    #print(selectedoption)
    cursor.execute('select correctoption  from questions where course_id=%s',[courseid])
    correctoption=cursor.fetchall()
    print(correctoption)
    cursor.execute('select marks from questions where course_id=%s',[courseid])
    marks=cursor.fetchall()
    #print(correctoption)    
    for i in question_id:        
        count=0
        for l,m,n in zip(correctoption,selectedoption,marks):
            if l==m:
                count+=int(n[0])
            else:
                count+=0            
    cursor.close()
    return render_template('checkmarks.html',count=count,courseid=courseid,data=data,data1=data1)
@app.route('/adminlogin')
def adminlogin():
    return render_template('adminlogin.html')
@app.route('/adminbase')
def adminbase():
    return render_template('adminbase.html')
@app.route('/adminvalidate',methods=['POST'])
def adminvalidate():
    user=request.form['username']
    password=request.form['password']
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT username,PASSWORD from admin ')
    data=cursor.fetchall()[0]
    userid=data[0]
    admin_password=data[1]
    cursor.close()
    if user==userid and password==admin_password:
        return redirect(url_for('adminbase'))
    else:
        return redirect(url_for('adminsignin'))
@app.route('/admindashboard')
def admindashboard():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT count(*) from student')
    data=cursor.fetchall()
    a=data[0]
    total_registered=a[0]
    cursor.execute('SELECT count(*) from courses')
    data1=cursor.fetchall()
    a=data1[0]
    total_courses=a[0]
    cursor.execute('SELECT count(*) from questions')
    data2=cursor.fetchall()
    a=data2[0]
    total_questions=a[0]
    cursor.close()
    return render_template('admindashboard.html',total_registered=total_registered,total_courses=total_courses,total_questions=total_questions)
@app.route('/adminstudent')
def adminstudent():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT count(*) from student')
    data=cursor.fetchall()
    a=data[0]
    total_registered=a[0]
    cursor.close()
    return render_template('adminstudent.html',total_registered=total_registered)
@app.route('/admincourse')
def admincourse():    
    return render_template('admincourse.html')
@app.route('/adminquestion')
def adminquestion():
    return render_template('adminquestion.html')
@app.route('/adminviewstudent')
def adminviewstudent():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * from student')
    studentlist=cursor.fetchall()
    cursor.close()
    return render_template('adminviewstudent.html',studentlist=studentlist)
@app.route('/adminviewcourse')
def adminviewcourse():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT * from courses')
    courselist=cursor.fetchall()    
    cursor.close()
    return render_template('adminviewcourse.html',courselist=courselist)
@app.route('/adminviewquestion')
def adminviewquestion():
    cursor=mysql.connection.cursor()
    cursor.execute('SELECT course_id,question from questions')
    questionslist=cursor.fetchall()
    cursor.close()
    return render_template('adminviewquestion.html',questionslist=questionslist)
@app.route('/adminaddcourse',methods=['GET','POST'])
def adminaddcourse():
    if request.method=='POST':
        courseid=request.form['courseid']
        coursename=request.form['coursename']
        duration=request.form['courseduration']
        cursor=mysql.connection.cursor()
        cursor.execute('insert into courses(course_id,course_name,duration) values(%s,%s,%s)',[courseid,coursename,duration])
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('adminviewcourses'))
    return render_template('adminaddcourse.html')
@app.route('/adminaddquestion',methods=['GET','POST'])
def adminaddquestion():
    cursor=mysql.connection.cursor()
    cursor.execute('select course_id from courses')
    data=cursor.fetchall()
    cursor.close()
    if request.method=='POST':
        courseid=request.form['courseid']
        questionid=request.form['questionid']
        question=request.form['question']
        marks=request.form['marks']
        option1=request.form['option1']
        option2=request.form['option2']
        option3=request.form['option3']
        option4=request.form['option4']
        correctanswer=request.form['correctanswer']
        cursor=mysql.connection.cursor()
        cursor.execute('insert into questions(question_id,question,course_id,option1,option2,option3,option4,correctoption,marks) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',[questionid,question,courseid,option1,option2,option3,option4,correctanswer,marks])
        mysql.connection.commit()
        return redirect(url_for('adminquestion'))       
    return render_template('adminaddquestion.html',data=data)
@app.route('/logout')
def logout():
    return render_template('logout.html')    
app.run(debug=True)
