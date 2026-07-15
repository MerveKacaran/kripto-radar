from flask import Flask, jsonify, send_file
from flask_cors import CORS
import ccxt
import os

app = Flask(__name__)
CORS(app) 

borsa = ccxt.btcturk()
piyasa_hafizasi = {}

@app.route('/')
def ana_sayfa():
    return send_file('index.html')

@app.route('/api/veri')
def veri_getir():
    global piyasa_hafizasi
    try:
        tum_veriler = borsa.fetch_tickers()
        anlik_degisimler = []
        
        for sembol, veri in tum_veriler.items():
            if '/TRY' in sembol:
                son_fiyat = veri.get('last')
                if son_fiyat is None or son_fiyat == 0: continue
                
                # Eğer daha önce hafızada yoksa kaydet ve devam et (ilk turda veri hesaplanamaz)
                if sembol not in piyasa_hafizasi:
                    piyasa_hafizasi[sembol] = son_fiyat
                    continue
                    
                onceki_fiyat = piyasa_hafizasi[sembol]
                
                # Değişim oranı hesapla
                degisim_orani = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
                
                # Sinyal belirle
                if degisim_orani >= 0.06: sinyal = "GÜÇLÜ AL 🚀"
                elif degisim_orani >= 0.02: sinyal = "AL 🔥"
                elif degisim_orani <= -0.06: sinyal = "GÜÇLÜ SAT 💥"
                elif degisim_orani <= -0.02: sinyal = "SAT 🚨"
                else: sinyal = "BEKLE ⏳"
                
                anlik_degisimler.append({
                    "sembol": sembol,
                    "fiyat": f"{son_fiyat:,.2f} ₺",
                    "degisim_orani": degisim_orani,
                    "degisim_format": f"%{degisim_orani:.2f}",
                    "sinyal": sinyal
                })
                
                # Hafızayı güncelle
                piyasa_hafizasi[sembol] = son_fiyat
                
        # En büyük değişimleri sırala
        top_5 = sorted(anlik_degisimler, key=lambda x: x['degisim_orani'], reverse=True)[:5]
        
        return jsonify({"top5": top_5})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
