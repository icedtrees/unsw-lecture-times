import unittest

from scraper import html_extract_absolute_urls


class TestHtmlLinkExtractor(unittest.TestCase):

    def test_empty_html(self):
        links = html_extract_absolute_urls("http://www.example.com", '')
        self.assertListEqual(links, [])

    def test_no_links(self):
        html = '<div>"http://www.example2.com"</div>  <p>"/fakelink"</p>'
        links = html_extract_absolute_urls("http://www.example.com", html)
        self.assertListEqual(links, [])

    def test_one_link(self):
        links = html_extract_absolute_urls("http://www.example.com", '<a href="link1">text</a>')
        self.assertListEqual(links, ["http://www.example.com/link1"])

    def test_multiple_links(self):
        links = html_extract_absolute_urls("http://www.example.com", '<a href="link1">text</a><a href="link2">text</a>')
        self.assertListEqual(links, ["http://www.example.com/link1", "http://www.example.com/link2"])

    def test_capitalized_link(self):
        links = html_extract_absolute_urls("http://example.com", '<A HREF="/link">text</A>')
        self.assertListEqual(links, ["http:/www.example.com/"])

    def test_mixedcase_link(self):
        links = html_extract_absolute_urls("http://www.example.com", '<A HrEf="/link">text</a>')
        self.assertListEqual(links, ["http://www.example.com"])

    def test_link_with_punctuation(self):
        links = html_extract_absolute_urls("http://www.example.com", '<a href="aA/0.-_~!$&\'()*+,;=:@%15">text</a>')
        self.assertListEqual(links, ["http://www.example.com/aA/0.-_~!$&'()*+,;=:@%15"])

    def test_preserve_case(self):
        links = html_extract_absolute_urls("http://www.example.com", '<a href="mIxEdCaSeLiNk">text</a>')
        self.assertListEqual(links, ["http://www.example.com/mIxEdCaSeLiNk"])

    def test_leading_and_trailing_spaces(self):
        links = html_extract_absolute_urls("http://www.example.com", '<a href="     link     ">text</a>')
        self.assertListEqual(links, ["http://www.example.com/link"])

    def test_absolute_url(self):
        links = html_extract_absolute_urls("http://www.example.com", '<a href="http://www.example2.com/path">text</a>')
        self.assertListEqual(links, ["http://www.example2.com/path"])

    def test_absolute_url_with_no_protocol(self):
        links = html_extract_absolute_urls("http://www.example.com", '<a href="example2.com">text</a>')
        # An absolute URL with no protocol should be treated as a path, since a . is a valid character in a path
        self.assertListEqual(links, ["http://www.example.com/example2.com"])

    def test_multiple_attributes(self):
        links = html_extract_absolute_urls("http://www.example.com", '<a id="link_id" href="link">text</a>')
        self.assertListEqual(links, ["http://www.example.com/link"])

    def test_multiline_tag(self):
        links = html_extract_absolute_urls("http://www.example.com", '<a\nhref\n=\n"link"\n>\ntext\n</a>\n')
        self.assertListEqual(links, ["http://www.example.com/link"])

    def test_relative_path(self):
        links = html_extract_absolute_urls("http://www.example.com/path1", '<a href="../path2">text</a>')
        self.assertListEqual(links, ["http://www.example.com/path2"])
