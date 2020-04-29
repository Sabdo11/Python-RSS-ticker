import os
import sys
import unittest
from model import parser
from datetime import timedelta, date, datetime
from unittest.mock import patch, Mock
from model.feed_manager import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class ArticleTestCase(unittest.TestCase):

    def test_article(self):
        article_title = "Test Article"
        article_link = "https://www.theguardian.com/us-news/2020/apr/08/bernie-sanders-ends-2020-presidential-race"
        article_published_date = datetime.now()
        Article(article_title, article_link, article_published_date)


class FeedTestCase(unittest.TestCase):

    def test_feed_add_new(self):
        article_1 = Article("Article 1", "Link 1", (datetime.now() - timedelta(days=1)))  # 1 day ago
        feed = Feed("Feed Name", [article_1])

        self.assertFalse(feed.add_new(article_1))  # Should not add duplicate
        self.assertEqual(feed.get_current_article(), article_1)

        article_4 = Article("Article 4", "Link 4", (datetime.now() - timedelta(days=4)))  # 4 days ago

        self.assertTrue(feed.add_new(article_4))

    def test_feed_contains(self):
        article_1 = Article("Article 1", "Link 1", (datetime.now() - timedelta(days=1)))  # 1 day ago (most recent)

        test_feed = Feed("Test Feed", [article_1])

        self.assertTrue(test_feed.contains(article_1))

        article_2 = Article("Article 2", "Link 2", (datetime.now() - timedelta(days=2)))  # 2 days ago
        article_3 = Article("Article 3", "Link 3", (datetime.now() - timedelta(days=3)))  # 3 days ago
        article_4 = Article("Article 4", "Link 4", (datetime.now() - timedelta(days=4)))  # 4 days ago
        test_feed.update([article_2, article_3, article_4])

        self.assertFalse(test_feed.contains(article_1))

        self.assertTrue(test_feed.contains(article_2))
        self.assertTrue(test_feed.contains(article_3))
        self.assertTrue(test_feed.contains(article_4))

    def test_feed_get_current_article(self):
        article_1 = Article("Article 1", "Link 1", (datetime.now() - timedelta(days=1)))  # 1 day ago
        test_feed = Feed("Test Feed", [article_1])
        self.assertEqual(test_feed.get_next_article(), article_1)  # Should stay at first entry since it only contains 1

        article_2 = Article("Article 2", "Link 2", (datetime.now() - timedelta(days=2)))  # 2 days ago
        test_feed = Feed("Test Feed", [article_1, article_2])

        self.assertEqual(test_feed.get_current_article(), article_1)  # Should start to first entry

        test_feed.get_next_article()  # Advance current article to article_2

        article_3 = Article("Article 3", "Link 3", (datetime.now() - timedelta(days=3)))  # 3 days ago
        article_4 = Article("Article 4", "Link 4", (datetime.now() - timedelta(days=4)))  # 4 days ago
        test_feed.update([article_1, article_3, article_4])

        # Should default to first entry if current article does not exist after update.
        self.assertEqual(test_feed.get_current_article(), article_1)

        test_feed.get_next_article()  # Advance current article to article_3
        test_feed.update([article_1, article_3, article_2])

        self.assertEqual(test_feed.get_current_article(), article_3)  # Should stay the same between updates if possible

    def test_feed_get_next_article(self):
        article_1 = Article("Article 1", "Link 1", (datetime.now() - timedelta(days=1)))  # 1 day ago (most recent)
        test_feed = Feed("Test Feed", [article_1])
        self.assertEqual(test_feed.get_next_article(), article_1)  # Should stay at first entry since it only contains 1

        article_2 = Article("Article 2", "Link 2", (datetime.now() - timedelta(days=2)))  # 2 days ago
        test_feed = Feed("Test Feed", [article_1, article_2])

        self.assertEqual(test_feed.get_next_article(), article_2)

        article_3 = Article("Article 3", "Link 3", (datetime.now() - timedelta(days=3)))  # 3 days ago
        article_4 = Article("Article 4", "Link 4", (datetime.now() - timedelta(days=4)))  # 4 days ago
        test_feed.update([article_1, article_3, article_4])

        # Should default to the newest if the same current article no longer exists after the update
        self.assertEqual(test_feed.get_next_article(), article_3)

        test_feed.update([article_1, article_3, article_4])

        # Current article should stay same between updates if possible
        self.assertEqual(test_feed.get_next_article(), article_4)
        self.assertEqual(test_feed.get_next_article(), article_1)  # Should loop around end to start

    def test_feed_update(self):
        article_1 = Article("Article 1", "Link 1", (datetime.now() - timedelta(days=1)))  # 1 day ago (most recent)
        article_2 = Article("Article 2", "Link 2", (datetime.now() - timedelta(days=2)))  # 2 days ago
        article_3 = Article("Article 3", "Link 3", (datetime.now() - timedelta(days=3)))  # 3 days ago

        feed_name = "Feed Name"
        feed = Feed(feed_name, [article_1, article_2, article_3])

        self.assertEqual(feed.get_current_article(), article_1)

        article_4 = Article("Article 4", "Link 4", (datetime.now() - timedelta(days=4)))  # 3 days ago
        feed.update([article_2, article_3, article_4])

        self.assertEqual(feed.get_current_article(), article_2)  # Should default to newest

        feed.get_next_article()

        self.assertEqual(feed.get_current_article(), article_3)

        feed.get_next_article()
        self.assertEqual(feed.get_current_article(), article_4)  # article_4 is now current

        feed.update([article_1, article_4, article_2])
        self.assertEqual(feed.get_current_article(),
                         article_4)  # Current should be the same between updates if possible

        feed.update([])
        self.assertEqual(feed.get_current_article(), article_4)  # Should not update if given list is empty


class FeedManagerTestCase(unittest.TestCase):

    def test_feed_manager_add(self):
        article_1 = Article("Article 1", "Link 1", (datetime.now() - timedelta(days=1)))  # 1 day ago (most recent)
        test_feed_name = "Test Feed 1"
        test_feed_manager = FeedManager()

        boolean = test_feed_manager.add(article_1, test_feed_name)
        self.assertFalse(boolean)  # Dont add if feed not created through update()

        article_2 = Article("Article 2", "Link 2", (datetime.now() - timedelta(days=2)))  # 2 days ago
        article_3 = Article("Article 3", "Link 3", (datetime.now() - timedelta(days=3)))  # 3 days ago
        test_feed_manager.update([article_1, article_2, article_3], test_feed_name)

        self.assertFalse(test_feed_manager.add(article_2, "Test Feed 2"))

        article_4 = Article("Article 4", "Link 4", (datetime.now() - timedelta(days=4)))  # 4 days ago

        self.assertTrue(test_feed_manager.add(article_4, test_feed_name))

    def test_feed_manager_contains(self):
        test_feed_manager = FeedManager()
        test_feed_name = "Test Feed"

        article_1 = Article("Article 1", "Link 1", (datetime.now() - timedelta(days=1)))  # 1 day ago (most recent)
        article_2 = Article("Article 2", "Link 2", (datetime.now() - timedelta(days=2)))  # 2 days ago
        article_3 = Article("Article 3", "Link 3", (datetime.now() - timedelta(days=3)))  # 3 days ago

        self.assertFalse(
            test_feed_manager.contains(article_1, test_feed_name))  # Feed named "Test Feed" not created yet.

        test_feed_manager.update([article_1, article_2, article_3], test_feed_name)

        self.assertTrue(test_feed_manager.contains(article_1, test_feed_name))

        article_4 = Article("Article 4", "Link 4", (datetime.now() - timedelta(days=4)))  # 4 days ago

        self.assertFalse(test_feed_manager.contains(article_4, test_feed_name))

    def test_feed_manager_get_current_article(self):
        test_feed_manager = FeedManager()
        test_feed_1_name = "Test Feed 1"

        article_1_1 = Article("Article 1_1", "Link 1_1",
                              (datetime.now() - timedelta(days=1)))  # 1 day ago (most recent)
        article_1_2 = Article("Article 1_2", "Link 1_2", (datetime.now() - timedelta(days=2)))  # 2 days ago
        article_1_3 = Article("Article 1_3", "Link 1_3", (datetime.now() - timedelta(days=3)))  # 3 days ago
        test_feed_manager.update([article_1_1, article_1_2, article_1_3], test_feed_1_name)

        #                                                   If current article in feed no longer exists after update,
        self.assertEqual(test_feed_manager.get_current_article(), article_1_1)  # feed should restart at newest

        test_feed_manager.remove(test_feed_1_name)
        # tes_feed_manager should be empty now

        self.assertTrue(test_feed_manager.is_empty())
        self.assertRaises(FeedManagerEmptyError, test_feed_manager.get_current_article)

    def test_feed_manager_get_next_article(self):
        test_feed_manager = FeedManager()
        test_feed_1_name = "Test Feed 1"

        article_1_1 = Article("Article 1_1", "Link 1_1",
                              (datetime.now() - timedelta(days=1)))  # 1 day ago (most recent)
        article_1_2 = Article("Article 1_2", "Link 1_2", (datetime.now() - timedelta(days=2)))  # 2 days ago
        article_1_3 = Article("Article 1_3", "Link 1_3", (datetime.now() - timedelta(days=3)))  # 3 days ago
        test_feed_manager.update([article_1_1, article_1_2, article_1_3], test_feed_1_name)

        self.assertEqual(test_feed_manager.get_next_article(), article_1_2)  # If only 1 feed, move to next within feed

        test_feed_2_name = "Test Feed 2"
        article_2_1 = Article("Article 2_1", "Link 2_1", (datetime.now() - timedelta(days=5)))  # 5 days ago
        article_2_2 = Article("Article 2_2", "Link 2_2", (datetime.now() - timedelta(days=6)))  # 6 days ago
        article_2_3 = Article("Article 2_3", "Link 2_3", (datetime.now() - timedelta(days=7)))  # 7 days ago
        test_feed_manager.update([article_2_1, article_2_2, article_2_3], test_feed_2_name)

        self.assertEqual(test_feed_manager.get_next_article(), article_2_2)  # Should rotate between feeds,
        # even though article_2_1 is older than all of the articles in test feed 1

        self.assertEqual(test_feed_manager.get_next_article(),
                         article_1_3)  # Should wrap around to next article from first feed

        # article_1_3 is now the current

        article_1_4 = Article("Article 4", "Link 4", (datetime.now() - timedelta(days=4)))  # 4 days ago
        article_list = [article_1_1, article_1_2, article_1_4]
        test_feed_manager.update(article_list, test_feed_1_name)

        #                                                   If current article in feed no longer exists after update,
        self.assertEqual(test_feed_manager.get_current_article(), article_1_1)  # feed should restart at newest

        test_feed_manager.remove(test_feed_1_name)
        test_feed_manager.remove(test_feed_2_name)
        # tes_feed_manager should be empty now

        self.assertRaises(FeedManagerEmptyError, test_feed_manager.get_next_article)

    def test_feed_manager_is_empty(self):
        test_feed_manager = FeedManager()
        test_feed_name = "Test Feed"

        self.assertTrue(test_feed_manager.is_empty())

        article_1 = Article("Article 1", "Link 1", (datetime.now() - timedelta(days=1)))  # 1 day ago (most recent)
        article_2 = Article("Article 2", "Link 2", (datetime.now() - timedelta(days=2)))  # 2 days ago
        article_3 = Article("Article 3", "Link 3", (datetime.now() - timedelta(days=3)))  # 3 days ago
        article_list = [article_1, article_2, article_3]
        test_feed_manager.update(article_list, test_feed_name)

        self.assertFalse(test_feed_manager.is_empty())

    def test_feed_manager_remove(self):
        test_feed_1_name = "Test Feed 1"
        article_1_1 = Article("Article 1_1", "Link 1_1",
                              (datetime.now() - timedelta(days=1)))  # 1 day ago (most recent)
        article_1_2 = Article("Article 1_2", "Link 1_2", (datetime.now() - timedelta(days=2)))  # 2 days ago
        article_1_3 = Article("Article 1_3", "Link 1_3", (datetime.now() - timedelta(days=3)))  # 3 days ago

        test_feed_manager = FeedManager()
        test_feed_manager.update([article_1_1, article_1_2, article_1_3], test_feed_1_name)

        test_feed_2_name = "Test Feed 2"
        self.assertFalse(test_feed_manager.remove(test_feed_2_name))

        article_2_1 = Article("Article 2_1", "Link 2_1", (datetime.now() - timedelta(days=5)))  # 5 days ago
        article_2_2 = Article("Article 2_2", "Link 2_2", (datetime.now() - timedelta(days=6)))  # 6 days ago
        article_2_3 = Article("Article 2_3", "Link 2_3", (datetime.now() - timedelta(days=7)))  # 7 days ago
        test_feed_manager.update([article_2_1, article_2_2, article_2_3], test_feed_2_name)

        test_feed_3_name = "Test Feed 3"
        article_3_1 = Article("Article 3_1", "Link 3_1", (datetime.now() - timedelta(days=5)))  # 5 days ago
        article_3_2 = Article("Article 3_2", "Link 3_2", (datetime.now() - timedelta(days=6)))  # 6 days ago
        article_3_3 = Article("Article 3_3", "Link 3_3", (datetime.now() - timedelta(days=7)))  # 7 days ago
        test_feed_manager.update([article_3_1, article_3_2, article_3_3], test_feed_3_name)

        self.assertEqual(test_feed_manager.get_next_article(), article_2_2)
        self.assertEqual(test_feed_manager.get_next_article(), article_3_2)

        self.assertTrue(test_feed_manager.remove(test_feed_3_name))
        # Current feed is now feed 1

        # Advance current feed to feed 2
        self.assertEqual(test_feed_manager.get_next_article(), article_2_3)

        self.assertTrue(test_feed_manager.remove(test_feed_1_name)) # Current_feed_index should decrement with this

    def test_feed_manager_size(self):
        test_feed_manager = FeedManager()

        self.assertEqual(test_feed_manager.size(), 0)

        article_1 = Article("Article 1", "Link 1", (datetime.now() - timedelta(days=1)))  # 1 day ago (most recent)
        article_2 = Article("Article 2", "Link 2", (datetime.now() - timedelta(days=2)))  # 2 days ago
        article_3 = Article("Article 3", "Link 3", (datetime.now() - timedelta(days=3)))  # 3 days ago
        article_list = [article_1, article_2, article_3]
        test_feed_manager.update(article_list, "Test Feed")

        self.assertEqual(test_feed_manager.size(), 1)

        article_4 = Article("Article 4", "Link 4", (datetime.now() - timedelta(days=4)))  # 4 days ago
        test_feed_manager.add(article_4, "Test Feed")

        self.assertEqual(test_feed_manager.size(), 1)

    def test_feed_manager_update(self):
        article_1 = Article("Article 1", "Link 1", (datetime.now() - timedelta(days=1)))  # 1 day ago (most recent)
        article_2 = Article("Article 2", "Link 2", (datetime.now() - timedelta(days=2)))  # 2 days ago
        article_3 = Article("Article 3", "Link 3", (datetime.now() - timedelta(days=3)))  # 3 days ago
        article_4 = Article("Article 4", "Link 4", (datetime.now() - timedelta(days=4)))  # 4 days ago

        test_feed_1_name = "Test Feed 1"
        test_feed_manager = FeedManager()
        test_feed_manager.update([article_1, article_2, article_3], test_feed_1_name)

        self.assertEqual(test_feed_manager.size(), 1)

        article_list = [article_2, article_3, article_4]
        test_feed_manager.update(article_list, test_feed_1_name)

        self.assertEqual(test_feed_manager.size(), 1)

        test_feed_2_name = "Test Feed 2"
        test_feed_manager.update([article_1, article_3, article_4], test_feed_2_name)

        self.assertEqual(test_feed_manager.size(), 2)

        article_list = [article_1, article_2, article_4]
        test_feed_manager.update(article_list, test_feed_2_name)

        self.assertEqual(test_feed_manager.size(), 2)

        test_feed_manager.update([], test_feed_1_name)


# @patch('parser.bs4.BeautifulSoup')
class TestParser(unittest.TestCase):

    def test_get_multi_feed_contents(self):
        pass

    @patch('model.parser.requests.get')
    @patch('model.parser.parser_type')
    def test_get_feed_contents_with_good_url(self, mock_get, mock_type):
        # Test xml feed from DrB80
        """url = 'http://feeds.bbci.co.uk/news/rss.xml'
        XML = '''
            <?xml version="1.0" encoding="UTF-8" ?>
            <rss version="2.0">
            <channel>
                <title>RSS Title</title>
                <description>This is an example of an RSS feed</description>
                <link>http://www.example.com/main.html</link>
                <lastBuildDate>Mon, 06 Sep 2010 00:01:00 +0000 </lastBuildDate>
                <pubDate>Sun, 06 Sep 2009 16:20:00 +0000</pubDate>
                <ttl>1800</ttl>

            <item>
                <title>Example entry</title>
                <description>Here is some text containing an interesting description.</description>
                <link>http://www.example.com/blog/post/1</link>
                <guid isPermaLink="false">7bd204c6-1655-4c27-aeee-53f933c5395f</guid>
                <pubDate>Sun, 06 Sep 2009 16:20:00 +0000</pubDate>
            </item>

            </channel>
            </rss>
        '''

        mock_get.return_value.ok = True
        mock_get.return_value = Mock()
        mock_get.return_value.content.return_value = XML
        mock_type.return_value = 'xml'

        result = parser.get_feed_contents(url)

        self.assertEqual(result[0].title, 'Example entry')
        self.assertEqual(result[0].link, 'http://www.example.com/blog/post/1')
    """

    def test_check_url(self):
        test_xml = 'www.test_url.net/feeds/xml'
        test_rss = 'www.test_url.net/feeds/rss'
        test_tml = 'www.test_url.net/other/tml'
        test_not = ''
        test_fail = 'www.thistestshallnotpass.com'

        result = parser.check_url(test_xml)
        self.assertTrue(result)
        result = parser.check_url(test_rss)
        self.assertTrue(result)
        result = parser.check_url(test_tml)
        self.assertTrue(result)
        result = parser.check_url(test_not)
        self.assertFalse(result)
        result = parser.check_url(test_fail)
        self.assertFalse(result)

    def test_parser_type(self):
        pass

    def test_remove_duplicates(self):
        test_input_one = ['a','a','b','c','d','e','b','a','f']
        expected_one = ['a','b','c','d','e','b','a','f']
        test_imput_two = ['a','b','c','d','e','f']
        test_imput_not = []

        result = parser.remove_duplicates(test_input_one)
        self.assertEqual(result, expected_one)

        result = parser.remove_duplicates(test_imput_two)
        self.assertEqual(result, test_imput_two)

        result = parser.remove_duplicates(test_imput_not)
        self.assertEqual(result, [])



if __name__ == '__main__':
    unittest.main()
