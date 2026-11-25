import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from django.shortcuts import render


BMKG_URL = "https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json"


def gempaterkini(request):
    daftar_gempa = []
    pesan_error = None

    try:
        req = Request(
            BMKG_URL,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; WebUMKM/1.0)',
                'Accept': 'application/json',
            }
        )

        with urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        daftar_gempa = data.get("Infogempa", {}).get("gempa", [])

        # Pastikan data berbentuk list
        if isinstance(daftar_gempa, dict):
            daftar_gempa = [daftar_gempa]

        # Konversi koordinat agar dapat digunakan Leaflet
        for gempa in daftar_gempa:
            try:
                gempa["lat"] = float(
                    gempa.get("Lintang", "0")
                    .replace(" LS", "")
                    .replace(" LU", "")
                )

                # Lintang LS bernilai negatif
                if "LS" in gempa.get("Lintang", ""):
                    gempa["lat"] *= -1

                gempa["lon"] = float(
                    gempa.get("Bujur", "0")
                    .replace(" BT", "")
                    .replace(" BB", "")
                )

                # Bujur BB bernilai negatif
                if "BB" in gempa.get("Bujur", ""):
                    gempa["lon"] *= -1

                gempa["magnitude"] = float(
                    gempa.get("Magnitude", "0").replace(",", ".")
                )

                gempa["kedalaman_angka"] = float(
                    gempa.get("Kedalaman", "0")
                    .replace(" km", "")
                    .replace(",", ".")
                )

                if gempa["kedalaman_angka"] < 70:
                    gempa["warna"] = "#dc2626"
                elif gempa["kedalaman_angka"] <= 300:
                    gempa["warna"] = "#e5a126"
                else:
                    gempa["warna"] = "#16a34a"

            except (ValueError, TypeError):
                gempa["lat"] = None
                gempa["lon"] = None
                gempa["magnitude"] = 0
                gempa["warna"] = "#16a34a"
                gempa["kedalaman_angka"] = 0

        # Hanya 15 data terbaru
        daftar_gempa = daftar_gempa[:15]

    except (HTTPError, URLError, TimeoutError, ValueError) as e:
        pesan_error = f"Tidak dapat mengambil data BMKG: {e}"

    context = {
        "daftar_gempa": daftar_gempa,
        "jumlah_gempa": len(daftar_gempa),
        "pesan_error": pesan_error,
    }

    return render(
        request,
        "gempabumi/gempaterkini.html",
        context
    )
