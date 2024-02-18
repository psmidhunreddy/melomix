from flask import Blueprint,request, redirect, flash, url_for, session
from flask import render_template
from flask_login import login_required, current_user
from . import db
from sqlalchemy.sql import func
import datetime
import pytz
from werkzeug.utils import secure_filename
from .models import Creator,User,song,rating,Playlist,SongPlaylist,Album,SongAlbum
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy import and_,or_
import matplotlib.pyplot as plt
plt.switch_backend('agg')

view = Blueprint('home_views', __name__)
def rategraph():
    result=db.session.query(func.avg(rating.rating)).group_by(rating.sid).all()
    rate=[]
    for r in result:
        rate.append(r[0])
    fig = plt.figure()
    plt.xlabel("Rating")
    plt.ylabel("No of Songs")
    plt.title('Songs Vs Ratings')
    plt.hist(rate, color = "skyblue")
    fig.savefig("web/static/img.png")
    
def usercreatorgraph():
    users=len(User.query.all())
    creatos=len(Creator.query.all())
    data={'Users':users,'Creator':creatos}
    key = list(data.keys())
    values = list(data.values())
    fig1=plt.figure()
    plt.ylabel("Count")
    plt.title("Users & Creators")
    plt.bar(key, values, color ='maroon', width = 0.4)
    fig1.savefig("web/static/img1.png")

def diffcreator():
    new=len(Creator.query.filter(Creator.flag==0).all())
    exist=len(Creator.query.filter(Creator.flag==1).all())
    blacklist=len(Creator.query.filter(Creator.flag==2).all())
    data={'New Requests':new,'Exsisting Creators':exist,'BlackListed Creators':blacklist}
    key = list(data.keys())
    values = list(data.values())
    fig2=plt.figure()
    plt.ylabel("Count")
    plt.title("Creators")
    plt.bar(key, values, color ='skyblue', width = 0.4)
    fig2.savefig("web/static/img2.png")

def songplaylistalbum():
    songs=len(song.query.all())
    playlists=len(Playlist.query.all())
    albums=len(Album.query.all())
    data={'Songs':songs,'Playlists':playlists,'Albums':albums}
    key = list(data.keys())
    values = list(data.values())
    fig3=plt.figure()
    plt.ylabel("Count")
    plt.title("Songs Vs Playlists Vs Albums")
    plt.bar(key, values, color ='skyblue', width = 0.4)
    fig3.savefig("web/static/img3.png")

def playlistprivacy():
    public=len(Playlist.query.filter(Playlist.privacy==1).all())
    private=len(Playlist.query.filter(Playlist.privacy==0).all())
    data={'Public':public,'Private':private}
    key = list(data.keys())
    values = list(data.values())
    fig4=plt.figure()
    plt.ylabel("Count")
    plt.title("Public Vs Private Playlist")
    plt.bar(key, values, color ='skyblue', width = 0.4)
    fig4.savefig("web/static/img4.png")

def allow_file(filename):
    ALLOWED_EXTENSION = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION
#def allow_file(filename):
    ALLOWED_EXTENSION = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION

@view.route("/userhome",methods=['GET','POST'])
@login_required
def userhome():
    if 'user_type' in session:
        if session["user_type"] == "user":
            user=current_user
            creator=Creator.query.filter(Creator.uid==user.id).first()
            songs=song.query.all()
            playlist=Playlist.query.all()
            album=Album.query.all()
            return render_template("userhome.html",user=user,creator=creator,songs=songs,playlist=playlist,album=album,hour=datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour)
    return render_template("userlogin.html")

@view.route("/userprofile",methods=['GET','POST'])
@login_required
def userprofile():
    if request.method=='POST':
        input_password=request.form.get("password")
        input_npassword=request.form.get("npassword")
        input_cpassword=request.form.get("cpassword")
        if input_password:
            user=current_user
            if check_password_hash(user.password, input_password):
                if input_npassword==input_cpassword and len(input_npassword) > 6:
                    password=generate_password_hash(input_npassword)
                    user.password=password
                    db.session.commit()
                    flash('Update successfull','success')
                elif len(input_npassword) < 6:
                    flash('Password length should be atleast 6', category='error')
                else:
                    flash('Password did not match','error')
            else:
                flash('Password incorrect','error')
        else:
            user=current_user
            input_name=request.form.get("name")
            input_pno=request.form.get("pno")
            input_photo=request.files["photo"]
            if input_photo and  allow_file(input_photo.filename):
                filename="user_"+str(user.id)+"profilephoto"+secure_filename(input_photo.filename)
                input_photo.save(os.path.join(view.root_path, 'static/profile_photos/', filename))
                input_url = "/static/profile_photos/" + filename
                user.profile_photo = input_url
                db.session.commit()
            
            user.name=input_name
            user.pno=input_pno
            db.session.commit()
        
    if 'user_type' in session:
        if session["user_type"] == "user":
            user=current_user
            creator=Creator.query.filter(Creator.uid==user.id).first()
            playlist=Playlist.query.filter(Playlist.uid==user.id).all()
            creator=Creator.query.filter(Creator.uid==user.id).first()
            if creator:
                songs=song.query.filter(song.cid==creator.id).all()
                albums=Album.query.filter(Album.cid==creator.id).all()
                return render_template("userprofile.html",user=user,creator=creator,songs=songs,albums=albums)
            return render_template("userprofile.html",user=user,creator=creator,playlist=playlist)
    
@view.route("/adminhome",methods=['GET','POST'])
@login_required
def adminhome():
    if 'user_type' in session:
        if session["user_type"] == "admin":
            admin=current_user
            return render_template("adminhome.html",admin=admin,hour=datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour)
    return render_template("adminlogin.html")

@view.route("/admin-dashboard")
@login_required
def admindashboard():
    if 'user_type' in session:
        if session["user_type"] == "admin":
            admin=current_user
            user=User.query.all()
            creator=Creator.query.filter(Creator.flag==1).all()
            s=song.query.all()
            p=Playlist.query.all()
            a=Album.query.all()
            rategraph()
            usercreatorgraph()
            diffcreator()
            songplaylistalbum()
            playlistprivacy()
            return render_template("admindashboard.html",admin=admin,user=user,creator=creator,song=s,playlist=p,album=a,datetime=datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
@view.route("/mad-song-manage",methods=['GET','POST'])
@login_required
def madsong():
    if 'user_type' in session:
        if session["user_type"] == "admin":
            admin=current_user
            user=User.query.all()
            creator=Creator.query.all()
            
            if request.method=='POST':
                action=request.form.get("action")
                if action=='song':
                    sid=request.form.get("sid")
                    keep=request.form.get("keep")
                    delete=request.form.get("delete")
                    res_song=song.query.filter(song.id==sid).one()
                    if keep:
                        res_song.flag_rate=0
                        db.session.commit()
                    if delete:
                        db.session.delete(res_song)
                        db.session.commit()
                    
                elif action=='playlist':
                    pid=request.form.get("pid")
                    keep=request.form.get("keep")
                    delete=request.form.get("delete")
                    res_playlist=Playlist.query.filter(Playlist.id==pid).one()
                    if keep:
                        res_playlist.flag_rate=0
                        db.session.commit()
                    if delete:
                        db.session.delete(res_playlist)
                        db.session.commit()
                    
                elif action=='album':
                    aid=request.form.get("aid")
                    keep=request.form.get("keep")
                    delete=request.form.get("delete")
                    res_album=Album.query.filter(Album.id==aid).one()
                    if keep:
                        res_album.flag_rate=0
                        db.session.commit()
                    if delete:
                        db.session.delete(res_album)
                        db.session.commit()
            s=song.query.filter(song.flag_rate>0).all()
            p=Playlist.query.filter(Playlist.flag_rate>0).all()
            a=Album.query.filter(Album.flag_rate>0).all()  
            return render_template("adminmanage1.html",admin=admin,user=user,creator=creator,song=s,playlist=p,album=a,datetime=datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
@view.route("/mad-creator-manage",methods=['GET','POST'])
@login_required
def madcreator():
    if 'user_type' in session:
        if session["user_type"] == "admin":
            admin=current_user
            user=User.query.all()
            if request.method == "POST":
                input_flag=request.form.get("flag")
                input_id=request.form.get("id")
                cre=Creator.query.filter(Creator.id==input_id).first()
                if cre:
                    flag=0
                    if input_flag=="Deny" or input_flag=="Remove Creator":
                        flag=0
                    elif input_flag=="Approve" or input_flag=="White List":
                        flag=1
                    elif input_flag=="Black List":
                        flag=2
                    cre.flag=flag
                    if cre.flag==0:
                        db.session.delete(cre)
                db.session.commit()
                return redirect(url_for('home_views.madcreator'))
            creator=Creator.query.all()  
            return render_template("adminmanage2.html",admin=admin,user=user,creator=creator,datetime=datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
    return redirect(url_for('auth.admin'))

@view.route("/creatorprofile",methods=['GET','POST'])
@login_required
def creatorprofile():
    if session["user_type"] == "user":
        user=current_user
        cid_exists= Creator.query.filter(Creator.uid==user.id).first()
        if cid_exists==None:
            return redirect(url_for('auth.creator'))
        if cid_exists and cid_exists.flag==1:
            flash("You are now a creator", category='success')
        elif cid_exists and  cid_exists.flag==2:
            flash("You are black listed", category='warning') 
        elif cid_exists and cid_exists.flag==0:
            flash("Creator registred! Wating for admin approval", category='success')
        songs=song.query.filter(song.cid==cid_exists.id).all()
        albums=Album.query.filter(Album.cid==cid_exists.id).all()
        return render_template("creatorhome.html",creator=cid_exists,songs=songs,albums=albums) 
    return redirect(url_for('auth.user'))

@view.route("/createsong",methods=['GET','POST'])
@login_required
def createsong():
    user=current_user
    cid_exists= Creator.query.filter(Creator.uid==user.id).first()
    if request.method=="POST":
        input_sname=request.form.get("sname")
        input_slyrics=request.form.get("slyrics")
        new_song=song(sname=input_sname,slyrics=input_slyrics,cid=cid_exists.id,doc=datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
        db.session.add(new_song)
        db.session.commit()
        input_afile=request.files["audiofile"]
        input_pfile=request.files["photofile"]
        if input_pfile and  allow_file(input_pfile.filename):
                filename="creator_"+str(cid_exists.id)+"song_coverphoto"+secure_filename(input_pfile.filename)
                input_pfile.save(os.path.join(view.root_path, 'static/song_coverphoto/', filename))
                input_url = "/static/song_coverphoto/" + filename
                new_song.scover_photo = input_url
                db.session.commit()
        if input_afile :
                filename="creator_"+str(cid_exists.id)+"_song_"+str(new_song.id)+secure_filename(input_afile.filename)
                input_afile.save(os.path.join(view.root_path, 'static/songs/', filename))
                input_url = "/static/songs/" + filename
                new_song.sfile = input_url
                db.session.commit()
        return redirect(url_for('home_views.creatorprofile'))
    return render_template("createsong.html",creator=cid_exists)

@view.route("/editsong",methods=['GET','POST'])
@login_required
def editsong():
    user=current_user
    cid_exists= Creator.query.filter(Creator.uid==user.id).first()
    if request.method=="POST" and cid_exists:
        input_sid=request.form.get("sid")
        input_edit=request.form.get("edit")
        input_delete=request.form.get("delete")
        input_sname=request.form.get("sname")
        input_slyrics=request.form.get("slyrics")
        if input_sname and input_slyrics:
            s=song.query.filter(song.id==input_sid).first()
            s.sname=input_sname
            s.slyrics=input_slyrics
            db.session.commit()
        if input_delete:
            s=song.query.filter(song.id==input_sid).first()
            db.session.delete(s)
            db.session.commit()
            return redirect(url_for('home_views.creatorprofile'))
        if input_edit:
            s=song.query.filter(song.id==input_sid).first()
            return render_template("editsong.html",song=s,creator=cid_exists)
    return redirect(url_for('home_views.creatorprofile'))


@view.route("/song/<sid>",methods=['GET','POST'])
@login_required
def songplay(sid):
    user=current_user
    s=song.query.filter(song.id==sid).all()
    if s:
        if 'user_type' in session:
            if session["user_type"] == "user":
                s=song.query.filter(song.id==sid).one()
                c=Creator.query.filter(Creator.id==s.cid).one()
                report_rate=s.flag_rate
                if request.method=="POST":
                    rate=request.form.get("rating") 
                    report=request.form.get("report")
                    old_rating=rating.query.filter(and_(rating.sid==sid,rating.uid==user.id)).first()
                    if report=="Report":
                        s.flag_rate=report_rate+1
                        
                    elif rate:
                        if old_rating:
                            old_rating.rating=rate
                        else:
                            new_rating=rating(rating=rate,sid=sid,uid=user.id)
                            db.session.add(new_rating)
                    db.session.commit()
                
                r=rating.query.filter(rating.sid==s.id).all()
                userrate=rating.query.filter(and_(rating.sid==sid,rating.uid==user.id)).first()
                
                return render_template("song.html",s=s,c=c,rating=r,user=user,userrate=userrate)
        return redirect(url_for('auth.user'))
    return redirect(url_for('home_views.userhome'))

@view.route("/createplaylist",methods=['GET','POST'])
@login_required
def createplaylist():
    user=current_user
    cid_exists= Creator.query.filter(Creator.uid==user.id).first()
    s=song.query.all()
    if request.method=="POST":
        input_pname=request.form.get("pname")
        input_songs=request.form.getlist("song")
        input_pfile=request.files["photofile"]
        input_privacy=request.form.get("privacy")
        new_playlist=Playlist(playlist_name=input_pname,uid=user.id,privacy=input_privacy,doc=datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
        db.session.add(new_playlist)
        db.session.commit()
        input_pid=new_playlist.id
        for sid in input_songs:
            new_songplaylist=SongPlaylist(pid=input_pid,sid=int(sid))
            db.session.add(new_songplaylist)
            db.session.commit()
        if input_pfile :
                filename="playlist_"+str(new_playlist.id)+"song_coverphoto"+secure_filename(input_pfile.filename)
                input_pfile.save(os.path.join(view.root_path, 'static/playlist_coverphoto/', filename))
                input_url = "/static/playlist_coverphoto/" + filename
                new_playlist.playlist_coverphoto = input_url
                db.session.commit()
                
        return redirect(url_for('home_views.userhome'))
        
    return render_template("createplaylist.html",creator=cid_exists,songs=s,user=user)

@view.route("/playlist/<pid>",methods=['GET','POST'])
@login_required
def playlistdisplay(pid):
    playlist=Playlist.query.filter(Playlist.id==pid).one()
    playlists=SongPlaylist.query.filter(SongPlaylist.pid==playlist.id).all()
    songs=[]
    user=User.query.filter(User.id==playlist.uid).one()
    cuser=current_user
    for p in playlists:
        sid=song.query.filter(song.id==p.sid).one()
        songs.append(sid)
    creator=Creator.query.all()
    if playlist.privacy==1 or (playlist.privacy==0 and playlist.uid==cuser.id):    
        return render_template("playlistdisplay.html",playlist=playlist,playlists=playlists,songs=songs,user=user,cuser=cuser,creator=creator)
    return redirect(url_for('home_views.userhome'))
@view.route("/editplaylist",methods=['GET','POST'])
@login_required
def editplaylist():
    user=current_user
    if request.method=='POST':
        input_pid=request.form.get("pid")
        input_flag=request.form.get("flag")
        input_delete=request.form.get("delete")
        report=request.form.get("report")
        if input_flag=="edit":
            current_playlist=Playlist.query.filter(Playlist.id==input_pid).one()
            playlists=SongPlaylist.query.filter(SongPlaylist.pid==input_pid).all()
            exsisting_songs=[]
            for p in playlists:
                sid=song.query.filter(song.id==p.sid).one()
                exsisting_songs.append(sid)
            songs=song.query.all()
            rem_songs=[]
            for e in songs:
                if e not in exsisting_songs:
                    rem_songs.append(e)
            return render_template("editplaylist.html",user=user,playlist=current_playlist,exsisting_songs=exsisting_songs,rem_songs=rem_songs)
        if input_delete=="delete":
            current_playlist=Playlist.query.filter(Playlist.id==input_pid).one()
            db.session.delete(current_playlist)
            db.session.commit()
            return redirect(url_for('home_views.userhome'))
        if report=="Report":
            current_playlist=Playlist.query.filter(Playlist.id==input_pid).one()
            current_playlist.flag_rate=current_playlist.flag_rate+1
            db.session.commit()
            return redirect(url_for('home_views.playlistdisplay',pid=input_pid))

        input_songs=request.form.getlist("song")
        input_privacy=request.form.get("privacy")

        if input_flag=="update":
            current_playlist=Playlist.query.filter(Playlist.id==input_pid).one()
            input_pname=request.form.get("pname")
            current_playlist.playlist_name=input_pname
            current_playlist.privacy=input_privacy
            playlists=SongPlaylist.query.filter(SongPlaylist.pid==input_pid).all()
            for p in playlists:
                db.session.delete(p)
                db.session.commit()
            for sid in input_songs:
                new_songplaylist=SongPlaylist(pid=input_pid,sid=int(sid))
                db.session.add(new_songplaylist)
                db.session.commit()
            return redirect(url_for('home_views.playlistdisplay',pid=input_pid))
    return redirect(url_for('home_views.userhome'))
    
@view.route("/createalbum",methods=['GET','POST'])
@login_required
def createalbum():
    user=current_user
    cid_exists= Creator.query.filter(Creator.uid==user.id).first()
    if cid_exists:
        if request.method=='POST':
            input_aname=request.form.get("aname")
            input_genre=request.form.get("genre")
            input_songs=request.form.getlist("song")
            input_pfile=request.files["photofile"]
            new_albul=Album(album_name=input_aname,genre=input_genre,cid=cid_exists.id,doc=datetime.datetime.now(pytz.timezone('Asia/Kolkata')))
            db.session.add(new_albul)
            db.session.commit()
            input_aid=new_albul.id
            for sid in input_songs:
                new_songplaylist=SongAlbum(aid=input_aid,sid=int(sid))
                db.session.add(new_songplaylist)
                db.session.commit()
            if input_pfile :
                filename="album_"+str(new_albul.id)+"album_coverphoto"+secure_filename(input_pfile.filename)
                input_pfile.save(os.path.join(view.root_path, 'static/album_coverphoto/', filename))
                input_url = "/static/album_coverphoto/" + filename
                new_albul.album_coverphoto = input_url
                db.session.commit()
            return redirect(url_for('home_views.creatorprofile'))
        s=song.query.filter(song.cid==cid_exists.id)
        return render_template("createalbum.html",creator=cid_exists,songs=s)
    else:
        flash('Register as creator first','error')
        return redirect(url_for("auth.creator"))

@view.route("album/<aid>",methods=['GET','POST'])
@login_required
def albumdisplay(aid):
    album=Album.query.filter(Album.id==aid).one()
    albums=SongAlbum.query.filter(SongAlbum.aid==album.id).all()
    songs=[]
    creator=Creator.query.filter(Creator.id==album.cid).one()
    cuser=current_user
    creators=Creator.query.all()
    for a in albums:
        sid=song.query.filter(song.id==a.sid).one()
        songs.append(sid)
    return render_template("albumdisplay.html",album=album,albums=albums,songs=songs,creator=creator,cuser=cuser,creators=creators)

@view.route("/editalbum",methods=['POST','GET'])
@login_required
def editalbum():
    user=current_user
    cid_exists= Creator.query.filter(Creator.uid==user.id).first()
    if request.method=='POST' and cid_exists:
        input_aid=request.form.get("aid")
        input_edit=request.form.get("edit")
        input_delete=request.form.get("delete")
        input_flag=request.form.get("flag")
        if input_edit=="Edit Album":
            current_album=Album.query.filter(Album.id==input_aid).first()
            albums=SongAlbum.query.filter(SongAlbum.aid==input_aid).all()
            exsisting_songs=[]
            for a in albums:
                sid=song.query.filter(song.id==a.sid).one()
                exsisting_songs.append(sid)
            songs=song.query.filter(song.cid==cid_exists.id).all()
            rem_songs=[]
            for e in songs:
                if e not in exsisting_songs:
                    rem_songs.append(e)
            return render_template("editalbum.html",album=current_album,creator=cid_exists,exsisting_songs=exsisting_songs,rem_songs=rem_songs)
        if input_delete=="Remove Album":
            current_album=Album.query.filter(Album.id==input_aid).one()
            db.session.delete(current_album)
            db.session.commit()
            return redirect(url_for('home_views.creatorprofile'))
        
        if input_flag=="update":
            input_songs=request.form.getlist("song")
            current_album=Album.query.filter(Album.id==input_aid).one()
            input_aname=request.form.get("aname")
            current_album.album_name=input_aname
            playlists=SongAlbum.query.filter(SongAlbum.aid==input_aid).all()
            for p in playlists:
                db.session.delete(p)
                db.session.commit()
            for sid in input_songs:
                new_songalbum=SongAlbum(aid=input_aid,sid=int(sid))
                db.session.add(new_songalbum)
                db.session.commit()
            return redirect(url_for('home_views.creatorprofile'))
        
    if request.method=='POST':
        input_aid=request.form.get("aid")
        report=request.form.get("report")
        if report=="Report":
            current_album=Album.query.filter(Album.id==input_aid).one()
            current_album.flag_rate=current_album.flag_rate+1
            db.session.commit()
            return redirect(url_for('home_views.albumdisplay',aid=input_aid))
    

@view.route("/search", methods=['POST'])
@login_required
def search():
    search = request.form.get("search")
    searchby=request.form.get("searchby")
    creator=Creator.query.all()
    cuser=current_user
    if searchby=='song':
        cre=Creator.query.filter(Creator.cname.like('%' + search + '%')).all()
        l=[]
        for c in cre:
            l.append(c.id)
        searched_song = song.query.filter(or_(Album.cid.in_(l),song.sname.like('%' + search + '%'))).all()
        return render_template("search.html",result=searched_song,searchby=searchby,user=cuser,search=search,creator=creator)
    elif searchby=='album':
        cre=Creator.query.filter(Creator.cname.like('%' + search + '%')).all()
        l=[]
        for c in cre:
            l.append(c.id)
        searched_album = Album.query.filter(or_(Album.cid.in_(l),Album.genre.like('%' + search + '%'),Album.album_name.like('%' + search + '%'))).all()
        return render_template("search.html",result=searched_album,searchby=searchby,user=cuser,search=search,creator=creator)
    elif searchby=='playlist':
        searched_playlist = Playlist.query.filter(Playlist.playlist_name.like('%' + search + '%')).all()
        alluser=User.query.all()
        return render_template("search.html",result=searched_playlist,searchby=searchby,alluser=alluser,user=cuser,search=search)
    
    return redirect(url_for('home_views.userhome'))
    

