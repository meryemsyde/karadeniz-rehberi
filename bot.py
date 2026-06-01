import requests
import time
from deep_translator import GoogleTranslator

#AYARLAR VE API TANIMLAMALARI
STRAPI_URL = "http://localhost:1337"
STRAPI_TOKEN = "7b5acbe25b4e7d1a8857234c7cb032efe8d4b58c65083c55fa7021ed81741f7d84a20a8861bd51bca7b183dedff0cd1dcc548fee0041f0e35ecc626884d6a1c49e0051677c129dce413b93aa4a76ece65ee784cae4b09b8606b0af2aa60851f619a74794cace9d16c48ee7b0341edaa41fb43f0e3b7750ccb87acebb8ec262f8" 

HEADERS = {
    "Authorization": f"Bearer {STRAPI_TOKEN}",
    "Content-Type": "application/json"
}

#KARADENİZ VERİ SETİ (VERİ TOPLAMA)
karadeniz_verileri = [
    {
        "sehir": "Rize",
        "ulke": "Türkiye",
        "sehir_ozet": "Yeşilin her tonunu barındıran, çayın ve yaylaların başkenti.",
        "mekanlar": [
            {"ad": "Ayder Yaylası", "puan": 4.8, "ozet": "Gelin Tülü Şelalesi ve ahşap yayla evleriyle ünlü, etrafı çam ormanlarıyla kaplı eşsiz bir doğa harikası."},
            {"ad": "Zil Kale", "puan": 4.7, "ozet": "Fırtına Vadisi'nde sarp bir kaya üzerine kurulmuş, tarihi İpek Yolu'nu gözetleyen büyüleyici bir ortaçağ kalesi."}
        ]
    },
    {
        "sehir": "Trabzon",
        "ulke": "Türkiye",
        "sehir_ozet": "Tarihi kökenleri, kültürel zenginliği ve muhteşem doğasıyla Karadeniz'in incisi.",
        "mekanlar": [
            {"ad": "Sümela Manastırı", "puan": 4.9, "ozet": "Karadağ'ın dik yamacına kazınmış, sisler arasında kaybolan tarihi ve mistik Rum Ortodoks manastırı."},
            {"ad": "Uzungöl", "puan": 4.5, "ozet": "Dik yamaçların arasında oluşan doğal gölü, yeşilin coşkusu ve yöresel mimarisi ile ünlü turistik merkez."}
        ]
    }
]

#YAPAY ZEKA VE ÇEVİRİ MOTORU

def metni_ingilizceye_cevir(metin):
    """Türkçe metni deep-translator kullanarak İngilizceye çevirir."""
    try:
        cevirici = GoogleTranslator(source='tr', target='en')
        ingilizce_metin = cevirici.translate(metin)
        print(f"🔄 Çeviri Yapıldı: {metin[:20]}... -> {ingilizce_metin[:20]}...")
        return ingilizce_metin
    except Exception as e:
        print(f"❌ Çeviri hatası: {e}")
        return metin  # Hata durumunda orijinal metni döndürür ki sistem çökmesin

def yz_gorsel_linki_uret(mekan_adi, sehir_adi):
    """Pollinations AI kullanarak mekana uygun görsel linki oluşturur."""
    # İngilizce prompt (bilgi istemi) yapay zekanın daha iyi görsel üretmesini sağlar
    prompt = f"cinematic professional travel photography of {mekan_adi} in {sehir_adi} region, lush green nature, beautiful landscape, 4k"
    
    # Boşlukları URL formatına uygun hale getiriyoruz
    uygun_prompt = prompt.replace(" ", "%20")
    gorsel_url = f"https://image.pollinations.ai/p/{uygun_prompt}?width=1024&height=768&seed=42"
    
    print(f"🎨 YZ Görsel Linki Hazırlandı: {mekan_adi} için.")
    return gorsel_url

# --- 4. DOSYA YÖNETİMİ (STRAPI MEDIA LIBRARY API) ---

def gorseli_strapiye_yukle(gorsel_url, dosya_adi):
    """İnternetteki YZ görselini indirir ve Strapi Medya Kütüphanesine yükler."""
    try:
        # 1. Yapay zeka görselini internetten indiriyoruz
        gorsel_yanit = requests.get(gorsel_url)
        if gorsel_yanit.status_code != 200:
            print("❌ Görsel internetten indirilemedi.")
            return None
            
        # 2. İndirilen veriyi geçici olarak belleğe (dosya formatına) alıyoruz
        dosya_verisi = ('files', (f"{dosya_adi}.jpg", gorsel_yanit.content, 'image/jpeg'))
        
        # 3. Strapi'nin dosya yükleme API'sine (upload endpoint) gönderiyoruz
        upload_url = f"{STRAPI_URL}/api/upload"
        
        # Resim yüklerken sadece Token yetkisini gönderiyoruz (Content-Type'ı requests kendi ayarlar)
        upload_headers = {"Authorization": f"Bearer {STRAPI_TOKEN}"}
        
        yanit = requests.post(upload_url, headers=upload_headers, files=[dosya_verisi])
        
        if yanit.status_code == 200:
            resim_id = yanit.json()[0]['id']
            print(f"📁 Görsel Strapi Medya Kütüphanesine Yüklendi! ID: {resim_id}")
            return resim_id  # Bu ID'yi mekana bağlamak için kullanacağız
        else:
            print(f"❌ Strapi görsel yükleme hatası: {yanit.text}")
            return None
    except Exception as e:
        print(f"❌ Görsel yükleme fonksiyonunda hata: {e}")
        return None
    

# --- 5. ANA OTOMASYON MOTORU (STRAPI v5 GÜNCEL FORMATI) ---

def verileri_strapiye_bas():
    print("🚀 Karadeniz Rehberi Otomasyon Motoru Başlatıldı...\n")
    
    for sehir_veri in karadeniz_verileri:
        print(f"📍 İşleniyor: {sehir_veri['sehir']}...")
        
        # 1. Şehri Strapi'ye POST ediyoruz (Varsayılan dil olan TR olarak kaydolur)
        sehir_payload = {
            "data": {
                "Name": sehir_veri["sehir"],
                "Country": sehir_veri["ulke"],
                "Description": sehir_veri["sehir_ozet"]
            }
        }
        
        try:
            sehir_url = f"{STRAPI_URL}/api/cities"
            sehir_yanit = requests.post(sehir_url, headers=HEADERS, json=sehir_payload)
            
            if sehir_yanit.status_code in [200, 201]:
                sehir_id = sehir_yanit.json()["data"]["documentId"] # Strapi v5 documentId'si
                print(f"✅ Şehir Strapi'ye Kaydedildi (ID: {sehir_id})")
            else:
                print(f"❌ Şehir kaydedilemedi: {sehir_yanit.text}")
                continue
        except Exception as e:
            print(f"❌ Şehir API hatası: {e}")
            continue
            
        # 2. O şehre ait mekanları dönüyoruz
        for mekan in sehir_veri["mekanlar"]:
            print(f"🔎 Mekan Ele Alınıyor: {mekan['ad']}")
            
            # YZ Çeviri Motorunu çağırıyoruz
            ingilizce_aciklama = metni_ingilizceye_cevir(mekan["ozet"])
            
            # YZ Görsel Üretim Motorunu çağırıyoruz
            gorsel_linki = yz_gorsel_linki_uret(mekan["ad"], sehir_veri["sehir"])
            
            # Üretilen görseli indirip Strapi Medya Kütüphanesine yüklüyoruz
            resim_id = gorseli_strapiye_yukle(gorsel_linki, mekan["ad"])
            
            # Strapi v5 için TR (Varsayılan) Mekan verisi
            mekan_payload_tr = {
                "data": {
                    "locale": "tr",
                    "Title": mekan["ad"],
                    "Description": mekan["ozet"],
                    "Rating": mekan["puan"],
                    "city": sehir_id,  # İlişki bağı
                    "Cover": resim_id if resim_id else None
                }
            }
            
            # Önce Türkçe mekanı ana kayıt olarak oluşturuyoruz
            try:
                mekan_url = f"{STRAPI_URL}/api/places"
                mekan_yanit_tr = requests.post(mekan_url, headers=HEADERS, json=mekan_payload_tr)
                
                if mekan_yanit_tr.status_code in [200, 201]:
                    mekan_document_id = mekan_yanit_tr.json()["data"]["documentId"]
                    print(f"🎉 {mekan['ad']} (TR) başarıyla yüklendi! ID: {mekan_document_id}")
                    
                    # Strapi v5 localization standart URL yapısı
                    mekan_payload_en = {
                        "data": {
                            "locale": "en",
                            "Title": mekan["ad"],
                            "Description": ingilizce_aciklama,
                            "Rating": mekan["puan"],
                            "city": sehir_id,
                            "Cover": resim_id if resim_id else None
                        }
                    }
                    
                    en_url = f"{STRAPI_URL}/api/places/{mekan_document_id}/localizations"
                    mekan_yanit_en = requests.post(en_url, headers=HEADERS, json=mekan_payload_en)
                    
                    if mekan_yanit_en.status_code in [200, 201]:
                        print(f"🇬🇧 {mekan['ad']} için İngilizce (EN) çevirisi sisteme başarıyla bağlandı!")
                    else:
                        print(f"❌ İngilizce dil paketi yükleme hatası: {mekan_yanit_en.text}")
                else:
                    print(f"❌ Mekan (TR) yükleme hatası: {mekan_yanit_tr.text}")
            except Exception as e:
                print(f"❌ Mekan API hatası: {e}")
                
            print("-" * 30)
            time.sleep(2)

    print("\n🏁 Tüm Karadeniz verileri YZ ile zenginleştirilip Strapi'ye başarıyla basıldı!")

if __name__ == "__main__":
    verileri_strapiye_bas()