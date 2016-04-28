import sqlite3,json


def insertionSort(alist):
    for index in range(1,len(alist)):
        currentvalue = alist[index]
        position = index
        while position>0 and int(alist[position-1][1])<int(currentvalue[1]):
            alist[position]=alist[position-1]
            position = position-1
        alist[position]=currentvalue

def get_score(u1,u2): #consider negative return as well
    print("u1 and u2 : "+u1+" "+u2)
    score = 0
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    d1 = cursor.execute("SELECT * FROM data WHERE user_id = ?",(u1,))
    d1 = d1.fetchall()
    #print ("D1 :> "+str(d1))
    d2 = cursor.execute("SELECT * FROM data WHERE user_id = ?",(u2,))
    
    d2 = d2.fetchall()
    #print("D1 and D2 : "+str(d1)+str(d2))
    for x in d1:
        for y in d2:
            if x[1] == y[1] and x[2] == y[2]:
                score += 1
    conn.close()
    return score


conn = sqlite3.connect('test.db')
cursor = conn.cursor()
'''
cursor.execute("DROP TABLE users")
cursor.execute("DROP TABLE songs")
cursor.execute("DROP TABLE data")

cursor.execute("CREATE table if not exists users(user_id text,name text,password text)")
cursor.execute("CREATE table if not exists songs(song_id text,name text,artist text,url text, votes)")
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

'''

x = cursor.execute("SELECT user_id from users where user_id != ?",("batman",))
x = cursor.fetchall()
#for i in x:
#    print(i)
conn.commit()
conn.close()

def testdb():
    #request.GET.get('uid','')
    uid = "batman"
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    users = cursor.execute("select user_id from users where user_id != ?",(uid,))
    users = cursor.fetchall()
    #dbg
    #print(users)
    min_score = 0

    similar_users = []

    for u in users:
        u = u[0]
        #dbg
        #print("User : "+u)
        score = get_score(uid,u)
        print("Score for "+u+" : "+str(score))
        if len(similar_users) < 20 or score >= min_score:
            min_score = min(min_score,score)
            similar_users.append((u,score))
            insertionSort(similar_users)
    print (similar_users)
    rec = []

    usongs = cursor.execute("select song_id from data where user_id = ?",(uid,))
    usongs = cursor.fetchall()
    for i in range(len(usongs)):
        usongs[i] = usongs[i][0]
    #print(usongs)
        

    for us in similar_users:
        if len(rec)>= 2 :
            break
        songs = cursor.execute("select song_id from data where user_id = ? and vote='1'",(us[0],))
        songs = songs.fetchall()
        for s in songs:
            if s[0] not in usongs:
                rec.append(s[0])

    conn.close()
    output = json.dumps(rec)
    return (output)

print("Recommeded : "+testdb())
