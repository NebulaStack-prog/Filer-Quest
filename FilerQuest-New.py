import json
import os
import shlex
import sys
import tempfile
from pathlib import Path

ROOT = Path(os.environ.get('LOCALAPPDATA') or Path.home() / '.local' / 'share') / 'NESTIMS' / 'FilerQuest'
SAVE = ROOT / 'progress.json'
ANSI = sys.stdout.isatty()
if ANSI and os.name == 'nt':
    try:
        import ctypes
        k = ctypes.windll.kernel32
        handle = k.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        ANSI = bool(k.GetConsoleMode(handle, ctypes.byref(mode)) and k.SetConsoleMode(handle, mode.value | 4))
    except Exception:
        ANSI = False


def color(text, code='96'):
    return f'\033[{code}m{text}\033[0m' if ANSI else text


def clear():
    if ANSI: print('\033[2J\033[H', end='', flush=True)
    else: print('\n' * 2)


def header():
    clear()
    print(color('+----------------------------------------------------+'))
    print(color('| N E S T I M S   /   F I L E R    Q U E S T    1.1  |'))
    print(color('+----------------------------------------------------+'))
    print('NS-018 / VIRTUAL LINUX TERMINAL / SAFE TRAINING\n')


class VirtualFS:
    def __init__(self, extras=None, cwd='/'):
        self.nodes = {
            '/': None, '/home': None, '/var': None, '/etc': None, '/tmp': None,
            '/home/readme.txt': 'Это твой домашний каталог. Тут хранятся твои файлы.\n',
            '/var/log.txt': 'Лог-файл: важные события.\nОшибка: не найден файл secret.key\n',
            '/etc/config.ini': '[settings]\nmode=debug\nkey=secret.key\n',
            '/tmp/draft.txt': 'Черновик: не удаляй, это важно.\n',
            '/secret.key': 'TRAINING-KEY-018\n', '/backup.tar': '',
        }
        self.nodes.update(extras or {})
        self.cwd = cwd

    def path(self, value):
        if not value or '\x00' in value or '\\' in value:
            raise ValueError('Некорректный виртуальный путь.')
        if value == '~' or value.startswith('~/'): value = '/home' + value[1:]
        full = value if value.startswith('/') else self.cwd.rstrip('/') + '/' + value
        stack = []
        for p in full.split('/'):
            if p in ('', '.'): continue
            if p == '..':
                if stack: stack.pop()
            else: stack.append(p)
        return '/' + '/'.join(stack)

    def parent(self, p): return p.rsplit('/', 1)[0] or '/'
    def is_dir(self, p): return p in self.nodes and self.nodes[p] is None
    def is_file(self, p): return p in self.nodes and isinstance(self.nodes[p], str)
    def require_dir(self, p):
        if not self.is_dir(p): raise ValueError('Каталог не найден: ' + p)
    def require_file(self, p):
        if not self.is_file(p): raise ValueError('Файл не найден: ' + p)
    def children(self, p):
        self.require_dir(p)
        return sorted(k for k in self.nodes if k != p and self.parent(k) == p)

    def create(self, p, content):
        self.require_dir(self.parent(p))
        if p in self.nodes: raise ValueError('Объект уже существует: ' + p)
        if len(self.nodes) >= 1000: raise ValueError('Лимит виртуальных объектов достигнут.')
        self.nodes[p] = content

    def run(self, line):
        try:
            if len(line) > 4096: raise ValueError('Слишком длинная команда.')
            args = shlex.split(line, posix=True)
            if not args: raise ValueError('Пустая команда.')
            cmd, a = args[0].lower(), args[1:]
            def count(lo, hi=None):
                if not lo <= len(a) <= (lo if hi is None else hi):
                    raise ValueError('Неверное количество аргументов. Введи help.')
            if cmd == 'pwd':
                count(0); return True, self.cwd, ('pwd', self.cwd)
            if cmd == 'ls':
                count(0,1); p = self.path(a[0]) if a else self.cwd
                out = '\n'.join(k.rsplit('/',1)[-1] + ('/' if self.is_dir(k) else '') for k in self.children(p))
                return True, out or '(пусто)', ('ls', p)
            if cmd == 'cd':
                count(0,1); p = self.path(a[0] if a else '~'); self.require_dir(p); self.cwd = p
                return True, p, ('cd', p)
            if cmd == 'mkdir':
                count(1); p = self.path(a[0]); self.create(p, None)
                return True, 'Каталог создан: ' + p, ('mkdir', p)
            if cmd == 'touch':
                count(1); p = self.path(a[0]);
                if not self.is_file(p): self.create(p, '')
                return True, 'Файл существует: ' + p, ('touch', p)
            if cmd == 'cat':
                count(1); p = self.path(a[0]); self.require_file(p)
                return True, self.nodes[p], ('cat', p)
            if cmd == 'grep':
                count(2); word, p = a[0], self.path(a[1]); self.require_file(p)
                matches = [x for x in self.nodes[p].splitlines() if word.casefold() in x.casefold()]
                if not matches: raise ValueError('Совпадений не найдено.')
                return True, '\n'.join(matches), ('grep', word.casefold(), p)
            if cmd in ('cp','mv'):
                count(2); src, dst = map(self.path, a); self.require_file(src)
                if self.is_dir(dst): dst = dst.rstrip('/') + '/' + src.rsplit('/',1)[-1]
                self.require_dir(self.parent(dst))
                if src == dst or dst in self.nodes: raise ValueError('Назначение занято; перезапись отключена.')
                self.create(dst, self.nodes[src])
                if cmd == 'mv': del self.nodes[src]
                return True, f'{src} -> {dst}', (cmd, src, dst)
            if cmd == 'rm':
                count(1); p = self.path(a[0]); self.require_file(p); del self.nodes[p]
                return True, 'Виртуальный файл удалён: ' + p, ('rm', p)
            if cmd == 'rmdir':
                count(1); p = self.path(a[0]); self.require_dir(p)
                if p == '/' or self.cwd == p or self.cwd.startswith(p + '/') or self.children(p):
                    raise ValueError('Нельзя удалить корень, текущий или непустой каталог.')
                del self.nodes[p]; return True, 'Каталог удалён: ' + p, ('rmdir', p)
            if cmd in ('write','append'):
                count(2); p, value = self.path(a[0]), a[1]
                self.require_file(p)
                text = self.nodes[p] + value + '\n' if cmd == 'append' else value + '\n'
                if len(text) > 65536: raise ValueError('Лимит размера файла.')
                self.nodes[p] = text
                return True, 'Текст записан.', (cmd, p, value)
            if cmd in ('head','tail','wc'):
                count(1); p = self.path(a[0]); self.require_file(p); lines = self.nodes[p].splitlines()
                msg = '\n'.join(lines[:5] if cmd == 'head' else lines[-5:]) if cmd != 'wc' else f'Строк: {len(lines)}; слов: {len(self.nodes[p].split())}'
                return True, msg, (cmd, p)
            if cmd == 'find':
                count(2); p = self.path(a[0]); self.require_dir(p)
                if not a[1]: raise ValueError('Укажи имя.')
                hits = sorted(k for k in self.nodes if k.startswith(p.rstrip('/') + '/') and k.rsplit('/',1)[-1] == a[1])
                if not hits: raise ValueError('Ничего не найдено.')
                return True, '\n'.join(hits), ('find', p, a[1])
            if cmd == 'tree':
                count(0,1); p = self.path(a[0]) if a else self.cwd; self.require_dir(p)
                def walk(base, depth=0):
                    out = []
                    for k in self.children(base):
                        out.append('  '*depth + '|-- ' + k.rsplit('/',1)[-1] + ('/' if self.is_dir(k) else ''))
                        if self.is_dir(k): out.extend(walk(k,depth+1))
                    return out
                return True, p + '\n' + '\n'.join(walk(p)), ('tree', p)
            raise ValueError('Неизвестная команда. Введи help.')
        except (ValueError, RecursionError) as e:
            return False, str(e), None



QUESTS = []

def quest(title, description, hint, expected, cwd='/', extras=None):
    QUESTS.append(dict(title=title, description=description, hint=hint, expected=expected, cwd=cwd, extras=extras))

quest('Где ты?', 'Узнай текущий путь.', 'pwd', ('pwd','/'))
quest('Осмотр', 'Посмотри содержимое корня.', 'ls', ('ls','/'))
quest('Дом', 'Перейди в /home.', 'cd home', ('cd','/home'))
quest('Инструкция', 'Прочитай readme.txt.', 'cat readme.txt', ('cat','/home/readme.txt'), '/home')
quest('Проекты', 'Создай projects в /home.', 'mkdir projects', ('mkdir','/home/projects'), '/home')
quest('Заметка', 'Создай note.txt в projects.', 'touch projects/note.txt', ('touch','/home/projects/note.txt'), '/home', {'/home/projects':None})
quest('Учебный ключ', 'Прочитай виртуальный secret.key из корня.', 'cat /secret.key', ('cat','/secret.key'), '/home')
quest('Порядок', 'Перемести var/log.txt в home.', 'mv var/log.txt home/', ('mv','/var/log.txt','/home/log.txt'))
quest('Ошибка', 'Найди слово ошибка в home/log.txt.', 'grep ошибка home/log.txt', ('grep','ошибка','/home/log.txt'), extras={'/home/log.txt':'Ошибка: не найден файл secret.key\n'})
quest('Абсолютный путь', 'Прочитай /etc/config.ini из /home.', 'cat /etc/config.ini', ('cat','/etc/config.ini'), '/home')
quest('На уровень выше', 'Вернись из /home в корень.', 'cd ..', ('cd','/'), '/home')
quest('Домашний каталог', 'Вернись в домашнюю папку через ~.', 'cd ~', ('cd','/home'), '/var')
quest('Копия', 'Скопируй readme.txt в /tmp/readme-copy.txt.', 'cp /home/readme.txt /tmp/readme-copy.txt', ('cp','/home/readme.txt','/tmp/readme-copy.txt'))
quest('Переименование', 'Переименуй /tmp/draft.txt в /tmp/final.txt.', 'mv /tmp/draft.txt /tmp/final.txt', ('mv','/tmp/draft.txt','/tmp/final.txt'))
quest('Уборка', 'Удали только виртуальный /tmp/old.txt.', 'rm /tmp/old.txt', ('rm','/tmp/old.txt'), extras={'/tmp/old.txt':'test'})
quest('Пустой каталог', 'Удали пустой каталог /tmp/empty.', 'rmdir /tmp/empty', ('rmdir','/tmp/empty'), extras={'/tmp/empty':None})
quest('Имя с пробелом', 'Создай файл /home/my note.txt.', 'touch "/home/my note.txt"', ('touch','/home/my note.txt'))
quest('Запись', 'Запиши NESTIMS в /home/note.txt (учебная команда write).', 'write /home/note.txt NESTIMS', ('write','/home/note.txt','NESTIMS'), extras={'/home/note.txt':''})
quest('Дополнение', 'Добавь READY в /home/note.txt (учебная команда append).', 'append /home/note.txt READY', ('append','/home/note.txt','READY'), extras={'/home/note.txt':'NESTIMS\n'})
quest('Начало файла', 'Покажи первые пять строк лога.', 'head /var/log.txt', ('head','/var/log.txt'))
quest('Конец файла', 'Покажи последние пять строк лога.', 'tail /var/log.txt', ('tail','/var/log.txt'))
quest('Статистика', 'Посчитай строки и слова в инструкции.', 'wc /home/readme.txt', ('wc','/home/readme.txt'))
quest('Поиск по имени', 'Найди config.ini внутри /etc (упрощённый find).', 'find /etc config.ini', ('find','/etc','config.ini'))
quest('Дерево', 'Выведи дерево корневого каталога.', 'tree /', ('tree','/'))
quest('Финал', 'Скопируй конфигурацию в /home/config-backup.ini.', 'cp /etc/config.ini /home/config-backup.ini', ('cp','/etc/config.ini','/home/config-backup.ini'))

HELP = '''УЧЕБНЫЕ КОМАНДЫ (не настоящий Bash):
  pwd | ls [путь] | cd [путь] | tree [путь]
  mkdir путь | touch путь | cat путь
  cp источник назначение | mv источник назначение
  rm файл | rmdir пустой_каталог
  grep слово файл | find каталог имя
  head файл | tail файл | wc файл
  write файл "текст" | append файл "текст" (учебные команды)
  hint | restart | help | exit
Пути виртуальные. Кавычки позволяют использовать пробелы.
Флаги Linux, конвейеры и перенаправления не реализованы.'''


def load_progress():
    try:
        n = json.loads(SAVE.read_text(encoding='utf-8'))['completed']
        return max(0, min(len(QUESTS), int(n)))
    except (OSError, ValueError, TypeError, KeyError): return 0


def save_progress(n):
    temp = None
    try:
        ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=ROOT, delete=False) as f:
            temp = Path(f.name); json.dump({'completed': n}, f)
        temp.replace(SAVE); return True
    except OSError:
        print(color('Не удалось сохранить прогресс на диск.', '91')); return False
    finally:
        if temp is not None:
            try: temp.unlink(missing_ok=True)
            except OSError: pass


def prompt(text): return input(text).strip()


def play(level=0, free=False):
    fs = VirtualFS()
    while free or level < len(QUESTS):
        q = None if free else QUESTS[level]
        fs = VirtualFS(q['extras'], q['cwd']) if q else VirtualFS()
        header()
        if q:
            print(color(f'КВЕСТ {level+1:02d}/{len(QUESTS)} | {q["title"]}', '93'))
            print(q['description'])
            print('Каждый квест — отдельный подготовленный снимок. restart восстанавливает его.')
        else: print('СВОБОДНЫЙ РЕЖИМ / все изменения виртуальные.')
        print('help — команды | hint — подсказка | restart — заново | exit — меню\n')
        while True:
            line = prompt(color(f'player:{fs.cwd}$ ', '92'))
            if line == 'exit': return
            if line == 'help': print(HELP); continue
            if line == 'hint': print(q['hint'] if q else HELP); continue
            if line == 'restart': break
            ok, message, event = fs.run(line)
            if message: print(color(message, '97' if ok else '91'))
            if q and ok and event == q['expected']:
                level += 1
                save_progress(max(load_progress(), level))
                print(color('>>> ЗАДАНИЕ ВЫПОЛНЕНО!', '92'))
                prompt('Enter — продолжить...'); break
    print(color('\nВСЕ 25 КВЕСТОВ ПРОЙДЕНЫ!', '93'))
    prompt('Enter — в меню...')


def main():
    try:
        while True:
            header(); n = load_progress()
            print(f'ПРОГРЕСС: [{"#"*n}{"-"*(len(QUESTS)-n)}] {n}/{len(QUESTS)}\n')
            print('[1] Продолжить\n[2] Новая игра / повтор заданий\n[3] Свободный режим\n[4] Справка\n[0] Выход')
            choice = prompt('> ')
            if choice == '0': return
            if choice == '1': play(n if n < len(QUESTS) else 0)
            elif choice == '2': play(0)
            elif choice == '3': play(free=True)
            elif choice == '4': print(HELP); prompt('Enter...')
    except (EOFError, KeyboardInterrupt): print('\nВыход из Filer Quest.')


if __name__ == '__main__': main()
