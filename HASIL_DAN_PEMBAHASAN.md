# BAB IV
# HASIL DAN PEMBAHASAN

## 4.1 Gambaran Umum Pengujian

Pada penelitian atau proyek ini dilakukan pengujian terhadap tiga algoritma kompresi citra pada format HEIC. Ketiga algoritma yang dibandingkan adalah **HEVC Quality Reduction**, **Chroma Subsampling**, dan **Color Quantization**. Tujuan utama dari pengujian ini adalah untuk mengetahui perbedaan karakteristik masing-masing algoritma dalam mengurangi ukuran file citra, menjaga kualitas visual gambar, serta melihat waktu pemrosesan yang dibutuhkan.

Format HEIC dipilih karena format ini menggunakan teknologi kompresi modern berbasis HEVC atau H.265. Dibandingkan format gambar konvensional seperti JPEG, HEIC umumnya mampu menghasilkan ukuran file yang lebih kecil dengan kualitas visual yang tetap baik. Namun, tingkat efisiensi kompresi tetap dipengaruhi oleh metode yang digunakan, parameter kompresi, dan karakteristik gambar yang diproses.

Pengujian dilakukan menggunakan aplikasi berbasis Python yang telah dibuat. Aplikasi menyediakan fitur untuk memuat gambar HEIC, memilih algoritma kompresi, mengatur parameter, menampilkan pratinjau gambar asli dan gambar hasil kompresi, serta menampilkan metrik evaluasi. Selain itu, aplikasi juga menyediakan fitur perbandingan tiga algoritma secara langsung sehingga hasil setiap algoritma dapat dianalisis dalam satu tabel.

Secara umum, proses pengujian dilakukan melalui tahapan berikut:

1. Gambar HEIC dimuat ke dalam aplikasi.
2. Gambar asli dikonversi ke bentuk array RGB agar dapat diproses dan dibandingkan.
3. Setiap algoritma kompresi dijalankan dengan parameter tertentu.
4. Gambar hasil kompresi disimpan kembali dalam format HEIC.
5. Ukuran file asli dan ukuran file hasil kompresi dihitung.
6. Kualitas gambar hasil kompresi dibandingkan dengan gambar asli menggunakan metrik PSNR, SSIM, dan MSE.
7. Hasil pengujian ditampilkan pada tabel aplikasi dan dapat diekspor ke file CSV.

## 4.2 Algoritma yang Diuji

### 4.2.1 HEVC Quality Reduction

HEVC Quality Reduction adalah algoritma kompresi yang bekerja dengan cara mengubah nilai kualitas penyimpanan gambar HEIC. Pada implementasi program, gambar dibuka menggunakan library Pillow, kemudian disimpan ulang dalam format HEIF dengan parameter `quality`.

Parameter utama pada algoritma ini adalah nilai kualitas, misalnya `quality=10`, `quality=50`, atau `quality=90`. Semakin kecil nilai kualitas, semakin besar tingkat kompresi yang dilakukan. Akibatnya, ukuran file hasil kompresi menjadi lebih kecil. Namun, apabila nilai kualitas terlalu rendah, detail gambar dapat berkurang dan artefak kompresi dapat terlihat.

Kode inti algoritma ini terdapat pada file `src/algorithms/hevc_quality.py`. Prosesnya relatif sederhana karena tidak melakukan manipulasi piksel secara manual. Program hanya membaca gambar, lalu menyimpannya kembali dengan nilai kualitas yang berbeda.

### 4.2.2 Chroma Subsampling

Chroma Subsampling adalah metode kompresi yang mengurangi informasi warna pada citra. Metode ini memanfaatkan fakta bahwa mata manusia lebih sensitif terhadap perubahan kecerahan dibandingkan perubahan warna. Oleh karena itu, informasi luminance atau kecerahan tetap dipertahankan, sedangkan informasi chrominance atau warna dapat dikurangi.

Pada implementasi program, gambar RGB dikonversi ke ruang warna YCrCb. Komponen Y menyimpan informasi kecerahan, sedangkan Cr dan Cb menyimpan informasi warna. Setelah itu, komponen Cr dan Cb diperkecil sesuai jenis subsampling yang dipilih, kemudian diperbesar kembali ke ukuran semula.

Jenis subsampling yang digunakan pada program adalah:

| Jenis Subsampling | Karakteristik |
|---|---|
| 4:4:4 | Tidak mengurangi resolusi warna, sehingga kualitas warna paling terjaga |
| 4:2:2 | Mengurangi resolusi warna secara horizontal |
| 4:2:0 | Mengurangi resolusi warna secara horizontal dan vertikal |

Metode 4:2:0 menghasilkan pengurangan informasi warna yang lebih besar dibandingkan 4:2:2. Oleh karena itu, 4:2:0 berpotensi menghasilkan ukuran file lebih kecil, tetapi juga memiliki risiko penurunan kualitas warna yang lebih tinggi.

### 4.2.3 Color Quantization

Color Quantization adalah metode kompresi yang mengurangi jumlah warna pada gambar. Pada program ini, Color Quantization dilakukan menggunakan algoritma K-Means clustering. Setiap piksel pada gambar dianggap sebagai data dengan tiga komponen warna, yaitu merah, hijau, dan biru. K-Means kemudian mengelompokkan piksel-piksel tersebut ke dalam sejumlah kelompok warna tertentu.

Setelah proses clustering selesai, setiap piksel diganti dengan warna pusat kelompok atau centroid terdekat. Dengan cara ini, gambar hasil kompresi hanya menggunakan sejumlah warna yang lebih sedikit dibandingkan gambar asli.

Parameter utama pada algoritma ini adalah jumlah warna, misalnya `n_colors=4`, `n_colors=16`, atau `n_colors=64`. Semakin sedikit jumlah warna yang digunakan, semakin sederhana informasi warna pada gambar. Hal ini dapat membantu mengurangi ukuran file, tetapi juga dapat menyebabkan hilangnya gradasi warna dan detail visual.

## 4.3 Metrik Evaluasi

Untuk menilai hasil kompresi, digunakan beberapa metrik evaluasi. Metrik ini dibagi menjadi dua kelompok, yaitu metrik kompresi dan metrik kualitas gambar.

### 4.3.1 Original Size

Original Size adalah ukuran file gambar sebelum dilakukan kompresi. Nilai ini digunakan sebagai acuan untuk menghitung efektivitas kompresi. Semakin besar ukuran file asli, semakin besar pula peluang pengurangan ukuran file setelah kompresi.

### 4.3.2 Compressed Size

Compressed Size adalah ukuran file setelah gambar diproses menggunakan algoritma kompresi. Nilai ini menjadi indikator utama keberhasilan kompresi. Semakin kecil nilai Compressed Size, semakin besar penghematan ruang penyimpanan yang diperoleh.

### 4.3.3 Compression Ratio

Compression Ratio menunjukkan perbandingan antara ukuran file asli dan ukuran file hasil kompresi. Rumus yang digunakan adalah:

```text
Compression Ratio = Original Size / Compressed Size
```

Semakin besar nilai Compression Ratio, semakin baik kemampuan algoritma dalam mengecilkan ukuran file. Contohnya, compression ratio 2 berarti file asli berukuran dua kali lebih besar daripada file hasil kompresi.

### 4.3.4 Space Savings

Space Savings menunjukkan persentase penghematan ruang penyimpanan setelah kompresi. Rumus yang digunakan adalah:

```text
Space Savings = (1 - Compressed Size / Original Size) x 100%
```

Semakin besar nilai Space Savings, semakin besar pengurangan ukuran file yang berhasil dicapai.

### 4.3.5 Bits Per Pixel

Bits Per Pixel atau BPP menunjukkan jumlah bit yang dibutuhkan untuk merepresentasikan satu piksel pada gambar hasil kompresi. Nilai BPP dihitung berdasarkan ukuran file hasil kompresi dan jumlah piksel gambar.

```text
BPP = (Compressed Size x 8) / Jumlah Piksel
```

Semakin kecil nilai BPP, semakin efisien penyimpanan gambar. Namun, nilai BPP yang terlalu kecil dapat menunjukkan adanya penurunan informasi visual.

### 4.3.6 PSNR

PSNR atau Peak Signal-to-Noise Ratio digunakan untuk mengukur tingkat kemiripan gambar hasil kompresi terhadap gambar asli. Nilai PSNR dinyatakan dalam satuan desibel. Semakin tinggi nilai PSNR, semakin baik kualitas gambar hasil kompresi.

Jika nilai PSNR tinggi, berarti perbedaan antara gambar asli dan gambar hasil kompresi relatif kecil. Sebaliknya, jika nilai PSNR rendah, berarti terdapat perbedaan piksel yang cukup besar antara gambar asli dan gambar hasil kompresi.

### 4.3.7 SSIM

SSIM atau Structural Similarity Index digunakan untuk mengukur kemiripan struktur visual antara gambar asli dan gambar hasil kompresi. Nilai SSIM berada pada rentang 0 sampai 1. Nilai yang mendekati 1 menunjukkan bahwa gambar hasil kompresi masih sangat mirip dengan gambar asli.

SSIM sering dianggap lebih representatif terhadap persepsi manusia dibandingkan MSE karena metrik ini memperhatikan struktur, kontras, dan luminance gambar.

### 4.3.8 MSE

MSE atau Mean Squared Error menghitung rata-rata kuadrat selisih nilai piksel antara gambar asli dan gambar hasil kompresi. Semakin kecil nilai MSE, semakin kecil perbedaan antara kedua gambar.

Berbeda dengan PSNR dan SSIM, MSE memiliki arah interpretasi terbalik. Nilai MSE yang rendah menunjukkan kualitas yang lebih baik, sedangkan nilai MSE yang tinggi menunjukkan kualitas yang lebih buruk.

### 4.3.9 Processing Time

Processing Time menunjukkan waktu yang dibutuhkan algoritma untuk melakukan proses kompresi. Metrik ini penting karena algoritma yang menghasilkan kualitas baik tetapi membutuhkan waktu terlalu lama belum tentu efisien untuk digunakan pada aplikasi nyata.

## 4.4 Hasil Pengujian

Pengujian dapat dilakukan melalui dua mode pada aplikasi, yaitu mode **Single Algorithm** dan mode **Compare 3 Algorithms**. Pada mode Single Algorithm, pengguna dapat memilih satu algoritma dan melihat hasilnya secara individual. Pada mode Compare 3 Algorithms, aplikasi menjalankan ketiga algoritma sekaligus pada gambar yang sama sehingga hasilnya dapat dibandingkan secara langsung.

Parameter default yang digunakan pada mode perbandingan adalah sebagai berikut:

| Algoritma | Parameter |
|---|---|
| HEVC Quality Reduction | Quality = 10 |
| Chroma Subsampling | 4:2:0 |
| Color Quantization | 4 warna |

Tabel berikut merupakan format hasil pengujian yang digunakan oleh aplikasi. Nilai aktual dapat diperoleh dari tabel aplikasi atau dari file CSV hasil export.

| Algoritma | Parameter | Time (s) | Original Size | Compressed Size | Ratio | Space Save (%) | BPP | PSNR | SSIM | MSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HEVC Quality Reduction | 10 | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Chroma Subsampling | 4:2:0 | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| Color Quantization | 4 warna | ... | ... | ... | ... | ... | ... | ... | ... | ... |

Walaupun nilai numerik dapat berbeda tergantung gambar yang diuji, kecenderungan hasil dari ketiga algoritma dapat dianalisis berdasarkan cara kerja masing-masing algoritma. HEVC Quality Reduction umumnya menghasilkan ukuran file yang kecil dengan waktu pemrosesan cepat. Chroma Subsampling menghasilkan perubahan visual yang relatif ringan pada gambar natural karena hanya mengurangi informasi warna. Color Quantization dapat mengurangi kompleksitas warna secara signifikan, tetapi kualitas visualnya sangat bergantung pada jumlah warna yang dipilih.

## 4.5 Pembahasan Hasil HEVC Quality Reduction

Berdasarkan cara kerja algoritmanya, HEVC Quality Reduction menjadi metode yang paling sederhana dan praktis. Algoritma ini tidak mengubah struktur piksel secara manual, tetapi menyerahkan proses kompresi kepada encoder HEIC melalui parameter kualitas. Oleh karena itu, metode ini sangat cocok digunakan untuk kebutuhan kompresi umum.

Ketika nilai kualitas diturunkan, ukuran file hasil kompresi akan ikut menurun. Hal ini terjadi karena encoder mengurangi detail informasi gambar agar file dapat disimpan dengan ukuran yang lebih kecil. Pada nilai kualitas rendah, compression ratio dan space savings biasanya meningkat. Namun, konsekuensinya adalah kualitas gambar dapat menurun.

Dari sisi kualitas visual, penurunan nilai kualitas dapat menyebabkan munculnya artefak kompresi, detail halus berkurang, dan tekstur gambar menjadi kurang tajam. Hal ini akan terlihat pada nilai PSNR yang menurun, SSIM yang semakin jauh dari 1, dan MSE yang meningkat.

Keunggulan utama algoritma ini adalah kecepatan dan kemudahannya. Karena proses utama dilakukan oleh encoder HEIF, waktu pemrosesan relatif singkat. Algoritma ini juga mudah dikontrol karena hanya membutuhkan satu parameter utama, yaitu nilai kualitas.

Dengan demikian, HEVC Quality Reduction dapat dikatakan sebagai algoritma yang paling seimbang untuk kebutuhan kompresi umum. Metode ini cocok digunakan apabila pengguna ingin mengecilkan ukuran file secara cepat tanpa melakukan pengolahan citra yang kompleks.

## 4.6 Pembahasan Hasil Chroma Subsampling

Chroma Subsampling menghasilkan kompresi dengan cara mengurangi detail warna, bukan detail kecerahan. Pada gambar, informasi kecerahan biasanya lebih penting bagi persepsi manusia dibandingkan informasi warna. Oleh karena itu, pengurangan resolusi warna sering kali tidak terlalu terlihat secara visual, terutama pada gambar natural seperti foto pemandangan, wajah, atau objek sehari-hari.

Pada pengaturan 4:2:0, komponen warna Cr dan Cb diperkecil menjadi setengah ukuran secara horizontal dan vertikal. Setelah itu, komponen warna diperbesar kembali agar dapat digabungkan dengan komponen Y. Proses ini menyebabkan sebagian detail warna hilang, tetapi struktur utama gambar tetap dipertahankan karena komponen Y tidak dikurangi.

Jika dilihat dari metrik kualitas, Chroma Subsampling dapat mempertahankan nilai SSIM yang cukup baik apabila struktur gambar tidak berubah secara signifikan. Hal ini karena SSIM lebih memperhatikan kemiripan struktur dibandingkan sekadar perbedaan nilai piksel. Namun, PSNR dapat menurun apabila perubahan warna cukup besar, dan MSE dapat meningkat karena nilai piksel hasil kompresi berbeda dari gambar asli.

Kelebihan dari metode ini adalah kemampuannya menjaga bentuk dan struktur gambar. Pada banyak kasus, mata manusia tidak langsung menyadari perubahan warna kecil akibat subsampling. Oleh karena itu, Chroma Subsampling sering digunakan pada sistem kompresi gambar dan video.

Namun, metode ini juga memiliki kelemahan. Pada gambar dengan teks, garis berwarna tajam, ilustrasi vektor, atau batas warna yang kontras, Chroma Subsampling dapat menyebabkan warna terlihat bergeser atau tepi objek menjadi kurang tajam. Hal ini terjadi karena informasi warna di sekitar batas objek mengalami penurunan resolusi.

Berdasarkan hasil tersebut, Chroma Subsampling cocok digunakan untuk gambar natural atau foto, tetapi perlu hati-hati jika digunakan pada gambar yang mengandung teks, logo, diagram, atau elemen grafis dengan warna tajam.

## 4.7 Pembahasan Hasil Color Quantization

Color Quantization bekerja dengan mengurangi jumlah warna yang digunakan dalam citra. Pada implementasi program, metode ini menggunakan K-Means clustering. Semua piksel gambar dikelompokkan ke dalam sejumlah kelompok warna tertentu, kemudian setiap piksel diganti dengan warna centroid dari kelompoknya.

Jika parameter jumlah warna dibuat kecil, misalnya 4 warna, gambar hasil kompresi hanya akan memiliki empat warna utama. Hal ini dapat mengurangi kompleksitas gambar secara signifikan. Pada gambar yang memang memiliki warna sederhana, seperti ikon, ilustrasi, bentuk geometri, atau logo, metode ini dapat bekerja dengan baik.

Namun, pada gambar dengan gradasi halus, Color Quantization dapat menyebabkan penurunan kualitas yang terlihat jelas. Gradasi yang sebelumnya halus akan berubah menjadi blok atau tingkat warna yang terpisah. Efek ini disebut banding. Banding biasanya terlihat pada gambar langit, bayangan, tekstur kulit, atau latar belakang dengan transisi warna lembut.

Dari sisi metrik, Color Quantization dapat menghasilkan nilai MSE yang cukup tinggi jika jumlah warna terlalu sedikit. Hal ini karena banyak piksel harus diganti dengan warna centroid yang mungkin berbeda cukup jauh dari warna aslinya. Nilai PSNR juga dapat menurun karena selisih piksel meningkat. SSIM masih dapat bertahan apabila struktur objek tetap terlihat, tetapi kualitas warna secara visual dapat berkurang.

Waktu pemrosesan Color Quantization juga dapat lebih lama dibandingkan HEVC Quality Reduction dan Chroma Subsampling. Hal ini disebabkan oleh proses K-Means yang harus melakukan clustering terhadap piksel gambar. Untuk mempercepat proses, implementasi program mengambil sampel maksimal 100.000 piksel jika ukuran gambar terlalu besar. Sampel ini digunakan untuk melatih K-Means, kemudian model digunakan untuk memprediksi warna seluruh piksel.

Dengan demikian, Color Quantization paling sesuai digunakan untuk gambar dengan jumlah warna terbatas. Jika digunakan pada foto realistis, parameter jumlah warna sebaiknya tidak terlalu kecil agar kualitas visual tetap terjaga.

## 4.8 Analisis Perbandingan Ketiga Algoritma

Ketiga algoritma memiliki pendekatan yang berbeda dalam melakukan kompresi. HEVC Quality Reduction mengatur tingkat kualitas encoding, Chroma Subsampling mengurangi informasi warna, sedangkan Color Quantization mengurangi jumlah warna.

Dari sisi kemudahan penggunaan, HEVC Quality Reduction merupakan algoritma paling sederhana karena hanya membutuhkan parameter kualitas. Pengguna cukup menentukan nilai kualitas yang diinginkan, kemudian encoder HEIC akan melakukan proses kompresi. Metode ini sangat praktis untuk penggunaan umum.

Dari sisi kualitas visual, Chroma Subsampling dapat menjadi pilihan yang baik apabila gambar yang digunakan adalah gambar natural. Hal ini karena pengurangan informasi warna sering kali tidak terlalu terlihat oleh mata manusia. Struktur gambar tetap terjaga karena informasi luminance tidak dikurangi.

Dari sisi pengurangan kompleksitas warna, Color Quantization memberikan hasil yang paling jelas. Gambar hasil kompresi akan terlihat memiliki palet warna yang lebih terbatas. Metode ini dapat sangat efektif untuk gambar sederhana, tetapi kurang ideal untuk gambar fotografis.

Perbandingan karakteristik ketiga algoritma dapat dilihat pada tabel berikut:

| Aspek | HEVC Quality Reduction | Chroma Subsampling | Color Quantization |
|---|---|---|---|
| Prinsip kerja | Menurunkan kualitas encoding HEIC | Mengurangi resolusi komponen warna | Mengurangi jumlah warna menggunakan K-Means |
| Parameter utama | Quality | Jenis subsampling | Jumlah warna |
| Kecepatan proses | Cepat | Cepat hingga sedang | Sedang hingga lambat |
| Kualitas visual | Bergantung nilai quality | Umumnya baik pada foto natural | Bergantung jumlah warna |
| Cocok untuk | Kompresi umum | Foto dan gambar natural | Ikon, ilustrasi, diagram |
| Risiko utama | Artefak kompresi | Pergeseran warna pada tepi tajam | Banding dan hilangnya gradasi |
| Kompleksitas implementasi | Rendah | Sedang | Tinggi |

Jika tujuan utama adalah mengecilkan ukuran file dengan proses cepat, HEVC Quality Reduction menjadi pilihan paling tepat. Jika tujuan utama adalah mempertahankan struktur visual gambar sambil mengurangi informasi warna, Chroma Subsampling dapat digunakan. Jika gambar memiliki warna sederhana dan ingin mengurangi variasi warna, Color Quantization dapat menjadi pilihan yang efektif.

## 4.9 Analisis Berdasarkan Jenis Gambar

Hasil kompresi tidak hanya dipengaruhi oleh algoritma, tetapi juga oleh jenis gambar yang digunakan. Gambar dengan karakteristik berbeda akan memberikan hasil kompresi yang berbeda.

Pada gambar dengan gradasi warna halus, HEVC Quality Reduction biasanya masih dapat mempertahankan tampilan visual selama nilai kualitas tidak terlalu rendah. Chroma Subsampling juga masih cukup baik, tetapi dapat terjadi sedikit perubahan warna. Color Quantization kurang cocok untuk gambar jenis ini jika jumlah warna terlalu sedikit karena dapat menyebabkan banding.

Pada gambar dengan bentuk sederhana dan warna solid, Color Quantization dapat bekerja sangat baik. Hal ini karena gambar jenis ini memang tidak membutuhkan terlalu banyak variasi warna. Chroma Subsampling juga dapat memberikan hasil yang cukup baik, tetapi perubahan pada batas warna mungkin terlihat. HEVC Quality Reduction tetap dapat digunakan, tetapi pengurangan ukuran file mungkin tidak selalu sebesar metode yang secara langsung mengurangi variasi warna.

Pada gambar yang mengandung teks atau garis tajam, HEVC Quality Reduction dengan kualitas sedang lebih aman digunakan. Chroma Subsampling dapat menyebabkan tepi warna menjadi kurang tajam, sedangkan Color Quantization dapat mengubah warna teks atau garis jika jumlah warna terlalu kecil.

## 4.10 Kelebihan dan Kekurangan Sistem

Sistem yang dibuat memiliki beberapa kelebihan. Pertama, aplikasi mampu membandingkan tiga algoritma kompresi dalam satu antarmuka. Kedua, aplikasi menampilkan metrik evaluasi yang cukup lengkap, mulai dari ukuran file, compression ratio, space savings, BPP, PSNR, SSIM, MSE, hingga waktu pemrosesan. Ketiga, aplikasi menyediakan fitur export CSV sehingga hasil pengujian dapat digunakan untuk analisis lanjutan atau dimasukkan ke laporan.

Selain itu, aplikasi juga menyediakan pratinjau gambar sehingga pengguna dapat menilai hasil kompresi secara visual. Hal ini penting karena metrik numerik tidak selalu sepenuhnya menggambarkan persepsi manusia terhadap kualitas gambar.

Namun, sistem ini juga memiliki beberapa keterbatasan. Pertama, hasil pengujian sangat bergantung pada gambar yang digunakan. Kedua, implementasi Chroma Subsampling pada program saat ini hanya membedakan 4:2:0, 4:2:2, dan 4:4:4. Ketiga, Color Quantization membutuhkan waktu lebih lama karena proses clustering menggunakan K-Means. Keempat, hasil kompresi akhir tetap dipengaruhi oleh encoder HEIF saat gambar disimpan ulang.

## 4.11 Kendala Pengujian

Dalam proses pengujian, salah satu hal yang perlu diperhatikan adalah ketersediaan library pendukung. Program membutuhkan beberapa library seperti Pillow, pillow-heif, OpenCV, scikit-image, scikit-learn, NumPy, dan CustomTkinter. Jika salah satu library belum terpasang, aplikasi tidak dapat berjalan secara penuh.

Selain itu, format HEIC belum selalu didukung secara default oleh semua sistem. Oleh karena itu, program menggunakan `pillow-heif` untuk mendaftarkan dukungan pembacaan dan penulisan file HEIC pada Pillow. Tanpa library ini, gambar HEIC tidak dapat dibuka atau disimpan dengan benar.

Kendala lain adalah perbedaan hasil kompresi pada setiap gambar. Gambar dengan banyak detail dan warna kompleks biasanya lebih sulit dikompresi tanpa menurunkan kualitas. Sebaliknya, gambar sederhana dengan warna terbatas biasanya lebih mudah dikompresi.

## 4.12 Kesimpulan Pembahasan

Berdasarkan hasil dan pembahasan, dapat disimpulkan bahwa ketiga algoritma memiliki karakteristik yang berbeda. HEVC Quality Reduction merupakan metode yang paling praktis dan cocok untuk kompresi umum. Metode ini cepat, sederhana, dan langsung memanfaatkan kemampuan encoder HEIC.

Chroma Subsampling cocok digunakan untuk gambar natural karena mampu mengurangi informasi warna tanpa terlalu banyak mengubah struktur gambar. Metode ini memanfaatkan karakteristik penglihatan manusia yang lebih peka terhadap kecerahan dibandingkan warna.

Color Quantization cocok digunakan pada gambar yang memiliki jumlah warna terbatas, seperti ikon, ilustrasi, atau diagram. Namun, metode ini kurang cocok untuk foto realistis dengan gradasi halus karena dapat menyebabkan efek banding dan hilangnya detail warna.

Secara keseluruhan, algoritma terbaik bergantung pada tujuan kompresi dan jenis gambar yang digunakan. Jika prioritas utama adalah keseimbangan antara ukuran file, kualitas visual, dan waktu pemrosesan, HEVC Quality Reduction menjadi pilihan paling stabil. Jika gambar berupa foto natural dan perubahan warna kecil masih dapat diterima, Chroma Subsampling dapat menjadi alternatif yang baik. Jika gambar berupa ilustrasi dengan warna terbatas, Color Quantization dapat memberikan hasil yang efektif.

## 4.13 Saran Pengembangan

Untuk pengembangan selanjutnya, sistem dapat ditingkatkan dengan menambahkan variasi parameter pengujian yang lebih lengkap. Misalnya, HEVC Quality Reduction dapat diuji dengan beberapa nilai kualitas seperti 10, 30, 50, 70, dan 90. Chroma Subsampling dapat dibandingkan menggunakan 4:4:4, 4:2:2, dan 4:2:0. Color Quantization dapat diuji menggunakan jumlah warna 4, 8, 16, 32, dan 64.

Selain itu, pengujian sebaiknya dilakukan pada beberapa jenis gambar, seperti gambar natural, gambar gradasi, gambar dengan teks, dan gambar ilustrasi. Dengan demikian, hasil analisis akan lebih lengkap dan dapat menunjukkan algoritma mana yang paling sesuai untuk setiap jenis gambar.

Sistem juga dapat dikembangkan dengan menambahkan grafik otomatis untuk membandingkan compression ratio, PSNR, SSIM, MSE, dan waktu pemrosesan. Grafik tersebut akan memudahkan pengguna dalam memahami hubungan antara tingkat kompresi dan kualitas gambar.

Terakhir, aplikasi dapat dikembangkan agar tidak hanya mendukung format HEIC, tetapi juga format lain seperti JPEG, PNG, dan WebP. Dengan begitu, sistem dapat digunakan sebagai alat perbandingan kompresi citra yang lebih umum.

## Catatan untuk Pengisian Data Aktual

Bagian tabel hasil pengujian dapat diisi menggunakan data dari aplikasi. Jalankan aplikasi dengan perintah:

```bash
python run.py
```

Setelah itu, buka gambar HEIC, pilih tab **Compare 3 Algorithms**, lalu tekan tombol **Run All 3 Algorithms**. Hasil metrik akan muncul pada tabel bagian bawah aplikasi. Jika ingin menyimpan hasilnya, gunakan tombol **Export All Results CSV**.
