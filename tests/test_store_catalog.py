import copy
import unittest
from unittest.mock import patch
from store_catalog import get_customized_products

class StoreImageCompatibilityTests(unittest.TestCase):
    def test_stock_customizations_keep_commercial_fields_and_refresh_only_old_images(self):
        persisted = {'BJJ-001': {'name': 'Kimono personalizado', 'stock_quantity': 7, 'colors': [
            {'id': 'preto', 'stock_quantity': 3, 'price': 510, 'image': 'img/store/kimono_preto.jpg'},
            {'id': 'branco', 'stock_quantity': 4, 'price': 490, 'image': 'uploads/custom-kimono.webp'}]}}
        before = copy.deepcopy(persisted)
        with patch('store_catalog.load_store_customizations', return_value=persisted):
            product = next(p for p in get_customized_products() if p['id'] == 'BJJ-001')
        self.assertEqual(product['name'], 'Kimono personalizado')
        self.assertEqual(product['stock_quantity'], 7)
        colors = {c['id']: c for c in product['colors']}
        self.assertEqual(colors['preto']['image'], 'img/store/kimono_preto_frente_costas_v1.png')
        self.assertEqual(colors['preto']['price'], 510)
        self.assertEqual(colors['preto']['stock_quantity'], 3)
        self.assertEqual(colors['branco']['image'], 'uploads/custom-kimono.webp')
        self.assertEqual(persisted, before)
