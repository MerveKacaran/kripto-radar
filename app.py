from flask import Flask, jsonify, send_file
from flask_cors import CORS
import ccxt
import os

app = Flask(__name__)
CORS(app) # Tüm güvenlik engellerini aşan anahtarımız

borsa = ccxt.btcturk()
piyasa_hafizasi = {}

@app.route('/')
def ana_sayfa():
    # index.html dosyasının yerini kesin olarak bulmasını sağlıyoruz
    dosya_yolu = os.path.join(os.path.dirname(__file__), 'index.html')
    if os.path.exists(dosya_yolu):
        return send_file(dosya_yolu)
    else:
        return "HATA: index.html dosyası bulunamadı!", 404

@app.route('/api/veri')
def veri_getir():
    global piyasa_hafizasi
    try:
        tum_veriler = borsa.fetch_tickers()
        anlik_degisimler = []
        tum_fiyatlar = {}
        
        for sembol, veri in tum_veriler.items():
            if '/TRY' in sembol:
                son_fiyat = veri.get('last')
                if son_fiyat is None: continue
                
                tum_fiyatlar[sembol] = son_fiyat
                
                if sembol not in piyasa_hafizasi:
                    piyasa_hafizasi[sembol] = son_fiyat
                    continue
                    
                onceki_fiyat = piyasa_hafizasi[sembol]
                
                if onceki_fiyat > 0:
                    degisim_orani = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
                    
                    if degisim_orani >= 0.06: sinyal = "GÜÇLÜ AL 🚀"
                    elif degisim_orani >= 0.02: sinyal = "AL 🔥"
                    elif degisim_orani <= -0.06: sinyal = "GÜÇLÜ SAT 💥"
                    elif degisim_orani <= -0.02: sinyal = "SAT 🚨"
                    else: sinyal = "BEKLE ⏳"
                    
                    anlik_degisimler.append({
                        "sembol": sembol,
                        "fiyat_raw": son_fiyat,
                        "fiyat": f"{son_fiyat:,.4f} ₺",
                        "degisim_orani": degisim_orani,
                        "degisim_format": f"%{degisim_orani:.4f}",
                        "sinyal": sinyal
                    })
                
                piyasa_hafizasi[sembol] = son_fiyat
                
        if anlik_degisimler:
            anlik_degisimler.sort(key=lambda x: x['degisim_orani'], reverse=True)
            top_5 = anlik_degisimler[:5]
        else:
            top_5 = []
            
        return jsonify({
            "top5": top_5,
            "tum_fiyatlar": tum_fiyatlar
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
