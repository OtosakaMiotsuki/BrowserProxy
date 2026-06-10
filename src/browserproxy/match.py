"""标签页匹配模块"""

from typing import List, Optional
from loguru import logger
from .tab import Tab


class TabMatcher:
    """标签页匹配器"""

    @staticmethod
    def match(
        tabs: List[Tab],
        url_contains: str = "",
        title_contains: str = ""
    ) -> Optional[Tab]:
        """匹配标签页

        Args:
            tabs: 标签页列表
            url_contains: URL 包含的字符串
            title_contains: 标题包含的字符串

        Returns:
            匹配的 Tab 对象，如果没有匹配返回 None
        """
        results = TabMatcher.find_all(tabs, url_contains, title_contains)
        if results:
            logger.debug(f"匹配到 {len(results)} 个标签页，返回第一个: tab_id={results[0].tab_id}")
            return results[0]
        logger.debug("没有匹配的标签页")
        return None

    @staticmethod
    def find_all(
        tabs: List[Tab],
        url_contains: str = "",
        title_contains: str = ""
    ) -> List[Tab]:
        """查找所有匹配的标签页

        Args:
            tabs: 标签页列表
            url_contains: URL 包含的字符串
            title_contains: 标题包含的字符串

        Returns:
            匹配的 Tab 列表
        """
        results = []
        for tab in tabs:
            url_match = not url_contains or url_contains.lower() in tab.url.lower()
            title_match = not title_contains or title_contains.lower() in tab.title.lower()

            if url_match and title_match:
                results.append(tab)

        logger.debug(f"找到 {len(results)} 个匹配的标签页")
        return results
