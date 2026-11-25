import json
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from .views import gempaterkini


class GempaTerkiniViewTests(TestCase):
    @patch('gempabumi.views.urlopen')
    def test_request_includes_browser_headers(self, mock_urlopen):
        response_data = {
            'Infogempa': {
                'gempa': [{
                    'Coordinates': '-6.2,106.8',
                    'Magnitude': '5.1',
                    'Wilayah': 'Jakarta',
                    'Tanggal': '01 Januari 2026',
                    'Jam': '10:00:00 WIB',
                    'Kedalaman': '10 km',
                    'Potensi': 'Tidak berpotensi tsunami',
                }],
            },
        }
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = json.dumps(response_data).encode('utf-8')

        response = gempaterkini(RequestFactory().get('/gempabumi/'))

        bmkg_request = mock_urlopen.call_args.args[0]
        self.assertEqual(
            bmkg_request.get_header('User-agent'),
            'Mozilla/5.0 (compatible; WebUMKM/1.0)',
        )
        self.assertEqual(
            bmkg_request.get_header('Accept'),
            'application/json',
        )
        self.assertEqual(mock_urlopen.call_args.kwargs['timeout'], 15)
        self.assertEqual(response.status_code, 200)
