"""파일 비교와 정렬 성능 비교를 위한 보너스 기능."""

from difflib import SequenceMatcher
from pathlib import Path
from random import Random
from time import perf_counter

from sorting import insertion_sort, merge_sort


def diff_lines(old_file, new_file):
    """공통 줄에는 공백, 삭제 줄에는 -, 추가 줄에는 +를 붙인다."""
    old = Path(old_file).read_text(encoding='utf-8').splitlines()
    new = Path(new_file).read_text(encoding='utf-8').splitlines()
    matcher = SequenceMatcher(None, old, new, autojunk=False)
    for change, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        if change == 'equal':
            for line in old[old_start:old_end]:
                yield f'  {line}'
        else:
            for line in old[old_start:old_end]:
                yield f'- {line}'
            for line in new[new_start:new_end]:
                yield f'+ {line}'


def benchmark():
    """입력 크기마다 같은 난수 목록을 두 정렬에 주고 실행 시간을 측정한다."""
    random = Random(42)
    yield 'items   merge (ms)   insertion (ms)'
    for size in (100, 500, 2000):
        values = [random.randrange(size) for _ in range(size)]
        times = []
        for algorithm in (merge_sort, insertion_sort):
            start = perf_counter()
            algorithm(values, key=int)
            times.append((perf_counter() - start) * 1000)
        yield f'{size:5d}   {times[0]:10.3f}   {times[1]:14.3f}'
