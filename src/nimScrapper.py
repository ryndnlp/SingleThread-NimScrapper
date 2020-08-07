import firebase_admin
import requests
import json
from firebase_admin import credentials
from firebase_admin import db
from pyquery import PyQuery as pq

# Get list of jurusan
kode_jurusan = []
with open('list-jurusan.json') as json_file_jurusan:
    data_jurusan = json.load(json_file_jurusan)
    for dj in data_jurusan:
        kode_jurusan.append(dj)

# Get list of fakultas
kode_fakultas = []
with open('list-fakultas.json') as json_file_fakultas:
    data_fakultas = json.load(json_file_fakultas)
    for df in data_fakultas:
        kode_fakultas.append(df)

tahun = ['14', '15', '16', '17', '18', '19'] # TODO Change to which year u want to scrap

# Setup posting to firebase
cred = credentials.Certificate(your_firebase_sdk) # TODO Change to your Admin SDK config file name 
firebase_admin.initialize_app(cred, {
    'databaseURL' : your_firebase_url # TODO Change to your firebase URL
})

# Setup web scraping
url = 'https://nic.itb.ac.id/manajemen-akun/pengecekan-user'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'} # TODO Change to your headers
cookies = your_cookies #TODO

# Process web scraping
max_mahasiswa_fakultas = 600
max_error = 120
s = requests.Session()
def scrape(jurusan, angkatan):
    data_nim = {'data': []}
    error = 0
    for i in range(1, max_mahasiswa_fakultas):
        try: 
            uniq = i
            if(uniq // 10 == 0):
                uniq = '00' + str(uniq)
            elif(uniq // 100 == 0):
                uniq = '0' + str(uniq)
            else:
                uniq = str(uniq)
            uid = jurusan + angkatan + uniq
            data = {'uid': uid}
            res = s.post(url, data=data, cookies=cookies)
            res_queried = pq(res.text)
            tabel = res_queried('#tabel')
            content = tabel.text().splitlines()
            temp = content[5].split(', ')
            if(len(temp) == 2): # NIM jurusan exist
                obj = {'name': content[8], 'tpb': temp[0], 'jurusan': temp[1]}
            else:
                obj = {'name': content[8], 'tpb': temp[0], 'jurusan': None}
            data_nim['data'].append(obj)
            print(obj)
        except Exception as e:
            if(str(e) == 'list index out of range'):
                if(error != max_error):
                    error += 1
                    print('Checking availability of ' + uid)
                    pass
                else:
                    print('Done processing ' + jurusan + angkatan)
                    break
            else:
                print(e)
    return data_nim

def scrapeAll():
    for kf in kode_fakultas:
        for t in tahun:
            try:
                data_nim_jurusan_tahun = scrape(kf, t)
                ref = db.reference(path='/' + kf + '/' + t) # Change to the path where you want to post
                ref.set(data_nim_jurusan_tahun)
                print('Done posting to firebase.')
            except Exception as e:
                print(e)

# To local file 
# with open('data.txt' , 'w') as outfile:
#     json.dump(data, outfile)

if __name__ == "__main__":
    scrapeAll()

