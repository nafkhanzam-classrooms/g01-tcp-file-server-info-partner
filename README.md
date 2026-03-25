[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Acquirell Kriswanto               |    5025241035        |    D       |
|                |            |           |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```

```

## Penjelasan Program
### 1. server-sync.py
**Cara kerja:**<br>
`Server menggunakan standard "accept()" call untuk menunggu client untuk terkoneksi. Saat terkoneksi maka server akan masuk ke infinite while loop dan mendengarkan client tersebut secara ekslusif`

### 2. server-select.py
**Cara kerja:**<br>
`Server menggunakan "select" module, yang berkerja seperti switchboard. Server tidak hanya terjebak mendengarkan satu clien, namun server memiliki list semua client yang terkoneksi dan diberikan kepada sistem operasi dengan "select.select()". Sistem operasi monitor terus menerus dan terus mengembalikan list dari client yang mengirimkan data. Server kemudian meloop hanya pada client yang aktif, dan memproses pesan mereka dan kembali ke monitoring. `

### 3. server-poll.py
**Cara kerja:**<br>
`Server berkerja berfungsi hampir identik dengan server-select tapi ini menggunakan "select-poll()" system call daripada select.select(). Poll() hanya bisa dijalankan di Linux/WSL`

### 4. server-thread.py
**Cara kerja:**<br>
`Setiap kali client baru terkoneksi, server membuat thread baru, thread independent yang terdedikasi khusus kepada client tersebut. Sehingga server menghandle banyak client secara concurrent dengan cara membuat parallel mini-process (threads). Jadi semisal ada client yang mengupload file yang sangat besar maka hanya akan memblock personal thread tersebut dan client lain tidak terpengaruh.`

### 5. client.py
**Cara kerja:**<br>
`Inisialisasi: memulai koneksi dengan mengambil IP dan port, menggunakan TCP socked dan berkoenksi dengan server. Setiap client akan mempunyai client files yang unik dengan template client_files_XXXXX folder untuk download` <br>
`Thread:Setiap client menggunakan background thread "recieve_thread" yang digunakan untuk menunggu data.`<br>
* Jika server mengirim msg, maka akan diprint
* Jika server mengrim file, maka akan membaca file size dan download.
`Input Loop:`
*/list: mempacking JSON dictionary dengan command "list" dan mengirim ke server
*/upload filename.txt: cek apakah file exists, liat total size, kemudian mengirim JSON dictionary dengan command "upload" header.  Setelah header, buka filenya dan mengirimkan raw bytes melalui socket ke server.
*/download filename.txt: mempacking JSON dictionary dengan command "download" dan mengirim ke server.

### 

## Screenshot Hasil
### 1. server-sync.py
<img width="1041" height="248" alt="image" src="https://github.com/user-attachments/assets/3efcb134-67b2-44cf-a197-0a5440b0cb82" />
<br>
`server sync hanya mendengarkan satu client dan menolak koneksi client lain`
<br>
<br>
<img width="502" height="518" alt="image" src="https://github.com/user-attachments/assets/3b10a8e7-fcba-464a-bdc3-9323cb8fe5c2" />
`hasil /list, /download, /upload`
<br>
### 2. server-select.py
<img width="1569" height="214" alt="image" src="https://github.com/user-attachments/assets/ff926d62-b5fc-4166-927d-1d85f74e4cf8" />
`server select terhubung dengan 2 client`
<br>
<img width="1580" height="343" alt="image" src="https://github.com/user-attachments/assets/3131fb9a-afd3-4eaa-aaac-b3a92694c7a5" />
`server select menghandle 2 client yang berbeda`
<br>
<br>

### 3. server-poll.py
<img width="1266" height="235" alt="image" src="https://github.com/user-attachments/assets/6b3f3d12-4486-4647-bcad-ac3f9e1843ef" />

`server poll terhubung dengan 2 client`

<br>
<img width="1274" height="171" alt="image" src="https://github.com/user-attachments/assets/2831892d-773d-4320-9171-e5da4f800b5b" />

`server poll menghandle 2 client yang berbeda`

<br>
<br>

### 4. server-thread.py
<img width="1574" height="210" alt="image" src="https://github.com/user-attachments/assets/5d70e049-786b-429f-99f0-be842d1b8bc1" />

`server thread terhubung dengan 2 client`

<br>

<img width="1566" height="357" alt="image" src="https://github.com/user-attachments/assets/2db8e432-9dfc-4722-83d3-4cf90dd5b2f4" />

`server thread menghandle 2 client yang berbeda`
<br>

