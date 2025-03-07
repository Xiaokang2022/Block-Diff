# Copyright (C) 2009-2013 Piotr Piastucki <the_leech@users.berlios.de>
# Copyright (C) 2012-2013 Kai Willadsen <kai.willadsen@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import difflib
import typing


def find_common_prefix(a: str, b: str) -> int:
    """查找两个字符串的公共前缀长度"""
    if not a or not b:  # 空字符串直接返回
        return 0
    if a[0] == b[0]:
        pointermax = min(len(a), len(b))
        pointermid = pointermax
        pointermin = 0
        while pointermin < pointermid:  # 二分查找
            if a[pointermin:pointermid] == b[pointermin:pointermid]:
                pointermin = pointermid
            else:
                pointermax = pointermid
            pointermid = int((pointermax - pointermin) // 2 + pointermin)
        return pointermid
    return 0


def find_common_suffix(a: str, b: str) -> int:
    """查找两个字符串的公共前缀长度，同上"""
    if not a or not b:
        return 0
    if a[-1] == b[-1]:
        pointermax = min(len(a), len(b))
        pointermid = pointermax
        pointermin = 0
        while pointermin < pointermid:
            a_tail = a[-pointermid:len(a) - pointermin]
            b_tail = b[-pointermid:len(b) - pointermin]
            if a_tail == b_tail:
                pointermin = pointermid
            else:
                pointermax = pointermid
            pointermid = int((pointermax - pointermin) // 2 + pointermin)
        return pointermid
    return 0


class DiffChunk(typing.NamedTuple):
    """差异块类，标准 difflib 的差异块五元组"""
    tag: str  # 差异块的类型：replace, delete, insert 和 equal 等，定义在标准库 difflib
    start_a: int  # 字符串 a 的起始位置
    end_a: int  # 字符串 a 的结束位置
    start_b: int  # 同上
    end_b: int


class MyersSequenceMatcher(difflib.SequenceMatcher):
    """基于 Myers 算法的序列差异匹配类"""

    def __init__(self, a: str = "", b: str = "") -> None:
        # The sequences we're comparing must be considered immutable;
        # calling e.g., GtkTextBuffer methods to retrieve these line-by-line
        # isn't really a thing we can or should do.
        self.a = a[:]
        self.b = b[:]
        self.matching_blocks = self.opcodes = None
        self.aindex = []
        self.bindex = []
        self.common_prefix = self.common_suffix = 0
        self.lines_discarded = False

    @typing.override  # 重写 difflib.SequenceMatcher 的方法，这行可以注释掉，类型提示用的
    def get_matching_blocks(self) -> list[tuple[int, int, int]]:
        """获取序列匹配（相等）列表，没有就自动跑一遍 Myers 算法的生成器并返回序列匹配列表

        返回值见: https://docs.python.org/zh-cn/3/library/difflib.html#difflib.SequenceMatcher.get_matching_blocks
        """
        if self.matching_blocks is None:
            for _ in self.initialise():  # 跑一遍实现 Myers 算法的生成器
                pass
        return self.matching_blocks

    @typing.override  # 重写 difflib.SequenceMatcher 的方法，这行可以注释掉，类型提示用的
    def get_opcodes(self) -> list[DiffChunk]:
        """获取一个 DiffChunk 的列表

        返回值见: https://docs.python.org/zh-cn/3/library/difflib.html#difflib.SequenceMatcher.get_opcodes
        """
        opcodes = super().get_opcodes()
        return [DiffChunk._make(chunk) for chunk in opcodes]  # _make: NamedTuple 类方法，从存在的序列或迭代实例创建一个新实例

    def get_difference_opcodes(self) -> list[DiffChunk]:
        """获取上面方法 get_opcodes 中非 equal 标签的 DiffChunk 实例，相当于过滤"""
        return [chunk for chunk in self.get_opcodes() if chunk.tag != "equal"]

    def preprocess_remove_prefix_suffix(self, a: str, b: str) -> tuple[str, str]:
        """预处理，移除两段序列前后相同的部分，返回处理后的两个字符串的元组"""
        # remove common prefix and common suffix
        self.common_prefix = self.common_suffix = 0
        self.common_prefix = find_common_prefix(a, b)
        if self.common_prefix > 0:
            a = a[self.common_prefix:]
            b = b[self.common_prefix:]

        if len(a) > 0 and len(b) > 0:
            self.common_suffix = find_common_suffix(a, b)
            if self.common_suffix > 0:
                a = a[:len(a) - self.common_suffix]
                b = b[:len(b) - self.common_suffix]
        return (a, b)

    def preprocess_discard_nonmatching_lines(self, a: str, b: str) -> tuple[str, str]:
        """预处理：删去完全不匹配的行"""
        # discard lines that do not match any line from the other file
        if len(a) == 0 or len(b) == 0:  # 直接返回
            self.aindex = []
            self.bindex = []
            return (a, b)

        def index_matching(a: str, b: str) -> tuple[list[str], list[int]]:
            aset = frozenset(a)
            matches, index = [], []
            for i, line in enumerate(b):
                if line in aset:
                    matches.append(line)
                    index.append(i)
            return matches, index

        indexed_b, self.bindex = index_matching(a, b)
        indexed_a, self.aindex = index_matching(b, a)

        # We only use the optimised result if it's worthwhile. The constant
        # represents a heuristic of how many lines constitute 'worthwhile'.
        self.lines_discarded = (len(b) - len(indexed_b) > 10 or
                                len(a) - len(indexed_a) > 10)
        if self.lines_discarded:
            a = indexed_a
            b = indexed_b
        return (a, b)

    def preprocess(self) -> tuple[str, str]:
        # 预处理：返回同时完成两项预处理操作后的字符串
        """
        Pre-processing optimizations:
        1) remove common prefix and common suffix
        2) remove lines that do not match
        """
        a, b = self.preprocess_remove_prefix_suffix(self.a, self.b)
        return self.preprocess_discard_nonmatching_lines(a, b)

    def postprocess(self) -> None:
        # 后处理
        """
        Perform some post-processing cleanup to reduce 'chaff' and make
        the result more human-readable. Since Myers diff is a greedy
        algorithm backward scanning of matching chunks might reveal
        some smaller chunks that can be combined together.
        """
        mb = [self.matching_blocks[-1]]
        i = len(self.matching_blocks) - 2
        while i >= 0:
            cur_a, cur_b, cur_len = self.matching_blocks[i]
            i -= 1
            while i >= 0:
                prev_a, prev_b, prev_len = self.matching_blocks[i]
                if prev_b + prev_len == cur_b or prev_a + prev_len == cur_a:
                    prev_slice_a = self.a[cur_a - prev_len:cur_a]
                    prev_slice_b = self.b[cur_b - prev_len:cur_b]
                    if prev_slice_a == prev_slice_b:
                        cur_b -= prev_len
                        cur_a -= prev_len
                        cur_len += prev_len
                        i -= 1
                        continue
                break
            mb.append((cur_a, cur_b, cur_len))
        mb.reverse()
        self.matching_blocks = mb

    def build_matching_blocks(self, lastsnake) -> None:
        """Build list of matching blocks based on snakes

        The resulting blocks take into consideration multiple preprocessing
        optimizations:
         * add separate blocks for common prefix and suffix
         * shift positions and split blocks based on the list of discarded
           non-matching lines
        """
        self.matching_blocks = matching_blocks = []

        common_prefix = self.common_prefix
        common_suffix = self.common_suffix
        aindex = self.aindex
        bindex = self.bindex
        while lastsnake is not None:
            lastsnake, x, y, snake = lastsnake
            if self.lines_discarded:
                # split snakes if needed because of discarded lines
                x += snake - 1
                y += snake - 1
                xprev = aindex[x] + common_prefix
                yprev = bindex[y] + common_prefix
                if snake > 1:
                    newsnake = 1
                    for i in range(1, snake):
                        x -= 1
                        y -= 1
                        xnext = aindex[x] + common_prefix
                        ynext = bindex[y] + common_prefix
                        if (xprev - xnext != 1) or (yprev - ynext != 1):
                            matching_blocks.insert(0, (xprev, yprev, newsnake))
                            newsnake = 0
                        xprev = xnext
                        yprev = ynext
                        newsnake += 1
                    matching_blocks.insert(0, (xprev, yprev, newsnake))
                else:
                    matching_blocks.insert(0, (xprev, yprev, snake))
            else:
                matching_blocks.insert(0, (x + common_prefix,
                                           y + common_prefix, snake))
        if common_prefix:
            matching_blocks.insert(0, (0, 0, common_prefix))
        if common_suffix:
            matching_blocks.append((len(self.a) - common_suffix,
                                    len(self.b) - common_suffix,
                                    common_suffix))
        matching_blocks.append((len(self.a), len(self.b), 0))
        # clean-up to free memory
        self.aindex = self.bindex = None

    def initialise(self):
        # 优化的 Myers 算法的实现，返回一个生成器
        """
        Optimized implementation of the O(NP) algorithm described by Sun Wu,
        Udi Manber, Gene Myers, Webb Miller
        ("An O(NP) Sequence Comparison Algorithm", 1989)
        http://research.janelia.org/myers/Papers/np_diff.pdf
        """

        a, b = self.preprocess()
        m = len(a)
        n = len(b)
        middle = m + 1
        lastsnake = None
        delta = n - m + middle
        dmin = min(middle, delta)
        dmax = max(middle, delta)
        if n > 0 and m > 0:
            size = n + m + 2
            fp = [(-1, None)] * size
            p = -1
            while True:
                p += 1
                if not p % 100:
                    yield None
                # move along vertical edge
                yv = -1
                node = None
                for km in range(dmin - p, delta, 1):
                    t = fp[km + 1]
                    if yv < t[0]:
                        yv, node = t
                    else:
                        yv += 1
                    x = yv - km + middle
                    if x < m and yv < n and a[x] == b[yv]:
                        snake = x
                        x += 1
                        yv += 1
                        while x < m and yv < n and a[x] == b[yv]:
                            x += 1
                            yv += 1
                        snake = x - snake
                        node = (node, x - snake, yv - snake, snake)
                    fp[km] = (yv, node)
                # move along horizontal edge
                yh = -1
                node = None
                for km in range(dmax + p, delta, -1):
                    t = fp[km - 1]
                    if yh <= t[0]:
                        yh, node = t
                        yh += 1
                    x = yh - km + middle
                    if x < m and yh < n and a[x] == b[yh]:
                        snake = x
                        x += 1
                        yh += 1
                        while x < m and yh < n and a[x] == b[yh]:
                            x += 1
                            yh += 1
                        snake = x - snake
                        node = (node, x - snake, yh - snake, snake)
                    fp[km] = (yh, node)
                # point on the diagonal that leads to the sink
                if yv < yh:
                    y, node = fp[delta + 1]
                else:
                    y, node = fp[delta - 1]
                    y += 1
                x = y - delta + middle
                if x < m and y < n and a[x] == b[y]:
                    snake = x
                    x += 1
                    y += 1
                    while x < m and y < n and a[x] == b[y]:
                        x += 1
                        y += 1
                    snake = x - snake
                    node = (node, x - snake, y - snake, snake)
                fp[delta] = (y, node)
                if y >= n:
                    lastsnake = node
                    break
        self.build_matching_blocks(lastsnake)
        self.postprocess()
        yield 1
