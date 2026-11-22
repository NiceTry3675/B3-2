"""부모·자식 관계를 따라 커밋 해시를 탐색한다."""

from collections import deque


def topological_order(commits, children):
    """아직 출력하지 않은 부모가 0개인 커밋부터 차례로 꺼낸다."""
    remaining = {h: len(commit.parents) for h, commit in commits.items()}
    ready = deque(h for h in commits if remaining[h] == 0)
    while ready:
        current = ready.popleft()
        yield current
        for child in children[current]:
            remaining[child] -= 1
            if remaining[child] == 0:
                ready.append(child)


def distances_from(start, neighbors):
    """BFS로 시작점에서 도달 가능한 각 커밋까지의 간선 수를 구한다."""
    distance = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for neighbor in neighbors(current):
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                queue.append(neighbor)
    return distance


def ancestors(start, parents_of):
    """부모 방향으로만 탐색한다. 시작 커밋 자신은 조상에서 제외한다."""
    reachable = distances_from(start, parents_of)
    del reachable[start]
    return list(reachable)


def shortest_path(start, end, neighbors):
    """최단 경로 중 해시를 이어 쓴 문자열이 사전순으로 가장 앞선 경로를 찾는다."""
    distance = distances_from(end, neighbors)
    if start not in distance:
        return []

    path = [start]
    current = start
    while current != end:
        # 남은 거리가 1 줄어드는 이웃은 모두 최단 경로 위에 있다.
        current = min(h for h in neighbors(current) if distance[h] == distance[current] - 1)
        path.append(current)
    return path
