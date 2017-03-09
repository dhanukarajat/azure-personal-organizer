__author__ = 'Rajat'
"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, session, url_for
from FlaskWebProject import app
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from imageData import imageData
from userData import userData
import sys
import pymongo
import uuid
import base64

app.secret_key = "rajat"

userCollection = "users"
filesCollection = "userfiles"

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'JPG'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Connection to MongoDB
def createDBConn():
    mongoconn = 'mongodb://username:password@dbid.mlab.com:dbid/dbname'
    client = pymongo.MongoClient(mongoconn)
    db = client.get_default_database()
    return client, db


@app.route('/')
def home():
    """Renders the home page."""
    return render_template(
        'home.html')


global startt1


# Login page for users
@app.route('/login_user', methods=['POST'])
def login_user():
    global startt1
    startt1 = datetime.now()
    if request.form['modeSelection'] == 'Register':
        return render_template('register.html')
    else:
        loginid = request.form['loginid']
        password = request.form['password']
        db_start = datetime.now()
        client, db = createDBConn()
    userDirectory = db[userCollection]
    userDocument = {}
    userDocument['loginid'] = loginid
    userDocument['password'] = password
    user = userDirectory.find_one(userDocument)
    client.close()
    db_end = datetime.now()
    db_time = str(db_end - db_start)  # Database time
    if user is not None:
        session['loginid'] = loginid
        session['userid'] = str(user['_id'])
        session['otherImages'] = str(user['_id'])
        # images, notes, photos = getFiles(ObjectId(session['userid']))
        t2 = datetime.now()
        return render_template('user.html', dbtime="Connection to DB finished in :" + db_time, loginid=loginid,
                               logintime="Time taken to login is :" + str(t2 - startt1), userid=str(user['_id']))
    else:
        t2 = datetime.now()
        msg = "Invalid credentials"
        return render_template('home.html', dbtime="Connection to DB finished in :" + db_time,
                               logintime="Time taken to login is :" + str(t2 - startt1), imsg=msg)


# Registration for new users
@app.route('/register_user', methods=['POST'])
def register_user():
    t1 = datetime.now()
    name = request.form['name']
    loginid = request.form['loginid']
    password = request.form['password']
    loginRegister = {}
    loginRegister['name'] = name
    loginRegister['loginid'] = loginid
    loginRegister['password'] = password
    client, db = createDBConn()
    userDirectory = db[userCollection]
    userDirectory.insert(loginRegister)
    t2 = datetime.now()
    msg = "Registration successful"
    return render_template('home.html', logintime="Time taken to register is :" + str(t2 - t1), imsg=msg)


# Uploading a note or image
@app.route('/upload_image', methods=['POST'])
def upload_image():
    t1 = datetime.now()
    loginid = request.form['loginid']
    client, db = createDBConn()
    file = request.files['mongoUpload']
    postComment = request.form['postComment']
    tag = request.form['tagg']
    tag = (tag[:100] + '*') if len(tag) > 100 else tag
    priority = int(request.form['priority'])
    file_name = file.filename
    userid = ObjectId(request.form['userid'])
    fileTuple = {}
    fileTuple['userid'] = userid
    fileTuple['priority'] = priority
    if file and allowed_file(file.filename):
        content = file.read()
        fileTuple['filedata'] = "data:image/jpeg;base64," + base64.b64encode(content)
        fileTuple['fileType'] = "image"
    else:
        content = file.read()
        fileTuple['filedata'] = content
        fileTuple['fileType'] = "note"

    fileTuple['tags'] = tag
    fileTuple['postComment'] = [postComment]
    fileTuple['uploadTime'] = datetime.now()
    fileTuple['filesize'] = len(content)
    fileTuple['uploader'] = loginid
    filesDirectory = db[filesCollection]
    filesDirectory.insert(fileTuple)
    client.close()

    t2 = datetime.now()
    return render_template('user.html', loginid=loginid, userid=userid,
                           uploadtime="File uploaded successfully. Time taken to upload is :" + str(t2 - t1))


# Retrieving user data from database
def getFiles(userid):
    client, db = createDBConn()
    filesDirectory = db[filesCollection]
    fileTuple = {}

    fileTuple['userid'] = userid
    filesID = filesDirectory.find(fileTuple).sort([("tags", pymongo.ASCENDING)])
    client.close()
    images = []
    notes = []
    photos = []

    for files in filesID:
        fileID = files['_id']
        fuploader = files['uploader']
        priority = files['priority']
        picdata = files['filedata']
        tag = files['tags']
        comment = files['postComment']
        uploadTime = files['uploadTime']
        fileType = files['fileType']
        picture = imageData(fileID, fuploader, priority, picdata, tag, comment, uploadTime, fileType)
        images.append(picture)
        if fileType == "note":
            notes.append(picture)
        else:
            photos.append(picture)
    return images, notes, photos


# Displaying all the notes and photos
@app.route('/view_all', methods=['POST'])
def view_all():
    t1 = datetime.now()
    displaytime = ""
    loginid = request.form['loginid']
    client, db = createDBConn()
    filesDirectory = db[filesCollection]
    fileTuple = {}
    fileTuple['userid'] = ObjectId(request.form['userid'])
    sort_type = None
    sort_order = None
    try:
        sort_type = str(request.form.get('sortmode'))
        sort_order = request.form['sort_order']
    except:
        None
    if (sort_type == None or sort_order == None):
        filesID = filesDirectory.find(fileTuple)
    else:
        if (sort_order == "desc"):
            filesid = filesDirectory.find(fileTuple).sort(sort_type, pymongo.DESCENDING)
        else:
            filesid = filesDirectory.find(fileTuple).sort(sort_type, pymongo.ASCENDING)
    client.close()
    t3 = datetime.now()
    images = []
    for files in filesid:
        fileID = files['_id']
        fuploader = files['uploader']
        priority = files['priority']
        picdata = files['filedata']
        tag = files['tags']
        comment = files['postComment']
        uploadTime = files['uploadTime']
        fileType = files['fileType']
        picture = imageData(fileID, fuploader, priority, picdata, tag, comment, uploadTime, fileType)
        images.append(picture)

    t2 = datetime.now()
    if loginid == "admin":
        return render_template('view_admin_images.html', images=images,
                               displaytime="Time taken to sort is :" + str(t3 - t1),
                               viewtime="Time taken to retrieve and view image is :" + str(t2 - t1))
    else:
        return render_template('view_user_images.html', images=images,
                               displaytime="Time taken to sort is :" + str(t3 - t1),
                               viewtime="Time taken to retrieve and view image is :" + str(t2 - t1))


# Displaying notes only
@app.route('/view_notes', methods=['POST'])
def view_notes():
    t1 = datetime.now()
    displaytime = ""
    loginid = request.form['loginid']
    images, notes, photos = getFiles(ObjectId(session['otherImages']))
    t2 = datetime.now()
    if loginid == "admin":
        return render_template('view_admin_images.html', images=notes, displaytime=displaytime,
                               viewtime="Time taken to retrieve and view image is :" + str(t2 - t1))
    else:
        return render_template('view_user_images.html', images=notes, displaytime=displaytime,
                               viewtime="Time taken to retrieve and view image is :" + str(t2 - t1))


# Displaying photos only
@app.route('/view_photos', methods=['POST'])
def view_photos():
    t1 = datetime.now()
    displaytime = ""
    loginid = request.form['loginid']
    images, notes, photos = getFiles(ObjectId(session['otherImages']))
    t2 = datetime.now()
    if loginid == "admin":
        return render_template('view_admin_images.html', images=photos, displaytime=displaytime,
                               viewtime="Time taken to retrieve and view image is :" + str(t2 - t1))
    else:
        return render_template('view_user_images.html', images=photos, displaytime=displaytime,
                               viewtime="Time taken to retrieve and view image is :" + str(t2 - t1))


# Displaying public data
@app.route('/view_public_images', methods=['POST'])
def view_public_images():
    client, db = createDBConn()
    listusers = []
    userDirectory = db[userCollection]
    filesDirectory = db[filesCollection]
    users = userDirectory.find()
    for user in users:
        if user['loginid'] != session['loginid']:
            current_user = userData(user['loginid'], str(user['_id']))
            listusers.append(current_user)

    return render_template('view_all_images.html', listusers=listusers)


@app.route('/view_images_for')
def view_images_for():
    userid = request.args.get('userid')
    loginid = request.args.get('loginid')
    session['otherImages'] = userid
    t1 = datetime.now()
    displaytime = ""
    client, db = createDBConn()
    filesDirectory = db[filesCollection]
    fileTuple = {}
    fileTuple['userid'] = ObjectId(userid)
    filesid = filesDirectory.find(fileTuple).sort([("tags", pymongo.ASCENDING)])
    client.close()
    images = []
    for files in filesid:
        fileID = files['_id']
        fuploader = files['uploader']
        priority = files['priority']
        picdata = files['filedata']
        tag = files['tags']
        comment = files['postComment']
        uploadTime = files['uploadTime']
        fileType = files['fileType']
        picture = imageData(fileID, fuploader, priority, picdata, tag, comment, uploadTime, fileType)
        images.append(picture)

    t2 = datetime.now()
    if loginid == "admin":
        return render_template('view_admin_images.html', images=images, displaytime=displaytime,
                               viewtime="Time taken to retrieve and view image is :" + str(t2 - t1))
    else:
        return render_template('view_user_images.html', images=images, displaytime=displaytime,
                               viewtime="Time taken to retrieve and view image is :" + str(t2 - t1))


# Adding a comment
@app.route('/add_comment', methods=['POST'])
def add_comment():
    displaytime = ""
    loginid = session['loginid']
    new_comment = request.form['mongocomment']
    id = request.form['id']
    client, db = createDBConn()

    filesDirectory = db[filesCollection]
    filesDirectory.update({'_id': ObjectId(id)}, {'$push': {'postComment': new_comment}})
    client.close()
    images, notes, photos = getFiles(ObjectId(session['otherImages']))
    if loginid == "admin":
        return render_template('view_admin_images.html', images=images, displaytime=displaytime)
    else:
        return render_template('view_user_images.html', images=images, displaytime=displaytime)


# Modifying the subject
@app.route('/modify_tag', methods=['POST'])
def modify_tag():
    displaytime = ""
    loginid = session['loginid']
    new_tag = request.form['mongotag']
    id = request.form['id']
    client, db = createDBConn()
    filesDirectory = db[filesCollection]
    fileTuple = {}
    fileTuple['userid'] = ObjectId(session['otherImages'])
    filesid = filesDirectory.find(fileTuple).sort([("priority", pymongo.ASCENDING), ("tag", 1)])
    for files in filesid:
        tag = files['tags']
        # if len(tag) > 3:
        # return "Maximum limit for tags is exceeded"
        # else:
        filesDirectory.update({'_id': ObjectId(id)}, {'$set': {'tags': new_tag}})
    client.close()
    images, notes, photos = getFiles(ObjectId(session['otherImages']))
    if loginid == "admin":
        return render_template('view_admin_images.html', images=images, displaytime=displaytime)
    else:
        return render_template('view_user_images.html', images=images, displaytime=displaytime)


# Modifying the priority
@app.route('/modify_priority', methods=['POST'])
def modify_priority():
    displaytime = ""
    loginid = session['loginid']
    new_priority = int(request.form['mongopriority'])
    id = request.form['id']
    client, db = createDBConn()
    filesDirectory = db[filesCollection]
    fileTuple = {}
    fileTuple['userid'] = ObjectId(session['otherImages'])
    filesid = filesDirectory.find(fileTuple).sort([("priority", pymongo.ASCENDING), ("tag", 1)])
    for files in filesid:
        priority = files['priority']
        filesDirectory.update({'_id': ObjectId(id)}, {'$set': {'priority': new_priority}})
    client.close()
    images, notes, photos = getFiles(ObjectId(session['otherImages']))
    if loginid == "admin":
        return render_template('view_admin_images.html', images=images, displaytime=displaytime)
    else:
        return render_template('view_user_images.html', images=images, displaytime=displaytime)


# Searching image based on subject
@app.route('/search_image', methods=['POST'])
def search_image():
    t1 = datetime.now()
    loginid = request.form['loginid']
    tosearch = str(request.form['tosearch'])
    client, db = createDBConn()
    filesDirectory = db[filesCollection]
    files = filesDirectory.find({'filedata':{'$regex':tosearch}})
    #files = filesDirectory.find({"tags": {'$in': [tosearch]}}).sort([("priority", pymongo.ASCENDING), ("tag", 1)])
    images = []
    for file in files:
        fileID = file['_id']
        uploader = file['uploader']
        priority = file['priority']
        picdata = file['filedata']
        tag = file['tags']
        comment = file['postComment']
        uploadTime = file['uploadTime']
        fileType = file['fileType']
        picture = imageData(fileID, uploader, priority, picdata, tag, comment, uploadTime, fileType)
        images.append(picture)
    client.close()
    t2 = datetime.now()
    if loginid == "admin":
        return render_template('view_admin_images.html', images=images, loginid=loginid,
                               displaytime="Time taken to search is :" + str(t2 - t1))
    else:
        return render_template('view_user_images.html', images=images, loginid=loginid,
                               displaytime="Time taken to search is :" + str(t2 - t1))


# Searching image based on time
@app.route('/search_time', methods=['POST'])
def search_time():
    t1 = datetime.now()
    loginid = request.form['loginid']
    # tosearch = request.form['tosearch']
    time_delta = request.form['time_delta']
    time_interval = datetime.now() - timedelta(minutes=int(time_delta))
    print time_interval
    client, db = createDBConn()
    filesDirectory = db[filesCollection]
    files = filesDirectory.find({"uploadTime": {"$gte": time_interval}}).sort([("_id", 1)])
    images = []
    #for file in files:
    #    filesDirectory.remove(file['_id'])
    #client.close()
    #t2 = datetime.now()
    #msg = "Deleted successfully"
    #return render_template('user.html', loginid=loginid, imsg=msg,
    #                      uploadtime="Time taken to delete is :" + str(t2 - t1))
    for file in files:
        fileID = file['_id']
        uploader = file['uploader']
        priority = file['priority']
        picdata = file['filedata']
        tag = file['tags']
        comment = file['postComment']
        uploadTime = file['uploadTime']
        fileType = file['fileType']
        picture = imageData(fileID, uploader, priority, picdata, tag, comment, uploadTime, fileType)
        images.append(picture)
    client.close()
    t2 = datetime.now()
    if loginid == "admin":
        return render_template('view_admin_images.html', images=images, loginid=loginid,
                               displaytime="Time taken to search is :" + str(t2 - t1))
    else:
        return render_template('view_user_images.html', images=images, loginid=loginid,
                               displaytime="Time taken to search is :" + str(t2 - t1))


# Deleting the file
@app.route('/delete_file', methods=['POST'])
def delete_file():
    t1 = datetime.now()
    loginid = session['loginid']
    fileid = request.form['delete_button']
    client, db = createDBConn()

    filesDirectory = db[filesCollection]
    file = ObjectId(fileid)
    fileTuple = {}
    fileTuple['_id'] = file
    filesID = filesDirectory.find(fileTuple)

    for files in filesID:
        filesDirectory.remove(files['_id'])
    client.close()
    images, notes, photos = getFiles(ObjectId(session['otherImages']))
    t2 = datetime.now()
    if loginid == "admin":
        return render_template('view_admin_images.html', images=images, loginid="",
                               displaytime="Image deleted in:" + str(t2 - t1) + "seconds")
    else:
        return render_template('view_user_images.html', images=images, loginid="",
                               displaytime="Image deleted in:" + str(t2 - t1) + "seconds")


# Deleting the file based on subject name
@app.route('/delete_userchoice', methods=['POST'])
def delete_userchoice():
    t1 = datetime.now()
    loginid = request.form['loginid']
    deletekey = request.form['deletekey']
    client, db = createDBConn()
    filesDirectory = db[filesCollection]
    files = filesDirectory.find({"tags": {'$in': [deletekey]}})
    for file in files:
        filesDirectory.remove(file['_id'])
    client.close()
    t2 = datetime.now()
    msg = "Deleted successfully"
    return render_template('user.html', loginid=loginid, imsg=msg,
                           uploadtime="Time taken to delete is :" + str(t2 - t1))


# Logging out 
@app.route('/logout', methods=['POST'])
def logout():
    global startt1
    session.clear()
    t2 = datetime.now()
    msg = "Thank you for using Pixelate"
    return render_template('home.html', logintime="Time taken to logout is :" + str(t2 - startt1), imsg=msg)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500


if __name__ == "__main__":
    app.run()