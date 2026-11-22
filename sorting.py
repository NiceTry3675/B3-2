"""Mini Git에서 사용하는 두 가지 안정 정렬."""


def merge_sort(items, key):
    """목록을 반씩 나누고, 정렬된 두 목록을 앞에서부터 합친다."""
    if len(items) <= 1:
        return list(items)

    middle = len(items) // 2
    left = merge_sort(items[:middle], key)
    right = merge_sort(items[middle:], key)

    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        # 값이 같으면 원래 앞에 있던 왼쪽 원소를 먼저 꺼낸다.
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def insertion_sort(items, key):
    """앞부분을 정렬된 상태로 유지하며 다음 원소를 알맞은 자리에 넣는다."""
    result = list(items)
    for i in range(1, len(result)):
        item = result[i]
        j = i
        while j > 0 and key(result[j - 1]) > key(item):
            result[j] = result[j - 1]
            j -= 1
        result[j] = item
    return result
