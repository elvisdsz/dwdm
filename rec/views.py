from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

import sqlite3
import json

database = "big.db"

# Create your views here.

def index(request):
    uid = request.GET.get('uid','user3')

    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    '''
    cursor.execute("DROP TABLE if exists users")
    cursor.execute("DROP TABLE if exists songs")
    cursor.execute("DROP TABLE if exists data")

    cursor.execute("CREATE table if not exists users(user_id text,name text,password text)")
    cursor.execute("CREATE table if not exists songs(song_id text,name text,artist text,url text, votes text)")
    cursor.execute("CREATE table if not exists data(user_id text, song_id text, vote text)")

    users = [('batman','Bruce','nananana'),
             ('mia','MK','mama'),
             ('jarjar','JB','binks'),
             ('joker','Joe','hahahaha')]

    songs = [('x1','lala','fakira','http://song1','0'),
             ('x2','jaja','print','http://song2','0'),
             ('x3','tata','dollar','http://song3','0'),
             ('x4','wawa','ra67','http://song4','0')]

    data = [('batman','x1','1'),
            ('batman','x2','1'),
            ('mia','x2','1'),
            ('jarjar','x2','1'),
            ('jarjar','xj','1'),
            ('jarjar','x1','1'),
            ('mia','xx','1'),
            ('joker','x1','1'),
            ('joker','x3','1'),
            ('joker','x2','1')]

    for x in users:
        cursor.execute("INSERT INTO users values(?,?,?)",x)

    for x in songs:
        cursor.execute("INSERT INTO songs values(?,?,?,?,?)",x)

    for x in data:
        cursor.execute("INSERT INTO data values(?,?,?)",x)
    conn.commit()
    '''

    users = cursor.execute("select user_id from users where user_id != ?",(uid,))
    users = cursor.fetchall()

    min_score = 0

    similar_users = []

    for u in users:
        u = u[0]
        score = get_score(uid,u)
        if len(similar_users) < 20 or score >= min_score:
            min_score = min(min_score,score)
            similar_users.append((u,score))
            insertionSort(similar_users)

    rec = []

    usongs = cursor.execute("select song_id from data where user_id = ?",(uid,))
    usongs = cursor.fetchall()
    for i in range(len(usongs)):
        usongs[i] = usongs[i][0]
    #print(usongs)

    for us in similar_users:
        if len(rec)>= 20 :
            break
        songs = cursor.execute("select song_id from data where user_id = ?",(us[0],))
        songs = songs.fetchall()
        for s in songs:
            if s[0] not in usongs and s[0] not in rec:
                rec.append(Song.get_song(s[0]))


    conn.close()
    #output = json.dumps(rec)
    #return HttpResponse(output)
    #return JsonResponse({'recommeded':rec})
    return render(request,'rec/home.html', {'recomm' : rec,'uid':uid})

class Song():
    def __init__(self,song_id,name,artist,url,votes=0):
        self.song_id = song_id
        self.name = name
        self.artist = artist
        self.url = url
        self.url = votes

    @staticmethod
    def get_song(sid):
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        x = cursor.execute("SELECT * FROM songs where song_id = ?",(sid,))
        row = x.fetchone()
        s = Song(row[0],row[1],row[2],row[3],row[4])
        conn.close()
        return s

def each(request):
    song_id = request.GET.get('sid','')
    uid = request.GET.get('uid','')
    song = Song.get_song(song_id)
    return render(request,'rec/other.html', {'song' : song,'uid':uid})

def vote(request):
    song_id = request.GET.get('sid','')
    uid = request.GET.get('uid','')
    vote = request.GET.get('vote','1')
    insert_data(uid,song_id,vote)

    '''
    insert_data('user43','song53','-1')
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    (uid,song_id,vote) = cursor.execute("SELECT * FROM data WHERE user_id = ? and song_id = ?",('user43','song53')).fetchone()
    conn.close()
    output = uid+song_id+vote
    return HttpResponse(output)
    '''
    
    url = "%s?uid=%s"%(reverse('rec:index'),uid)
    return HttpResponseRedirect(url)


def insert_data(uid,sid,vote):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    x = cursor.execute("SELECT * FROM data WHERE user_id = ? and song_id = ?",(uid,sid))
    y = x.fetchone()
    xs = cursor.execute("SELECT votes from songs where song_id = ?",(sid,))
    cur_votes = int(xs.fetchone()[0])
    if y != None:
        cursor.execute("UPDATE data SET vote = ? WHERE user_id = ? and song_id = ?",(str(vote),uid,sid))
        eff_votes = cur_votes - int(y[2]) + int(vote)
        cursor.execute("UPDATE songs SET votes = ? WHERE song_id = ?",(str(eff_votes),sid))
    else :
        cursor.execute("INSERT INTO data VALUES(?,?,?)",(uid,sid,vote))
        eff_votes = cur_votes + int(vote)
        cursor.execute("UPDATE songs SET votes = ? WHERE song_id = ?",(str(eff_votes),sid))
    conn.commit()
    conn.close()

def get_score(u1,u2): #consider negative return as well
    score = 0
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    d1 = cursor.execute("SELECT * FROM data WHERE user_id = ?",(u1,))
    d1 = d1.fetchall()
    d2 = cursor.execute("SELECT * FROM data WHERE user_id = ?",(u2,))
    d2 = d2.fetchall()
    for x in d1:
        for y in d2:
            if x[1] == y[1] and x[2] == y[2]:
                score += 1
    conn.close()
    return score



def insertionSort(alist):
    for index in range(1,len(alist)):
        currentvalue = alist[index]
        position = index
        while position>0 and int(alist[position-1][1])<int(currentvalue[1]):
            alist[position]=alist[position-1]
            position = position-1
        alist[position]=currentvalue


def uauth(request):
    uid = request.POST.get('uid','')
    password = request.POST.get('password','')
    
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    users = cursor.execute("select user_id from users where user_id = ? and password = ?",(uid,password))
    y = users.fetchone()
    conn.close()
    #return HttpResponse(print(y))
    
    if y==None:
        return render(request,'home.html')
    url = "%s?uid=%s"%(reverse('rec:index'),uid)
    return HttpResponseRedirect(url)
    
