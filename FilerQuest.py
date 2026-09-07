import os
import shutil
from pathlib import Path


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_box(text, color=Colors.CYAN):
    width = len(text) + 4
    top = color + "+" + "-" * (width - 2) + "+" + Colors.RESET
    middle = color + "| " + text + " |" + Colors.RESET
    bottom = color + "+" + "-" * (width - 2) + "+" + Colors.RESET
    print(top)
    print(middle)
    print(bottom)


def print_header():
    clear_screen()
    title = "ФАЙЛОВАЯ СИСТЕМА: КВЕСТЫ ПО LINUX"
    print_box(title, Colors.BOLD + Colors.YELLOW)
    print()


SANDBOX_ROOT = Path("./fs_sandbox").resolve()
read_files = set()  


def setup_sandbox():
    if SANDBOX_ROOT.exists():
        shutil.rmtree(SANDBOX_ROOT)
    SANDBOX_ROOT.mkdir(exist_ok=True)
    (SANDBOX_ROOT / "home").mkdir()
    (SANDBOX_ROOT / "var").mkdir()
    (SANDBOX_ROOT / "etc").mkdir()
    (SANDBOX_ROOT / "tmp").mkdir()

    (SANDBOX_ROOT / "home" / "readme.txt").write_text("Это твой домашний каталог. Тут хранятся твои файлы.\n")
    (SANDBOX_ROOT / "var" / "log.txt").write_text(
        "Лог-файл: тут пишут важные события.\nОшибка: не найден файл secret.key\n")
    (SANDBOX_ROOT / "etc" / "config.ini").write_text("[settings]\nmode=debug\nkey=secret.key\n")
    (SANDBOX_ROOT / "tmp" / "draft.txt").write_text("Черновик: не удаляй, это важно.\n")
    
    (SANDBOX_ROOT / "secret.key").touch()
    (SANDBOX_ROOT / "backup.tar").touch()

    read_files.clear()


def get_current_path(cwd: Path) -> str:
    rel = cwd.relative_to(SANDBOX_ROOT) if cwd != SANDBOX_ROOT else Path(".")
    return str(rel)

QUESTS = [
    {
        "id": 1,
        "title": "Найди, где ты находишься",
        "description": "Ты в песочнице. Узнай свой текущий путь командой pwd.",
        "expected_cmd": "pwd",
        "check": lambda cwd, files: True,
        "success": "Отлично! Ты видишь путь к текущей директории."
    },
    {
        "id": 2,
        "title": "Посмотри, что вокруг",
        "description": "Посмотри список файлов и папок в текущей директории командой ls.",
        "expected_cmd": "ls",
        "check": lambda cwd, files: len(files) > 0,
        "success": "Ты видишь файлы и папки. Это основа навигации."
    },
    {
        "id": 3,
        "title": "Перейди в домашнюю директорию",
        "description": "Перейди в папку home командой cd home.",
        "expected_cmd": "cd home",
        "check": lambda cwd, files: cwd.name == "home",
        "success": "Теперь ты в домашней директории. Тут твой readme.txt."
    },
    {
        "id": 4,
        "title": "Прочитай инструкцию",
        "description": "Открой файл readme.txt командой cat readme.txt.",
        "expected_cmd": "cat readme.txt",
        "check": lambda cwd, files: str(cwd / "readme.txt") in read_files,
        "success": "Ты прочитал инструкцию. Теперь знаешь, где искать подсказки."
    },
    {
        "id": 5,
        "title": "Создай папку для проектов",
        "description": "Создай новую папку projects командой mkdir projects.",
        "expected_cmd": "mkdir projects",
        "check": lambda cwd, files: (cwd / "projects").is_dir(),
        "success": "Папка projects создана. Теперь тут можно хранить файлы."
    },
    {
        "id": 6,
        "title": "Создай файл заметки",
        "description": "Создай файл note.txt в папке projects командой touch projects/note.txt.",
        "expected_cmd": "touch projects/note.txt",
        "check": lambda cwd, files: (cwd / "projects" / "note.txt").exists(),
        "success": "Файл note.txt создан. Теперь можно писать заметки."
    },
    {
        "id": 7,
        "title": "Найди секретный ключ",
        "description": "В корне песочницы лежит файл secret.key. Прочитай его командой cat secret.key (сначала перейди в корень командой cd ..).",
        "expected_cmd": "cat secret.key",
        "check": lambda cwd, files: str(SANDBOX_ROOT / "secret.key") in read_files,
        "success": "Секретный ключ найден! Это важный артефакт для следующих уровней."
    },
    {
        "id": 8,
        "title": "Перемести лог в домашнюю директорию",
        "description": "Перемести файл var/log.txt в домашнюю директорию командой mv var/log.txt home/.",
        "expected_cmd": "mv var/log.txt home/",
        "check": lambda cwd, files: (SANDBOX_ROOT / "home" / "log.txt").exists() and not (
                    SANDBOX_ROOT / "var" / "log.txt").exists(),
        "success": "Лог перемещён в домашнюю директорию. Порядок наведён."
    },
    {
        "id": 9,
        "title": "Найди строку с ошибкой",
        "description": "Открой файл home/log.txt и найди строку со словом 'ошибка' командой grep ошибка home/log.txt.",
        "expected_cmd": "grep ошибка home/log.txt",
        "check": lambda cwd, files: "ошибка" in (SANDBOX_ROOT / "home" / "log.txt").read_text().lower(),
        "success": "Строка с ошибкой найдена! Ты освоил поиск по тексту."
    }
]


def run_command(cmd: str, cwd: Path) -> tuple[bool, str, Path | None]:
    parts = cmd.strip().split()
    if not parts:
        return False, "Пустая команда.", None

    action = parts[0].lower()
    new_cwd = None

    if action == "help":
        return True, "Доступные команды: ls, cd, pwd, mkdir, touch, rm, cp, mv, cat, grep, help, hint, exit.", None
    if action == "hint":
        return True, "Подсказка: используй команды, которые соответствуют заданию. Например, cd для перехода, ls для просмотра, cat для чтения.", None

    try:
        if action == "pwd":
            return True, f"Текущий путь: {get_current_path(cwd)}", None

        elif action == "ls":
            entries = list(cwd.iterdir())
            if not entries:
                return True, "В директории пусто.", None
            names = "\n".join(e.name for e in sorted(entries))
            return True, f"Содержимое:\n{names}", None

        elif action == "cd":
            if len(parts) < 2:
                new_cwd = SANDBOX_ROOT / "home"
                if not new_cwd.exists():
                    return False, "Домашняя папка не существует", None
                return True, "", new_cwd

            target = parts[1]

            if target == "..":
                new_cwd = cwd.parent
            elif target == "~":
                new_cwd = SANDBOX_ROOT / "home"
            elif target.startswith("/"):
                new_cwd = (SANDBOX_ROOT / target[1:]).resolve()
            else:
                new_cwd = (cwd / target).resolve()

            try:
                new_cwd.relative_to(SANDBOX_ROOT)
            except ValueError:
                return False, f"Нельзя выходить за пределы песочницы. Попытка перейти в: {new_cwd}", None

            if not str(new_cwd).startswith(str(SANDBOX_ROOT)):
                return False, f"Нельзя выходить за пределы песочницы. Попытка перейти в: {new_cwd}", None

            if not new_cwd.exists() or not new_cwd.is_dir():
                return False, "Такой директории нет.", cwd

            return True, "", new_cwd

        elif action == "mkdir":
            if len(parts) < 2:
                return False, "Укажи имя папки: mkdir <имя>", None
            name = parts[1]
            path = cwd / name
            path.mkdir(exist_ok=False)
            return True, f"Папка {name} создана.", None

        elif action == "touch":
            if len(parts) < 2:
                return False, "Укажи имя файла: touch <имя>", None
            name = parts[1]
            path = cwd / name
            path.touch(exist_ok=True)
            return True, f"Файл {name} создан.", None

        elif action == "rm":
            if len(parts) < 2:
                return False, "Укажи файл: rm <имя>", None
            name = parts[1]
            path = cwd / name
            if not path.exists():
                return False, "Такого файла нет.", None
            path.unlink()
            return True, f"Файл {name} удалён.", None

        elif action == "cp":
            if len(parts) < 3:
                return False, "Используй: cp <откуда> <куда>", None

            src_path = parts[1]
            dst_path = parts[2]

            src = cwd / src_path
            dst = cwd / dst_path

            if not src.exists():
                return False, f"Исходный файл не найден: {src}", None

            if dst.exists() and dst.is_dir():
                final_dst = dst / src.name
            else:
                final_dst = dst

            shutil.copy2(src, final_dst)

            return True, f"Файл скопирован: {src} -> {final_dst}", None

        elif action == "mv":
            if len(parts) < 3:
                return False, "Используй: mv <откуда> <куда>", None

            src_path = parts[1]
            dst_path = parts[2]

            src = cwd / src_path
            dst = cwd / dst_path

            if not src.exists():
                return False, f"Исходный файл не найден: {src}", None

            if dst.exists() and dst.is_dir():
                final_dst = dst / src.name
            else:
                final_dst = dst

            src.rename(final_dst)

            return True, f"Файл перемещён: {src} -> {final_dst}", None

        elif action == "cat":
            if len(parts) < 2:
                return False, "Укажи файл: cat <имя>", None
            path = cwd / parts[1]
            if not path.is_file():
                return False, "Это не файл или не существует.", None
            content = path.read_text()
            read_files.add(str(path.resolve()))
            return True, content, None

        elif action == "grep":
            if len(parts) < 3:
                return False, "Используй: grep <слово> <файл>", None
            word = parts[1].lower()
            path = cwd / parts[2]
            if not path.is_file():
                return False, "Файл не найден.", None
            lines = path.read_text().splitlines()
            matches = [l for l in lines if word in l.lower()]
            if not matches:
                return False, "Совпадений не найдено.", None
            read_files.add(str(path.resolve()))
            return True, "\n".join(matches), None

        else:
            return False, f"Неизвестная команда: {action}. Попробуй help.", None

    except Exception as e:
        return False, f"Ошибка: {e}", None


def play():
    setup_sandbox()
    current_cwd = SANDBOX_ROOT
    level = 0

    while level < len(QUESTS):
        quest = QUESTS[level]
        print_header()
        print(f"{Colors.BOLD}Квест {level + 1}/{len(QUESTS)}{Colors.RESET}")
        print_box(quest["title"], Colors.BLUE)
        print()
        print(quest["description"])
        print()
        print(f"Текущая директория: {get_current_path(current_cwd)}")
        print()

        while True:
            user_input = input(f"{Colors.GREEN}$ {Colors.RESET}").strip()
            if user_input.lower() == "exit":
                print("Выход из игры.")
                return

            ok, msg, new_cwd = run_command(user_input, current_cwd)

            if not ok:
                print(Colors.RED + msg + Colors.RESET)
                continue

            if new_cwd is not None:
                current_cwd = new_cwd

            if msg:
                print(msg)

            if quest["check"](current_cwd, list(current_cwd.iterdir())):
                print()
                print(Colors.GREEN + quest["success"] + Colors.RESET)
                print()
                input("Нажми Enter, чтобы перейти к следующему квесту...")
                level += 1
                break

    print_header()
    print(Colors.YELLOW + "Поздравляем! Все квесты пройдены!" + Colors.RESET)
    print("Ты освоил базовые команды Linux в игровой форме.")


if __name__ == "__main__":
    play()
