"""标签页匹配测试"""

import pytest
from unittest.mock import MagicMock
from browserproxy.match import TabMatcher
from browserproxy.tab import Tab


class TestTabMatcher:
    """标签页匹配器测试"""

    def _create_mock_tab(self, tab_id: int, url: str, title: str) -> Tab:
        """创建模拟标签页"""
        tab = MagicMock(spec=Tab)
        tab.tab_id = tab_id
        tab.url = url
        tab.title = title
        return tab

    def test_match_by_url(self):
        """测试通过 URL 匹配"""
        tabs = [
            self._create_mock_tab(1, "https://www.baidu.com", "百度一下"),
            self._create_mock_tab(2, "https://www.google.com", "Google"),
            self._create_mock_tab(3, "https://www.bilibili.com", "哔哩哔哩"),
        ]

        result = TabMatcher.match(tabs, url_contains="baidu")

        assert result is not None
        assert result.tab_id == 1

    def test_match_by_title(self):
        """测试通过标题匹配"""
        tabs = [
            self._create_mock_tab(1, "https://www.baidu.com", "百度一下"),
            self._create_mock_tab(2, "https://www.google.com", "Google搜索"),
            self._create_mock_tab(3, "https://www.bilibili.com", "哔哩哔哩"),
        ]

        result = TabMatcher.match(tabs, title_contains="百度")

        assert result is not None
        assert result.tab_id == 1

    def test_match_by_url_and_title(self):
        """测试通过 URL 和标题同时匹配"""
        tabs = [
            self._create_mock_tab(1, "https://www.baidu.com", "百度一下"),
            self._create_mock_tab(2, "https://m.baidu.com", "百度一下"),
            self._create_mock_tab(3, "https://www.google.com", "Google"),
        ]

        result = TabMatcher.match(tabs, url_contains="www.baidu", title_contains="百度")

        assert result is not None
        assert result.tab_id == 1

    def test_match_no_result(self):
        """测试没有匹配结果"""
        tabs = [
            self._create_mock_tab(1, "https://www.baidu.com", "百度一下"),
            self._create_mock_tab(2, "https://www.google.com", "Google"),
        ]

        result = TabMatcher.match(tabs, url_contains="bilibili")

        assert result is None

    def test_match_multiple_results_returns_first(self):
        """测试多个匹配结果返回第一个"""
        tabs = [
            self._create_mock_tab(1, "https://www.baidu.com", "百度一下"),
            self._create_mock_tab(2, "https://m.baidu.com", "百度一下"),
            self._create_mock_tab(3, "https://www.google.com", "Google"),
        ]

        result = TabMatcher.match(tabs, url_contains="baidu")

        assert result is not None
        assert result.tab_id == 1

    def test_find_all_by_url(self):
        """测试查找所有 URL 匹配的标签页"""
        tabs = [
            self._create_mock_tab(1, "https://www.baidu.com", "百度一下"),
            self._create_mock_tab(2, "https://m.baidu.com", "百度一下"),
            self._create_mock_tab(3, "https://www.google.com", "Google"),
        ]

        results = TabMatcher.find_all(tabs, url_contains="baidu")

        assert len(results) == 2
        assert results[0].tab_id == 1
        assert results[1].tab_id == 2

    def test_find_all_by_title(self):
        """测试查找所有标题匹配的标签页"""
        tabs = [
            self._create_mock_tab(1, "https://www.baidu.com", "百度一下"),
            self._create_mock_tab(2, "https://www.google.com", "百度搜索"),
            self._create_mock_tab(3, "https://www.bilibili.com", "哔哩哔哩"),
        ]

        results = TabMatcher.find_all(tabs, title_contains="百度")

        assert len(results) == 2
        assert results[0].tab_id == 1
        assert results[1].tab_id == 2

    def test_find_all_no_match(self):
        """测试没有匹配结果"""
        tabs = [
            self._create_mock_tab(1, "https://www.baidu.com", "百度一下"),
            self._create_mock_tab(2, "https://www.google.com", "Google"),
        ]

        results = TabMatcher.find_all(tabs, url_contains="bilibili")

        assert len(results) == 0

    def test_match_empty_tabs(self):
        """测试空标签页列表"""
        result = TabMatcher.match([], url_contains="baidu")

        assert result is None

    def test_find_all_empty_tabs(self):
        """测试空标签页列表"""
        results = TabMatcher.find_all([], url_contains="baidu")

        assert len(results) == 0
