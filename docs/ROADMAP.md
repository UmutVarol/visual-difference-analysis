# Visual Difference Analysis — Yol Haritası

> Projenin canlı planı. Her faz bitince durum ve öğrendiklerimiz buraya işlenir.
> Kaynak: `Visual Difference Analysis Project Overview.pdf` — Image Processing dersi,
> Muhammed Umut Varol (220218040) & Zeynep Özdemir (220218038).
>
> **Kural: Proje PDF'teki gibi, basit tutulacak. PDF'te olmayan özellik eklenmez.**

## 1. Proje özeti (PDF)

Aynı web sayfasının **eski** ve **güncel** ekran görüntülerini karşılaştırıp değişen bölgeleri
bounding box ile işaretleyen araç. Araç değişen alanları bulur; değişikliğin hata mı yoksa
kasıtlı bir güncelleme mi olduğuna kullanıcı karar verir.

- Kullanıcı **aynı boyutta** iki ekran görüntüsü seçer
- Pipeline: `Piksel farkı → Eşikleme → Morfoloji → Kontur → Bounding box`
- Sonuç PDF'teki görsel gibi: **Earlier version | Updated version | Detected differences**

## 2. Teknolojiler (PDF'teki liste)

| Araç | Ne için |
|---|---|
| Python 3.13 | Proje dili |
| OpenCV (`opencv-python`) | Piksel farkı, eşikleme, morfoloji, kontur bulma |
| NumPy | Görüntü dizileriyle çalışma |
| Streamlit | Basit kullanıcı arayüzü |
| Visual Studio Code | Geliştirme ortamı |
| Git | Sürüm kontrolü ve ortak çalışma |

Ortam: Python'un kendi `venv` sanal ortamı + `requirements.txt` (sürümler sabit, Zeynep aynı
ortamı `pip install -r requirements.txt` ile kurar).

**Kurulum** (Python **3.12 veya üstü** gerekli — NumPy 2.5 bunu istiyor):

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt      # Windows: .venv\Scripts\pip install -r requirements.txt
.venv/bin/streamlit run app.py                 # Windows: .venv\Scripts\streamlit run app.py
```

**Veritabanı / sunucu yok.** İki görüntü yüklenir, bellekte işlenir, sonuç ekranda gösterilir;
saklanacak bir veri yok. Uygulama lokalde Streamlit ile çalışır.

## 3. Dosya yapısı

```
Image Processing Project/
├── app.py            # Streamlit arayüzü (yükle → karşılaştır → göster)
├── visual_diff.py    # Görüntü işleme fonksiyonları (OpenCV + NumPy)
├── samples/          # Denemek için örnek önce/sonra görüntüleri
├── requirements.txt
├── README.md
└── docs/ROADMAP.md
```

Görüntü işleme (`visual_diff.py`) ile arayüz (`app.py`) ayrı dosyada: her biri tek işe odaklı,
okuması ve anlatması kolay.

## 4. Fazlar

Her faz sonunda: çalışan kod → ne yaptığımızın ve kavramların açıklaması →
**durup genel görünümü kontrol** → onayla commit.

### Faz 0 — Ortam kurulumu
- Proje klasörü, `git init`, `.gitignore`
- `python3 -m venv .venv`, `requirements.txt` (opencv-python, numpy, streamlit)
- VS Code'da `.venv` yorumlayıcısını seçme
- Kontrol: `import cv2, numpy, streamlit` çalışıyor, boş Streamlit sayfası açılıyor
- **Kavramlar:** sanal ortam, bağımlılık dosyası, Git'in temeli

### Faz 1 — Görüntüleri okuma ve boyut kontrolü
- İki görüntüyü okuma (OpenCV → NumPy dizisi)
- Aynı boyutta değilse anlaşılır hata (PDF: ilk sürümde aynı boyut şartı)
- `samples/` içine denemek için bir önce/sonra çifti (PDF'teki örnek dashboard gibi)
- **Kavramlar:** görüntü = `(yükseklik, genişlik, 3)` boyutlu `uint8` dizi, BGR renk sırası,
  piksel koordinatları

### Faz 2 — Piksel farkı ve eşikleme (pipeline adım 1–2)
- `cv2.absdiff` ile iki görüntünün piksel piksel farkı — **3 renk kanalında ayrı ayrı**, sonra
  kanalların en büyüğü alınır (önce gri tonlamaya çevirmek bazı renk değişimlerini kaçırır)
- `cv2.threshold` ile farkı siyah-beyaz maskeye çevirme; eşik düşük tutulur ki ince renk tonu
  değişimleri de yakalansın
- **Kavramlar:** neden düz çıkarma değil `absdiff`, neden gri tonlama yetmez, eşik değeri seçimi

### Faz 3 — Morfoloji, kontur ve bounding box (pipeline adım 3–5)
- Morfoloji (`cv2.dilate` / `cv2.morphologyEx`): yakın fark piksellerini tek bölgede birleştirme
  (ör. bir sayının rakamları tek kutu olur)
- Gerçek küçük değişiklikler (tek rakam, birkaç piksellik ikon) kaybolmasın diye büyük alan
  filtresi kullanılmaz
- `cv2.findContours` ile bölgeleri bulma, `cv2.boundingRect` ile kutuya çevirme
- Kutuları güncel görüntü üzerine `cv2.rectangle` ile çizme
- **Kavramlar:** genişletme/aşındırma, kernel, kontur, bounding box

### Faz 4 — Streamlit arayüzü
- İki ekran görüntüsü yükleme
- Boyut uyuşmazlığında hata mesajı
- PDF'teki gibi üç sütun: Earlier version | Updated version | Detected differences
- **Kavramlar:** Streamlit'in çalışma mantığı, BGR ↔ RGB dönüşümü

### Faz 5 — Son kontrol ve teslim
- Örneklerle baştan sona deneme: her değişiklik yakalandı mı, işlem ne kadar sürdü
- README: kurulum ve çalıştırma adımları
- Git ile son commit

## 5. Dikkat noktaları

- **uint8 taşması:** `after - before` negatifte sarar (5 − 10 = 251) → `cv2.absdiff` kullanılır
- **Gri tonlamada renk kaybı:** koyu kırmızı (196,0,0) ile koyu yeşil (0,100,0) OpenCV gri
  tonlamasında ikisi de **59** olur → fark kanal bazlı alınır
- **Görüntü formatı:** PNG kullanılmalı; JPEG sıkıştırması değişmeyen alanlarda da fark üretir
- **Aynı koşullar:** iki görüntü aynı tarayıcı, aynı zoom, aynı pencere boyutunda alınmalı;
  böylece değişmeyen pikseller birebir aynı olur ve eşik çok düşük tutulabilir
- **Kenar yumuşatma gürültüsü:** koşullar farklıysa yazı kenarlarında küçük farklar çıkar
- **BGR ↔ RGB:** OpenCV BGR, Streamlit RGB bekler
- **PNG alfa kanalı:** 4 kanallı görüntüler 3 kanala çevrilir
- **Sınırlama (raporda belirtilecek):** bir eleman kayınca altındaki alan da "değişmiş" görünür
- **Sınırlama:** araç *nerenin* değiştiğini bulur; rengin neye dönüştüğünü ya da sayının ne
  olduğunu "okumaz" (bu OCR gerektirir, PDF kapsamı dışında)

## 6. Durum ve ilerleme günlüğü

- [x] **Planlama** — 2026-11-02: PDF analiz edildi, plan PDF kapsamına göre sadeleştirildi.
  Hassasiyet kararları: kanal bazlı fark, düşük eşik, büyük alan filtresi yok, PNG. Veritabanı yok.
- [x] **Faz 0 — Ortam kurulumu** — 2026-11-02: `git init` (main), `.gitignore`, `.venv` (Python 3.13.2),
  `requirements.txt` (opencv-python 4.14.0.94, numpy 2.5.4, streamlit 1.66.1), geçici `app.py`.
  Doğrulandı: importlar çalışıyor, Streamlit sayfası localhost:8501'de açılıyor. İlk commit atıldı.
- [ ] Faz 1 — Görüntüleri okuma ve boyut kontrolü
- [ ] Faz 2 — Piksel farkı ve eşikleme
- [ ] Faz 3 — Morfoloji, kontur ve bounding box
- [ ] Faz 4 — Streamlit arayüzü
- [ ] Faz 5 — Son kontrol ve teslim

## 7. Açık sorular

- Teslim tarihi?
- Zeynep hangi işletim sisteminde çalışıyor?
- GitHub reposu var mı?
