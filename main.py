"""Mini Git의 입력을 해석하고 저장소의 처리 결과를 출력한다."""

import shlex

from bonus import benchmark, diff_lines
from repository import Repository


def print_matches(repo, hashes):
    print(f'Found {len(hashes)} commit(s).')
    for h in hashes:
        print(f'- {h}: {repo.get_commit(h).message}')


def run_command(repo, command, args):
    """초기화된 저장소에서 명령 하나를 실행한다. 잘못된 문법은 한 곳에서 처리한다."""
    match [command, *args]:
        case ['branch', name]:
            repo.branch(name)
            print(f'Created branch: {name}')
        case ['switch', name]:
            repo.switch(name)
            print(f'Switched to branch: {name}')
        case ['commit', message]:
            commit = repo.commit(message)
            print(f'[{repo.head} {commit.hash}] {commit.message}')
        case ['merge', name]:
            commit = repo.merge(name)
            print(f'[{repo.head} {commit.hash}] {commit.message}')
        case ['log'] | ['log', '--sort-by=date'] | ['log', '--sort-by=author']:
            sort_by = args[0].removeprefix('--sort-by=') if args else None
            commits = repo.log(sort_by)
            if not commits:
                print('No commits')
            for commit in commits:
                print(f'commit {commit.hash} ({commit.author}, {commit.timestamp:%Y-%m-%d %H:%M:%S})')
                print(commit.message)
        case ['path', start, end]:
            path = repo.path(start, end)
            print('Path: ' + ' -> '.join(path) if path else 'No path')
        case ['ancestors', start]:
            print_matches(repo, repo.ancestors(start))
        case ['search', query]:
            if query.startswith('--author='):
                author = query.removeprefix('--author=')
                if not author.strip():
                    raise ValueError('Invalid args')
                hashes = repo.index.by_author.get(author, [])
            elif query.startswith('--'):
                raise ValueError('Invalid args')
            else:
                hashes = repo.index.keywords(query)
            print_matches(repo, hashes)
        case _:
            raise ValueError('Invalid args')


def main():
    """한 세션에 저장소 하나를 두고, 입력 오류가 나면 다음 명령을 받는다."""
    repo = None
    while True:
        try:
            line = input('mini-git> ')
        except (EOFError, KeyboardInterrupt):
            print()
            return

        try:
            words = shlex.split(line)
        except ValueError:
            print('Invalid args')
            continue
        if not words:
            continue
        command, *args = words
        command = command.lower()

        try:
            if any(not arg.strip() for arg in args):
                raise ValueError('Invalid args')
            if command in ('exit', 'quit') and not args:
                return
            if command == 'init' and len(args) == 1:
                if repo is not None:
                    raise ValueError('Repository already initialized')
                repo = Repository(args[0])
                print(f'Initialized repository.\nCurrent branch: {repo.head}\nCurrent user: {repo.user}')
            elif command == 'diff' and len(args) == 2:
                for line in diff_lines(*args):
                    print(line)
            elif command == 'bench' and not args:
                for line in benchmark():
                    print(line)
            elif command in ('init', 'exit', 'quit', 'diff', 'bench'):
                raise ValueError('Invalid args')
            elif repo is None:
                print('Initialize repository with INIT <user_name>')
            else:
                run_command(repo, command, args)
        except (ValueError, OSError) as error:
            print(error)


if __name__ == '__main__':
    main()
