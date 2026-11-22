"""커밋, 브랜치, 현재 사용자와 검색용 역색인을 메모리에 보관한다."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from itertools import chain

import graph
from sorting import merge_sort


@dataclass(frozen=True)
class Commit:
    """한 번 생성하면 내용과 부모가 바뀌지 않는 커밋 노드."""

    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: tuple[str, ...]


class SearchIndex:
    """커밋을 만들 때 키워드와 작성자별로 해시를 모아 둔다."""

    def __init__(self):
        self.by_keyword = defaultdict(list)
        self.by_author = defaultdict(list)

    def add(self, commit: Commit):
        self.by_author[commit.author].append(commit.hash)
        for word in set(commit.message.lower().split()):
            self.by_keyword[word].append(commit.hash)

    def keywords(self, query: str):
        """여러 단어를 입력하면 모든 단어가 포함된 커밋을 생성 순서로 반환한다."""
        words = query.lower().split()
        if not words:
            return []
        first = self.by_keyword.get(words[0], [])
        matches = set(first)
        for word in words[1:]:
            matches.intersection_update(self.by_keyword.get(word, []))
        return [h for h in first if h in matches]


class Repository:
    """HEAD는 브랜치 이름을, 각 브랜치는 마지막 커밋의 해시를 가리킨다."""

    def __init__(self, user: str):
        self.user = user
        self.head = 'main'
        self.branches: dict[str, str | None] = {'main': None}
        self.commits: dict[str, Commit] = {}
        self.children: dict[str, list[str]] = {}
        self.index = SearchIndex()

    def branch(self, name):
        if name in self.branches:
            raise ValueError(f'Branch already exists: {name}')
        self.branches[name] = self.branches[self.head]

    def branch_tip(self, name):
        if name not in self.branches:
            raise ValueError(f'Unknown branch: {name}')
        return self.branches[name]

    def switch(self, name):
        self.branch_tip(name)
        self.head = name

    def commit(self, message):
        parent = self.branches[self.head]
        parents = () if parent is None else (parent,)
        return self._record(message, parents)

    def merge(self, name):
        """현재 브랜치와 대상 브랜치의 서로 다른 두 커밋을 부모로 연결한다."""
        current = self.branches[self.head]
        other = self.branch_tip(name)
        if current is None or other is None:
            raise ValueError('Both branches need a commit')
        if current == other:
            raise ValueError('Branches point to the same commit')
        return self._record(f'Merge {name} into {self.head}', (current, other))

    def _record(self, message, parents):
        """노드와 자식 관계를 기록하고 현재 브랜치와 역색인을 함께 갱신한다."""
        # 커밋을 삭제하지 않으므로 이 번호는 저장소에서 한 번만 쓰인다.
        commit_hash = f'{len(self.commits) + 1:06x}'
        commit = Commit(commit_hash, message, self.user, datetime.now(), parents)
        self.commits[commit_hash] = commit
        self.children[commit_hash] = []
        for parent in parents:
            self.children[parent].append(commit_hash)
        self.branches[self.head] = commit_hash
        self.index.add(commit)
        return commit

    def get_commit(self, commit_hash):
        if commit_hash not in self.commits:
            raise ValueError(f'Unknown commit: {commit_hash}')
        return self.commits[commit_hash]

    def log(self, sort_by=None):
        """기본 로그는 위상 순서로, 정렬 옵션을 주면 해당 필드 순서로 반환한다."""
        if sort_by == 'date':
            return merge_sort(list(self.commits.values()), key=lambda c: c.timestamp)
        if sort_by == 'author':
            return merge_sort(list(self.commits.values()), key=lambda c: c.author)
        return [self.commits[h] for h in graph.topological_order(self.commits, self.children)]

    def parents_of(self, h):
        return self.get_commit(h).parents

    def neighbors(self, h):
        """PATH에서는 한 간선을 양방향으로 따라가므로 부모와 자식을 함께 본다."""
        return chain(self.parents_of(h), self.children[h])

    def path(self, start, end):
        self.get_commit(start)
        self.get_commit(end)
        return graph.shortest_path(start, end, self.neighbors)

    def ancestors(self, start):
        return graph.ancestors(start, self.parents_of)
