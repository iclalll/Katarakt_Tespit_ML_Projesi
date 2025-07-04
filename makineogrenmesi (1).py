# -*- coding: utf-8 -*-
"""makineogrenmesi

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1lCpxYw7zfucm6kkqIOy3tHZj7RoHXqgW
"""

# Bu kod, Kaggle API'sinin beklediği '.kaggle' klasörünü oluşturur.
# Eğer klasör zaten varsa hata vermez.
!mkdir -p ~/.kaggle

# Bu kod, az önce Colab'a yüklediğimiz 'kaggle.json' dosyasını
# '.kaggle' klasörünün içine kopyalar.
!cp kaggle.json ~/.kaggle/

# Bu kod, 'kaggle.json' dosyasının sadece senin tarafından okunup yazılabilmesini sağlar.
# Bu bir güvenlik ayarıdır, API anahtarının gizli kalmasına yardımcı olur.
!chmod 600 ~/.kaggle/kaggle.json

print("Kaggle API kimlik bilgileri başarıyla ayarlandı. Artık Kaggle veri setlerini indirebiliriz!")

import kagglehub
import os
import shutil
from sklearn.model_selection import train_test_split
import pandas as pd

print("--- Adım 1: Kaggle Veri Setini İndirme ---")
try:
    path = kagglehub.dataset_download("gunavenkatdoddi/eye-diseases-classification")
    print(f"Veri seti başarıyla indirildi. Yolu: {path}")
except Exception as e:
    print(f"Hata: Veri seti indirilemedi. {e}")
    print("Kaggle API anahtarınızın doğru yüklendiğinden ve izinlerinin ayarlandığından emin olun.")
    exit()

print("\n--- Adım 2: İndirilen Veri Setinin Yapısını Keşfetme ve AYARLAMA ---")
initial_data_root = path

print(f"İndirilen ana veri dizini: {initial_data_root}")
print("İçerik (ilk birkaç seviye):")
for root, dirs, files in os.walk(initial_data_root):
    level = root.replace(initial_data_root, '').count(os.sep)
    indent = ' ' * 4 * (level)
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 4 * (level + 1)
    for d in dirs:
        print(f'{subindent}{d}/')
    for f in files[:5]:
        print(f'{subindent}{f}')
    if len(files) > 5:
        print(f'{subindent}... ({len(files) - 5} daha fazla dosya)')
    if level > 2:
        break
print("-" * 50)

# ÖNCEKİ KODDAKİ OTOMATİK BULMA KISMINI SİLİYORUZ VEYA ESKİ HALİNE GETİRİYORUZ
# VE ÇIKTIYA GÖRE MANUEL OLARAK data_source_dir VE found_classes'I AYARLIYORUZ.

# SENİN ÇIKTINA GÖRE DOĞRU YOL VE SINIFLAR:
data_source_dir = os.path.join(initial_data_root, 'dataset')
found_classes = [d for d in os.listdir(data_source_dir) if os.path.isdir(os.path.join(data_source_dir, d))]
# Bu liste ['glaucoma', 'normal', 'diabetic_retinopathy', 'cataract'] gibi olacak.
# Sınıfların sırası önemli değil, sadece doğru tespit edildiklerinden emin olmalıyız.

if not found_classes:
    print("Hata: data_source_dir ayarlandı ancak sınıf klasörleri bulunamadı. Lütfen yolu kontrol edin.")
    print(f"data_source_dir: {data_source_dir}")
    exit()
else:
    print(f"Sınıf klasörleri şu dizinde bulundu: {data_source_dir}")
    print(f"Kullanılacak sınıflar: {found_classes}")

print("\n--- Adım 3: Eğitim ve Doğrulama Dizinlerini Oluşturma ve Verileri Ayırma ---")

base_output_dir = 'dataset_split'
train_dir = os.path.join(base_output_dir, 'train')
val_dir = os.path.join(base_output_dir, 'val')

os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)

all_image_paths = []
all_labels = []

for class_name in found_classes:
    class_path = os.path.join(data_source_dir, class_name)
    if not os.path.exists(class_path):
        print(f"Uyarı: {class_name} sınıfının yolu bulunamadı: {class_path}. Bu sınıf atlanıyor.")
        continue

    images = [os.path.join(class_path, img) for img in os.listdir(class_path) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
    all_image_paths.extend(images)
    all_labels.extend([class_name] * len(images))

if not all_image_paths:
    print("Hata: Hiç görüntü dosyası bulunamadı. Lütfen 'data_source_dir' ve sınıf klasörlerini kontrol edin.")
    exit()

train_paths, val_paths, train_labels, val_labels = train_test_split(
    all_image_paths, all_labels, test_size=0.2, random_state=42, stratify=all_labels
)

print(f"Toplam görüntü sayısı: {len(all_image_paths)}")
print(f"Eğitim seti boyutu: {len(train_paths)}")
print(f"Doğrulama seti boyutu: {len(val_paths)}")

print("\nGörüntüler kopyalanıyor... Bu işlem biraz zaman alabilir.")

for i, img_path in enumerate(train_paths):
    class_name = train_labels[i]
    dest_dir = os.path.join(train_dir, class_name)
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy(img_path, os.path.join(dest_dir, os.path.basename(img_path)))
    if (i + 1) % 1000 == 0:
        print(f"  {i+1}/{len(train_paths)} eğitim görüntüsü kopyalandı.")

for i, img_path in enumerate(val_paths):
    class_name = val_labels[i]
    dest_dir = os.path.join(val_dir, class_name)
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy(img_path, os.path.join(dest_dir, os.path.basename(img_path)))
    if (i + 1) % 200 == 0:
        print(f"  {i+1}/{len(val_paths)} doğrulama görüntüsü kopyalandı.")

print("\nVeri seti başarıyla ayrıldı ve organize edildi!")
print(f"Eğitim verisi yolu: {train_dir}")
print(f"Doğrulama verisi yolu: {val_dir}")

print("\n--- Yeni Veri Seti Yapısı Kontrolü ---")
for dataset_type in ['train', 'val']:
    current_dir = os.path.join(base_output_dir, dataset_type)
    if os.path.exists(current_dir):
        print(f"\n{dataset_type.capitalize()} Klasörü:")
        for class_name in os.listdir(current_dir):
            class_path = os.path.join(current_dir, class_name)
            if os.path.isdir(class_path):
                num_images = len(os.listdir(class_path))
                print(f"  {class_name}: {num_images} görüntü")
    else:
        print(f"Uyarı: {current_dir} bulunamadı.")

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16, MobileNet, ResNet50, EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt
import numpy as np

# Önceki adımdan gelen dizin yolları
train_dir = 'dataset_split/train'
val_dir = 'dataset_split/val'

# Görüntü boyutları ve toplu iş boyutu (Batch Size)
IMAGE_SIZE = (224, 224) # Çoğu önceden eğitilmiş model 224x224 veya 256x256 bekler
BATCH_SIZE = 32 # Makalede 32 olarak belirtilmiş

print("--- Adım 4: Veri Artırma ve Görüntü Akışları Oluşturma ---")

# Eğitim veri artırma ve yeniden ölçekleme
train_datagen = ImageDataGenerator(
    rescale=1./255, # Piksel değerlerini 0-1 arasına normalize et
    shear_range=0.2, # Kaydırma dönüşümleri
    zoom_range=0.2, # Yakınlaştırma dönüşümleri
    horizontal_flip=True # Yatay çevirme
)

# Doğrulama verisi sadece yeniden ölçekleme
val_datagen = ImageDataGenerator(rescale=1./255)

# Eğitim veri akışı
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical' # Çok sınıflı sınıflandırma için
)

# Doğrulama veri akışı
validation_generator = val_datagen.flow_from_directory(
    val_dir,
    target_size=IMAGE_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical' # Çok sınıflı sınıflandırma için
)

# Sınıf isimlerini ve sayısını alalım
class_names = list(train_generator.class_indices.keys())
num_classes = len(class_names)

print(f"\nSınıf isimleri: {class_names}")
print(f"Sınıf sayısı: {num_classes}")
print(f"Eğitim adımları (epochs başına): {train_generator.samples // train_generator.batch_size}")
print(f"Doğrulama adımları (epochs başına): {validation_generator.samples // validation_generator.batch_size}")

print("\nVeri akışları başarıyla oluşturuldu. Modeller eğitime hazır.")

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16, MobileNetV2, ResNet50, EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt
import numpy as np
import os

# Önceki adımdan gelen sabitler
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
# train_generator ve validation_generator'ın Adım 4'ten sonra tanımlı olduğunu varsayıyoruz.
# Eğer bu kod çalışırken 'num_classes' tanımsız hatası alırsanız,
# aşağıdaki satırı ekleyin:
# num_classes = len(train_generator.class_indices)
# Veya Adım 4'teki 'num_classes' tanımını bu kod bloğunun başına kopyalayın.
# En güvenlisi, Adım 4 kodunu bir kez daha çalıştırmaktır eğer oturumunuz sıfırlandıysa.
num_classes = len(train_generator.class_indices) # Adım 4'ten gelen class_indices'i kullanarak sınıf sayısını alalım


print("--- Adım 5: Önceden Eğitilmiş CNN Modellerini Oluşturma ve Derleme ---")

def create_model(base_model_name, input_shape=IMAGE_SIZE + (3,)):
    """
    Önceden eğitilmiş bir temel model üzerine özel katmanlar ekleyerek
    bir sınıflandırma modeli oluşturur.
    """
    if base_model_name == 'VGG16':
        base_model = VGG16(weights='imagenet', include_top=False, input_shape=input_shape)
    elif base_model_name == 'MobileNetV2':
        base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=input_shape)
    elif base_model_name == 'ResNet50':
        base_model = ResNet50(weights='imagenet', include_top=False, input_shape=input_shape)
    elif base_model_name == 'EfficientNetB0':
        base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=input_shape)
    else:
        raise ValueError(f"Bilinmeyen temel model adı: {base_model_name}")

    # Temel modelin katmanlarını dondur (ilk eğitimde sadece eklediğimiz katmanlar eğitilecek)
    for layer in base_model.layers:
        layer.trainable = False

    # Temel modelin çıktısına kendi özel katmanlarımızı ekleyelim
    x = base_model.output
    x = GlobalAveragePooling2D()(x) # Özellik haritalarını tek bir vektöre indirge
    x = Dense(1024, activation='relu')(x) # Makalede belirtilen 1024 nöronlu Dense katmanı
    x = Dropout(0.5)(x) # Makalede %0.5 dropout belirtilmişti
    predictions = Dense(num_classes, activation='softmax')(x) # Çıkış katmanı (softmax ile çok sınıflı)

    model = Model(inputs=base_model.input, outputs=predictions)

    # Modeli derleme
    # Makalede Adam optimizer ve categorical_crossentropy (çok sınıflı için) belirtilmiş
    # Metrik olarak doğruluk (accuracy) kullanılacak
    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    print(f"\n--- {base_model_name} Modeli Oluşturuldu ve Derlendi ---")
    model.summary() # Modelin özetini göster

    return model

# Eğiteceğimiz modellerin listesi
model_names = ['VGG16', 'MobileNetV2', 'ResNet50', 'EfficientNetB0']
models = {} # Modelleri saklayacağımız sözlük

# Her bir modeli oluşturalım ve derleyelim
for name in model_names:
    try:
        models[name] = create_model(name)
    except Exception as e:
        print(f"Hata oluştu {name} modeli oluşturulurken: {e}")
        print("Lütfen yukarıdaki create_model fonksiyon tanımının ve gerekli import'ların eksiksiz olduğundan emin olun.")

print("\nTüm modeller oluşturuldu ve eğitime hazır.")

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16, MobileNetV2, ResNet50, EfficientNetB0 # Bu import'lar zaten yukarıda olduğu için sorun değil
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model # Model fonksiyonu zaten tanımlı olduğu için sorun değil
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt
import numpy as np
import os # Kaydedilen modelleri saklamak için

# Önceki adımdan gelen sabitler ve jeneratörler
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
num_classes = 4 # Tespit edilen sınıf sayısı

# train_generator ve validation_generator'ın Adım 4'ten sonra tanımlı olduğunu varsayıyoruz.
# Eğer bu kod çalışırken 'train_generator' veya 'validation_generator' tanımsız hatası alırsanız,
# lütfen Adım 4 kod bloğunu (veri artırma ve jeneratörleri oluşturma) bu kod bloğunun en başına tekrar yapıştırın ve bu hücreyi yeniden çalıştırın.
# Veya en güvenlisi, tüm Colab not defterini baştan (her hücreyi sırasıyla) çalıştırmaktır.

# create_model fonksiyonunun tanımlı olduğundan emin olalım
# (Adım 5'ten buraya taşıdık, eğer Adım 5'i yeniden çalıştırmak istemezsen diye)
def create_model(base_model_name, input_shape=IMAGE_SIZE + (3,)):
    """
    Önceden eğitilmiş bir temel model üzerine özel katmanlar ekleyerek
    bir sınıflandırma modeli oluşturur.
    """
    if base_model_name == 'VGG16':
        base_model = VGG16(weights='imagenet', include_top=False, input_shape=input_shape)
    elif base_model_name == 'MobileNetV2':
        base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=input_shape)
    elif base_model_name == 'ResNet50':
        base_model = ResNet50(weights='imagenet', include_top=False, input_shape=input_shape)
    elif base_model_name == 'EfficientNetB0':
        base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=input_shape)
    else:
        raise ValueError(f"Bilinmeyen temel model adı: {base_model_name}")

    # Temel modelin katmanlarını dondur
    for layer in base_model.layers:
        layer.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(1024, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model

# Modellerin oluşturulması (Eğer önceki hücreyi çalıştırdıysanız 'models' değişkeni zaten dolu olacaktır.
# Bu kısım, oturum sıfırlanırsa diye bir güvenlik önlemi olarak burada.)
model_names = ['VGG16', 'MobileNetV2', 'ResNet50', 'EfficientNetB0']
models = {}
for name in model_names:
    print(f"'{name}' modeli hazırlanıyor...")
    try:
        models[name] = create_model(name)
        # model.summary() çıktısını burada tekrar vermeyelim, Adım 5'te gördük
    except Exception as e:
        print(f"Hata oluştu {name} modeli oluşturulurken: {e}")
        # Hata durumunda döngüden çıkıp kullanıcıyı bilgilendirelim
        exit("Model oluşturma hatası, lütfen kodu kontrol edin.")


print("\n--- Adım 6: CNN Modellerini Eğitme ---")

# Eğitim için geri çağırma (callbacks) fonksiyonlarını tanımlayalım
early_stopping = EarlyStopping(
    monitor='val_accuracy', # Doğrulama doğruluğunu izle
    patience=5, # 5 epoch boyunca iyileşme olmazsa durdur
    restore_best_weights=True # En iyi ağırlıkları geri yükle
)

# Her model için sonuçları ve geçmişi saklayacağımız bir sözlük
history_results = {}

# Kaydedilen modelleri saklamak için dizin oluşturalım
model_save_dir = 'saved_models'
os.makedirs(model_save_dir, exist_ok=True)

# Her modeli eğitelim
for name, model in models.items():
    print(f"\n***** {name} Modeli Eğitiliyor *****")

    model_filepath = os.path.join(model_save_dir, f'{name}_best_model.h5')

    # En iyi modeli kaydetmek için ModelCheckpoint
    model_checkpoint = ModelCheckpoint(
        filepath=model_filepath,
        monitor='val_accuracy',
        save_best_only=True, # Sadece en iyi doğrulama doğruluğunu veren modeli kaydet
        mode='max', # Doğruluğun maksimum olmasını isteriz
        verbose=1 # Kayıt bildirimlerini göster
    )

    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        epochs=50, # Maksimum epoch sayısı (makalede 50 belirtilmiş)
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // BATCH_SIZE,
        callbacks=[early_stopping, model_checkpoint],
        verbose=1 # Eğitim çıktısını göster (Her epoch sonunda bilgi verir)
    )
    history_results[name] = history

    print(f"\n***** {name} Modeli Eğitimi Tamamlandı *****")
    # En iyi doğrulama doğruluğunu history nesnesinden alalım
    best_val_accuracy = max(history.history['val_accuracy'])
    print(f"En yüksek doğrulama doğruluğu: {best_val_accuracy:.4f}")
    print(f"Model şuraya kaydedildi: {model_filepath}")

print("\nTüm modellerin eğitimi tamamlandı.")

# --- Eğitimin Sonuçlarını Görselleştirme (Ek Adım: İsteğe Bağlı) ---
# Her modelin eğitim ve doğrulama doğruluğunu/kaybını çizdirelim

print("\n--- Adım 7: Eğitim Sonuçlarını Görselleştirme ---")

for name, history in history_results.items():
    plt.figure(figsize=(12, 5))

    # Doğruluk grafiği
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Eğitim Doğruluğu')
    plt.plot(history.history['val_accuracy'], label='Doğrulama Doğruluğu')
    plt.title(f'{name} - Eğitim ve Doğrulama Doğruluğu')
    plt.xlabel('Epoch')
    plt.ylabel('Doğruluk')
    plt.legend()
    plt.grid(True)

    # Kayıp grafiği
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Eğitim Kaybı')
    plt.plot(history.history['val_loss'], label='Doğrulama Kaybı')
    plt.title(f'{name} - Eğitim ve Doğrulama Kaybı')
    plt.xlabel('Epoch')
    plt.ylabel('Kayıp')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

print("\nEğitim sonuçlarının görselleştirmesi tamamlandı.")
print("\n--- Proje Tamamlandı ---")
print("Tüm modeller eğitildi, en iyi ağırlıklar kaydedildi ve performans grafikleri çizildi.")
print("Makaledeki sonuçlarla kendi sonuçlarınızı karşılaştırabilirsiniz.")