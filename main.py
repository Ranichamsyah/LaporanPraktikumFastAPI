# conda activate webservicep2plending webservicep2plending
# uvicorn main:app --reload

from typing import Union  # Import Union untuk mendefinisikan tipe data gabungan
from fastapi import FastAPI, Response, Request, HTTPException  # Import modul FastAPI dan kelas-kelas yang diperlukan
from fastapi.middleware.cors import CORSMiddleware  # Import middleware CORSMiddleware untuk menangani CORS
import sqlite3  # Import modul sqlite3 untuk berinteraksi dengan database SQLite

app = FastAPI()  # Inisialisasi objek FastAPI sebagai aplikasi

app.add_middleware(  # Menambahkan middleware CORS untuk menangani CORS (Cross-Origin Resource Sharing)
    CORSMiddleware,  # Menggunakan CORSMiddleware
    allow_origins=["*"],  # Mengizinkan semua asal permintaan (origin) dengan tanda "*" sebagai wildcard
    allow_credentials=True,  # Mengizinkan pengiriman kredensial melalui CORS
    allow_methods=["*"],  # Mengizinkan semua metode HTTP (GET, POST, PUT, dll.)
    allow_headers=["*"],  # Mengizinkan semua header dalam permintaan
)


@app.get("/")  # Mendefinisikan endpoint untuk permintaan GET pada akar (root) URL
def read_root():  # Fungsi yang akan dipanggil saat permintaan GET diterima pada akar URL
    return {"Hello": "World"}  # Mengembalikan respons JSON dengan pesan "Hello World"

@app.get("/mahasiswa/{nim}")  # Mendefinisikan endpoint untuk permintaan GET dengan parameter "nim" pada URL "/mahasiswa/{nim}"
def ambil_mhs(nim:str):  # Fungsi yang akan dipanggil saat permintaan GET diterima pada URL "/mahasiswa/{nim}"
    return {"nama": "Budi Martami"}  # Mengembalikan respons JSON dengan nama mahasiswa

@app.get("/mahasiswa2/")  # Mendefinisikan endpoint untuk permintaan GET pada URL "/mahasiswa2/"
def ambil_mhs2(nim:str):  # Fungsi yang akan dipanggil saat permintaan GET diterima pada URL "/mahasiswa2/"
    return {"nama": "Budi Martami 2"}  # Mengembalikan respons JSON dengan nama mahasiswa 2

@app.get("/daftar_mhs/")  # Mendefinisikan endpoint untuk permintaan GET pada URL "/daftar_mhs/"
def daftar_mhs(id_prov:str,angkatan:str):  # Fungsi yang akan dipanggil saat permintaan GET diterima pada URL "/daftar_mhs/"
    return {"query": " idprov: {}; angkatan: {} ".format(id_prov, angkatan),  # Mengembalikan respons JSON dengan query dan data mahasiswa
            "data": [{"nim": "1234"}, {"nim": "1235"}]}  # Data mahasiswa yang disertakan dalam respons


# panggil sekali saja
@app.get("/init/")
def init_db():
  try:
    DB_NAME = "upi.db" # Nama database yang akan dibuat atau diinisialisasi
    con = sqlite3.connect(DB_NAME) # Membuat koneksi ke database SQLite
    cur = con.cursor() # Membuat kursor untuk eksekusi perintah SQL
      # Membuat perintah SQL untuk membuat tabel 'mahasiswa' jika belum ada
    create_table = """ CREATE TABLE mahasiswa(
            ID      	INTEGER PRIMARY KEY 	AUTOINCREMENT,
            nim     	TEXT            	NOT NULL,
            nama    	TEXT            	NOT NULL,
            id_prov 	TEXT            	NOT NULL,
            angkatan	TEXT            	NOT NULL,
            tinggi_badan  INTEGER
        )  
        """
    cur.execute(create_table) # Menjalankan perintah SQL untuk membuat tabel
    con.commit # Melakukan commit untuk menyimpan perubahan ke dalam database
  except:
           return ({"status":"terjadi error"})  # Mengembalikan pesan error jika terjadi kesalahan
  finally:
           con.close() # Menutup koneksi ke database
    
  return ({"status":"ok, db dan tabel berhasil dicreate"})  # Mengembalikan pesan sukses jika operasi berhasil

from pydantic import BaseModel  # Mengimpor kelas BaseModel dari modul pydantic untuk membuat model data

from typing import Optional  # Mengimpor tipe data Optional untuk memungkinkan nilai yang dapat null atau kosong

class Mhs(BaseModel):  # Mendefinisikan kelas Mhs sebagai subkelas dari BaseModel
   nim: str  # Mendefinisikan atribut nim dengan tipe data string
   nama: str  # Mendefinisikan atribut nama dengan tipe data string
   id_prov: str  # Mendefinisikan atribut id_prov dengan tipe data string
   angkatan: str  # Mendefinisikan atribut angkatan dengan tipe data string
   tinggi_badan: Optional[int] | None = None  # Mendefinisikan atribut tinggi_badan dengan tipe data opsional yang dapat berupa integer atau None

# status code 201 standard return creation
# return objek yang baru dicreate (response_model tipenya Mhs)

@app.post("/tambah_mhs/", response_model=Mhs, status_code=201)  # Mendefinisikan endpoint untuk menambahkan data mahasiswa dengan menggunakan metode POST
def tambah_mhs(m: Mhs, response: Response, request: Request):  # Mendefinisikan fungsi tambah_mhs dengan parameter m (objek Mhs), response, dan request
   try:
       DB_NAME = "upi.db"  # Nama database SQLite
       con = sqlite3.connect(DB_NAME)  # Membuat koneksi ke database SQLite
       cur = con.cursor()  # Membuat kursor untuk eksekusi perintah SQL

       # Menjalankan perintah SQL untuk menambahkan data mahasiswa ke dalam tabel 'mahasiswa'
       cur.execute("""INSERT INTO mahasiswa (nim, nama, id_prov, angkatan, tinggi_badan) VALUES ("{}", "{}", "{}", "{}", {})""".format(m.nim, m.nama, m.id_prov, m.angkatan, m.tinggi_badan))
       con.commit()  # Melakukan commit untuk menyimpan perubahan ke dalam database

   except:
       print("oioi error")  # Menampilkan pesan kesalahan jika terjadi error
       return ({"status": "terjadi error"})  # Mengembalikan pesan error jika terjadi kesalahan

   finally:
       con.close()  # Menutup koneksi ke database setelah selesai

   response.headers["Location"] = "/mahasiswa/{}".format(m.nim)  # Menetapkan header Location untuk respons dengan URL mahasiswa yang baru ditambahkan
   print(m.nim)  # Mencetak NIM mahasiswa yang baru ditambahkan ke konsol
   print(m.nama)  # Mencetak nama mahasiswa yang baru ditambahkan ke konsol
   print(m.angkatan)  # Mencetak angkatan mahasiswa yang baru ditambahkan ke konsol

   return m  # Mengembalikan objek mahasiswa yang baru ditambahkan sebagai respons


@app.get("/tampilkan_semua_mhs/")  # Mendefinisikan endpoint untuk menampilkan semua data mahasiswa dengan menggunakan metode GET
def tampil_semua_mhs():  # Mendefinisikan fungsi untuk menampilkan semua data mahasiswa
   try:
       DB_NAME = "upi.db"  # Nama database SQLite
       con = sqlite3.connect(DB_NAME)  # Membuat koneksi ke database SQLite
       cur = con.cursor()  # Membuat kursor untuk eksekusi perintah SQL
       recs = []  # Membuat daftar kosong untuk menyimpan hasil query

       # Melakukan iterasi dan menambahkan setiap baris data dari hasil query ke dalam daftar recs
       for row in cur.execute("SELECT * FROM mahasiswa"):
           recs.append(row)

   except:
       return ({"status": "terjadi error"})  # Mengembalikan pesan error jika terjadi kesalahan

   finally:
       con.close()  # Menutup koneksi ke database

   return {"data": recs}  # Mengembalikan data mahasiswa dalam bentuk respons JSON

from fastapi.encoders import jsonable_encoder


@app.put("/update_mhs_put/{nim}", response_model=Mhs)
def update_mhs_put(response: Response, nim: str, m: Mhs):
    # Mendefinisikan endpoint untuk melakukan pembaruan data mahasiswa berdasarkan NIM
    # Endpoint ini menggunakan metode PUT karena akan mengupdate keseluruhan data mahasiswa
    # Response_model digunakan untuk menentukan respons yang diharapkan dari endpoint ini

    # Membuat koneksi ke database
    try:
        DB_NAME = "upi.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("select * from mahasiswa where nim = ?", (nim,))
        existing_item = cur.fetchone()
    except Exception as e:
        # Menangani exception jika terjadi kesalahan dalam koneksi atau eksekusi query
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))

    if existing_item:
        # Jika data mahasiswa dengan NIM yang diberikan ditemukan

        # Melakukan pembaruan data mahasiswa
        cur.execute("update mahasiswa set nama = ?, id_prov = ?, angkatan=?, tinggi_badan=? where nim=?", 
                    (m.nama, m.id_prov, m.angkatan, m.tinggi_badan, nim))
        con.commit()

        # Menetapkan header lokasi untuk respons
        response.headers["location"] = "/mahasiswa/{}".format(m.nim)
    else:
        # Jika data mahasiswa dengan NIM yang diberikan tidak ditemukan
        print("item not found")
        raise HTTPException(status_code=404, detail="Item Not Found")

    # Menutup koneksi ke database
    con.close()

    # Mengembalikan data mahasiswa yang telah diperbarui
    return m


# khusus untuk patch, jadi boleh tidak ada
# menggunakan "kosong" dan -9999 supaya bisa membedakan apakah tdk diupdate ("kosong") atau mau
# diupdate dengan dengan None atau 0
class MhsPatch(BaseModel):
   nama: str | None = "kosong"
   id_prov: str | None = "kosong"
   angkatan: str | None = "kosong"
   tinggi_badan: Optional[int] | None = -9999  # yang boleh null hanya ini



@app.patch("/update_mhs_patch/{nim}", response_model=MhsPatch)  # Mendefinisikan endpoint untuk memperbarui data mahasiswa dengan menggunakan metode PATCH
def update_mhs_patch(response: Response, nim: str, m: MhsPatch):  # Mendefinisikan fungsi untuk memperbarui data mahasiswa dengan parameter nim, m (objek MhsPatch), dan response
    try:
        DB_NAME = "upi.db"  # Nama database SQLite
        con = sqlite3.connect(DB_NAME)  # Membuat koneksi ke database SQLite
        cur = con.cursor()  # Membuat kursor untuk eksekusi perintah SQL

        # Menjalankan perintah SQL untuk mengambil data mahasiswa dengan NIM tertentu
        cur.execute("SELECT * FROM mahasiswa WHERE nim = ?", (nim,))  # Menambahkan koma untuk menandakan tupel pada parameter
        existing_item = cur.fetchone()  # Mengambil satu baris hasil query

    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))  # Menangani kesalahan dan mengembalikan respons dengan status code 500 jika terjadi kesalahan, misalnya database down

    if existing_item:  # Jika data mahasiswa dengan NIM yang diberikan ditemukan
        sqlstr = "UPDATE mahasiswa SET "  # Membuat perintah SQL untuk memperbarui data mahasiswa

        # Memperbarui setiap kolom data mahasiswa yang diubah
        if m.nama != "kosong":
            if m.nama is not None:
                sqlstr = sqlstr + " nama = '{}' ,".format(m.nama)
            else:
                sqlstr = sqlstr + " nama = null ,"

        if m.angkatan != "kosong":
            if m.angkatan is not None:
                sqlstr = sqlstr + " angkatan = '{}' ,".format(m.angkatan)
            else:
                sqlstr = sqlstr + " angkatan = null ,"

        if m.id_prov != "kosong":
            if m.id_prov is not None:
                sqlstr = sqlstr + " id_prov = '{}' ,".format(m.id_prov)
            else:
                sqlstr = sqlstr + " id_prov = null, "

        if m.tinggi_badan != -9999:
            if m.tinggi_badan is not None:
                sqlstr = sqlstr + " tinggi_badan = {} ,".format(m.tinggi_badan)
            else:
                sqlstr = sqlstr + " tinggi_badan = null ,"

        sqlstr = sqlstr[:-1] + " WHERE nim='{}' ".format(nim)  # Menghapus koma terakhir dan menambahkan kondisi WHERE berdasarkan NIM

        try:
            cur.execute(sqlstr)  # Menjalankan perintah SQL untuk memperbarui data mahasiswa
            con.commit()  # Melakukan commit untuk menyimpan perubahan ke dalam database

            response.headers["location"] = "/mahasixswa/{}".format(nim)  # Menetapkan header Location untuk respons dengan URL mahasiswa yang telah diperbarui

        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))  # Menangani kesalahan dan mengembalikan respons dengan status code 500 jika terjadi kesalahan

    else:  # Jika data mahasiswa dengan NIM yang diberikan tidak ditemukan
         raise HTTPException(status_code=404, detail="Item Not Found")  # Mengembalikan respons dengan status code 404 (Not Found)

    con.close()  # Menutup koneksi ke database
    return m  # Mengembalikan objek mahasiswa yang telah diperbarui sebagai respons

  
    
@app.delete("/delete_mhs/{nim}")  # Mendefinisikan endpoint untuk menghapus data mahasiswa dengan menggunakan metode DELETE
def delete_mhs(nim: str):  # Mendefinisikan fungsi untuk menghapus data mahasiswa dengan parameter nim
    try:
        DB_NAME = "upi.db"  # Nama database SQLite
        con = sqlite3.connect(DB_NAME)  # Membuat koneksi ke database SQLite
        cur = con.cursor()  # Membuat kursor untuk eksekusi perintah SQL

        # Membuat perintah SQL untuk menghapus data mahasiswa berdasarkan NIM
        sqlstr = "DELETE FROM mahasiswa WHERE nim='{}'".format(nim)
        print(sqlstr)  # Debugging: mencetak perintah SQL ke konsol

        cur.execute(sqlstr)  # Menjalankan perintah SQL untuk menghapus data mahasiswa
        con.commit()  # Melakukan commit untuk menyimpan perubahan ke dalam database

    except:
        return ({"status": "terjadi error"})  # Mengembalikan pesan error jika terjadi kesalahan

    finally:
        con.close()  # Menutup koneksi ke database

    return {"status": "ok"}  # Mengembalikan pesan sukses setelah data mahasiswa berhasil dihapus



