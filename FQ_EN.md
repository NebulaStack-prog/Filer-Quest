## Part 1. Main Document.

### 1. Title and Basic Information.

• **Name:** Filer Quest

• **Purpose:** Project No. 18. Product.

• **Project Phase:** Phase II.

• **Technology Stack:** Python (standard libraries, terminal interaction using ANSI colors).

• **Project Status:** Fully completed.

### 2. Project Overview.

**Filer Quest** is an educational console quest game written in Python and designed to teach the basic Linux file system commands in a game-based format.

The player completes a sequence of 9 quests, each introducing a new command: pwd, ls, cd, cat, mkdir, touch, mv, grep, and others.

All operations are performed inside an isolated "sandbox" (fs_sandbox), making the game completely safe — the real file system is never affected.

The application uses colored terminal output (ANSI escape sequences) to create a friendly and visually clear interface.

The project is a fully functional educational game with a structured quest system, condition checking, and protection against escaping the sandbox.

### 3. Clear Project Goals.

• Create an educational quest game for learning Linux file system commands.

• Implement a secure isolated sandbox for performing file operations.

• Implement a system of 9 sequential quests with completion checks.

• Provide support for the main commands: pwd, ls, cd, mkdir, touch, rm, cp, mv, cat, grep.

• Implement command-line emulation with a current working directory (cwd) and input handling.

• Implement colored output using ANSI colors to improve information readability.

• Prevent the player from escaping the sandbox (SANDBOX_ROOT).

• Implement a hint system (help, hint) to assist the player.

• Demonstrate an approach to developing educational console applications in Python.

### 4. Project Components.

The project consists of a single executable file that contains all components:

• **filer_quest.py** – the main script containing all game code: the color class, output functions, sandbox logic, quest system, command handler, and game loop.

• **fs_sandbox/** – the sandbox directory, created automatically when the game starts (contains the home, var, etc, tmp subdirectories and initial files).

### 5. Usage Instructions.

* **5.1. Launch:**

• No additional libraries are required — only standard Python modules (os, shutil, pathlib) are used.

• Run the script using Python (for example, from PyCharm or a terminal).

* **5.2. Game Objective:**

• Complete all 9 quests in sequence, with each quest teaching a new Linux command.

• Each quest contains a description, an expected command, and a completion check.

• After successfully completing a quest, the player proceeds to the next one.

* **5.3. Controls:**

• **Command input:** the player enters commands at the command prompt ($).

• **Enter:** confirms the command input.

• **Enter after success:** proceeds to the next quest.

• **exit:** exits the game at any time.

• **help:** displays the list of available commands.

• **hint:** displays a hint for the current task.

* **5.4. Supported Commands:**

• pwd – show the current path.

• ls – show the contents of the current directory.

• cd <path> – navigate to a directory (supports .., ~, absolute and relative paths).

• mkdir <name> – create a directory.

• touch <name> – create a file.

• rm <name> – delete a file.

• cp <source> <destination> – copy a file.

• mv <source> <destination> – move a file.

• cat <name> – read the contents of a file.

• grep <word> <file> – find lines containing the specified word.

• help – list available commands.

• hint – display a hint.

• exit – exit the game.

* **5.5. Interface:**

• Colored output using ANSI escape sequences:

* green – command prompt

* red – errors

* yellow – headers

* blue – quest titles

* cyan – message borders

* bold – emphasis

• Frames (print_box) for highlighting important messages.

• A title displaying the game name and automatically clearing the screen.

• The current directory displayed before entering a command.

• Progress: displays the current quest number (Quest N/9).

**5.6. Quest System:**

• **Quest 1:** pwd — find the current path.

• **Quest 2:** ls — view the contents of the directory.

• **Quest 3:** cd home — navigate to the home directory.

• **Quest 4:** cat readme.txt — read the instructions.

• **Quest 5:** mkdir projects — create a projects directory.

• **Quest 6:** touch projects/note.txt — create a note file.

• **Quest 7:** cat secret.key — find the secret key.

• **Quest 8:** mv var/log.txt home/ — move the log file.

• **Quest 9:** grep error home/log.txt — find the line containing the error.

## Part 2. Technical Document.

### 1. Development Goals.

• The primary goal of the project was to create an educational console application for learning the basic Linux file system commands in a game-based format.

• Additionally, the project focuses on learning how to work with the file system using the pathlib, os, and shutil modules, as well as learning how to implement colored terminal output using ANSI escape sequences.

• The tasks included implementing a secure sandbox, command-line emulation, a quest system with completion checks, and protection against escaping the working directory.

### 2. Technologies Used.

• **Programming Language:** Python

• **Standard Libraries:**

* os – for clearing the screen and detecting the operating system.

* shutil – for recursively deleting and copying files.

* pathlib – for convenient path handling (Path).

* ANSI escape sequences for colored terminal output (Colors class).

### 3. Project Architecture.

• The project is implemented as a monolithic console application with a game loop.

• Main loop: while level < len(QUESTS): — iterates through all quests sequentially.

• The logic is divided into functional blocks:

• Initialization and configuration (setup_sandbox, clear_screen, print_box, print_header).

• Command handler (run_command).

• Quest system (QUESTS list).

• Game loop (play).

• Each quest follows the same process: display the task, wait for input, process the command, check the condition, and proceed to the next quest.

### 4. Project Structure.

• **Initialization:** definition of the Colors class, output functions (clear_screen, print_box, print_header), and the SANDBOX_ROOT constant.

• **Global Variables:** SANDBOX_ROOT (path to the sandbox), read_files (set of files that have been read), QUESTS (list of quests).

• **Setup Functions:**

* setup_sandbox() – creates the sandbox with its initial structure.

* get_current_path(cwd) – returns the relative path.

• **Output Functions:**

* clear_screen() – clears the screen.

* print_box(text, color) – displays text inside a frame.

* print_header() – displays the game header.

• **Command Handler:**

* run_command(cmd, cwd) – the main command dispatcher, returning a tuple (ok, msg, new_cwd).

• **Game Loop:**

* play() – the main game loop.

* Entry point: if **name** == "**main**": – starts the game.

### 5. Key System Components.

• **Sandbox (SANDBOX_ROOT):** An isolated ./fs_sandbox directory created at startup. It contains the home, var, etc, and tmp subdirectories, as well as initial files (readme.txt, log.txt, config.ini, draft.txt, secret.key, backup.tar).

• **Quest System (QUESTS):** A list of dictionaries, each containing:

* id – quest number.

* title – title.

* description – task description.

* expected_cmd – expected command (for reference).

* check – lambda function used to check completion.

* success – success message.

• **Command Handler (run_command):** A command dispatcher implemented using an if/elif chain. Returns a tuple (success, message, new_directory).

• **Read File Tracking (read_files):** A set of strings containing absolute paths to files that the player has read using cat or grep.

• **Colored Output:** The Colors class containing ANSI codes for different colors and styles.

• **Sandbox Protection:** The new_cwd.relative_to(SANDBOX_ROOT) check prevents the player from escaping the working directory.

### 6. User Interface Implementation.

• The interface is fully implemented using standard terminal capabilities.

• Main elements: command prompt ($), message frames, colored text, and a header with automatic screen clearing.

• Output is handled using print() with ANSI codes.

• Input is handled using input().

### 7. Development Process.

Development was carried out in several stages:

• creation of the Colors class and colored output functions;

• implementation of screen clearing and the header;

• creation of the sandbox with its initial structure;

• development of the command handler (run_command);

• implementation of the basic commands: pwd, ls, cd;

• addition of file-related commands: mkdir, touch, rm, cat;

• addition of cp, mv, grep;

• implementation of sandbox protection;

• development of the quest list (QUESTS) with completion checks;

• implementation of the game loop (play) with transitions between quests;

• addition of the hint system (help, hint).

### 8. Main Challenges and Solutions.

• **(1) Challenge:** performing file operations safely without risking the real system.

**Solution:** creating an isolated SANDBOX_ROOT sandbox and using relative_to() checks for all paths.

• **(2) Challenge:** correctly handling relative and absolute paths in cd.**Solution:** supporting .., ~, paths starting with /, and relative paths using Path.resolve().

• **(3) Challenge:** checking quest completion without relying strictly on the entered command.

**Solution:** using lambda functions check(cwd, files) that check the state of the file system rather than the command entered by the player.

• **(4) Challenge:** tracking whether the player actually read a file.

**Solution:** using the read_files set, which stores paths when cat or grep is executed.

• **(5) Challenge:** implementing colored output across different operating systems.

**Solution:** using ANSI escape sequences (supported by modern Windows, Linux, and macOS terminals).

• **(6) Challenge:** handling errors during file operations.

**Solution:** wrapping the run_command logic in a try/except block and returning a clear error message.

### 9. Current Project Limitations.

• No progress saving between launches.

• No scoring or ranking system.

• Limited set of commands (basic commands only).

• No support for file permissions (chmod, chown).

• No interactive hints while entering commands (autocomplete).

• The code remains monolithic (not separated into modules).

• No support for other shells (bash, zsh) — emulation only.

### 10. Potential Improvements and Future Development.

• Refactoring the code (splitting it into modules: commands.py, quests.py, ui.py).

• Adding progress saving to a JSON file.

• Expanding the quest list (file permissions, archives, find search).

• Adding a scoring system and leaderboard.

• Implementing interactive documentation (man-like).

• Adding Tab command autocomplete.

• Supporting multiple difficulty levels.

• Adding a "free sandbox" mode without quests.
