# Project Libraries
from genre_scraper import scrape_genres
from genre_scraper import WeightType

# General Libraries
from unittest import TestCase

BASEDIR = '../../../../Thesis/data_sample/W/D/E'

class TestGenreScraper(TestCase):
    def test_scrape_simple_1(self):
        tags = scrape_genres(BASEDIR, WeightType.BINARY, limit=1)
        expected = [('blues-rock', 1), ('soft rock', 1), ('pop rock', 1), ('rock', 1), ('jazz', 1), ('classic', 1), ('english', 1), ('pop', 1), ('vocal', 1), ('60s', 1), ('guitar', 1), ('piano', 1), ('duet', 1)]
        self.assertEqual(tags, expected, "scrape 1 naive")

    def test_scrape_frequency_1(self):
        tags_by_frequency = scrape_genres(BASEDIR, WeightType.FREQUENCY, limit=1)
        expected = [('rock', 1.0), ('blues-rock', 0.9998878591909136), ('soft rock', 0.9998878591909136), ('pop rock', 0.9998878591909136), ('jazz', 0.43106126785540716), ('pop', 0.39847915627882613), ('guitar', 0.25148147737469884), ('classic', 0.24372721803089764), ('60s', 0.2395540907941682), ('english', 0.21470880654101426), ('vocal', 0.21470880654101426), ('piano', 0.18733404982450955), ('duet', 0.0)]
        self.assertEqual(tags_by_frequency, expected, "scrape 1 by frequency")

    def test_scrape_weight_1(self):
        tags_by_weight = scrape_genres(BASEDIR, WeightType.WEIGHT, limit=1)
        expected = [('blues-rock', 1.0), ('soft rock', 0.9616059237952426), ('pop rock', 0.9092005730906622), ('rock', 0.7599333215383747), ('jazz', 0.4058097998611308), ('classic', 0.3782070272002891), ('english', 0.3653708791043639), ('pop', 0.3542271232018013), ('vocal', 0.3540044153385307), ('60s', 0.35381009014916337), ('guitar', 0.35250235097906557), ('piano', 0.3131757460906124), ('duet', 0.2725739154084517)]
        self.assertEqual(tags_by_weight, expected, "scrape 1 by weight")


    def test_scrape_simple_5(self):
        tags = scrape_genres(BASEDIR, WeightType.BINARY, limit=5)
        self.assertFalse(('rock', 6) in tags, "scrape 5 naive")
        self.assertTrue(('rock', 5) in tags, "scrape 5 naive")
        self.assertTrue(('jazz', 4) in tags, "scrape 5 naive")
        self.assertTrue(('punk', 3) in tags, "scrape 5 naive")

    def test_scrape_frequency_5(self):
        tags_by_frequency = scrape_genres(BASEDIR, WeightType.FREQUENCY, limit=5)
        self.assertFalse(('rock', 4.8390515770347005) in tags_by_frequency, "scrape 5 by frequency")
        self.assertTrue(('rock', 4.3390515770347005) in tags_by_frequency, "scrape 5 by frequency")
        self.assertTrue(('jazz', 2.7407714279851785) in tags_by_frequency, "scrape 5 by frequency")
        self.assertTrue(('punk', 2.023645641441104)  in tags_by_frequency, "scrape 5 by frequency")

    def test_scrape_weight_5(self):
        tags_by_weight = scrape_genres(BASEDIR, WeightType.WEIGHT, limit=5)
        self.assertFalse(('rock', 4.7895484705702067) in tags_by_weight, "scrape 5 by weight")
        self.assertTrue(('rock', 3.7895484705702067) in tags_by_weight, "scrape 5 by weight")
        self.assertTrue(('jazz', 2.6672770688968876) in tags_by_weight, "scrape 5 by weight")
        self.assertTrue(('punk', 1.99298322314339)   in tags_by_weight, "scrape 5 by weight")

