#!/usr/bin/env python3
"""Linux Quest: guided terminal RPG with safe simulated commands."""
import posixpath
import shlex

WORLD = {
    '/home/hero': {'type': 'dir', 'children': ['village', 'forest', 'castle']},
    '/home/hero/village': {'type': 'dir', 'children': ['welcome.txt']},
    '/home/hero/village/welcome.txt': {'type': 'file', 'text': 'Find the hidden map in the forest. Use cat to read it.'},
    '/home/hero/forest': {'type': 'dir', 'children': ['map.txt']},
    '/home/hero/forest/map.txt': {'type': 'file', 'text': 'The map reveals the castle entrance. Return to the castle!'},
    '/home/hero/castle': {'type': 'dir', 'children': ['tower']},
    '/home/hero/castle/tower': {'type': 'dir', 'children': ['treasure.txt']},
    '/home/hero/castle/tower/treasure.txt': {'type': 'file', 'text': 'You found the treasure! The dungeon is yours.'},
}

QUESTS = [
    ('WHERE AM I?', 'Find your current working directory.', 'The command has three letters and means Print Working Directory.', 'pwd', 'pwd prints your current location.'),
    ('LOOK AROUND', 'List the files and directories around you.', 'The command is short for list.', 'ls', 'ls displays directory contents.'),
    ('ENTER THE FOREST', 'Travel into the forest directory.', 'Use cd followed by the directory name.', 'cd forest', 'cd changes your working directory.'),
    ('FIND THE MAP', 'List the contents of the forest.', 'Use the same two-letter listing command from Quest 2.', 'ls', 'You can use ls in any directory.'),
    ('READ THE MAP', 'Print the contents of map.txt.', 'Use cat followed by the filename.', 'cat map.txt', 'cat displays text stored in a file.'),
    ('RETURN TO THE CROSSROADS', 'Move up one directory.', 'Two dots (..) represent the parent directory.', 'cd ..', 'cd .. moves to the parent directory.'),
    ('UNLOCK THE CASTLE', 'Enter the castle directory.', 'Use cd and the name of the castle.', 'cd castle', 'The map you read lets you pass the castle gate.'),
    ('CLIMB THE TOWER', 'Enter the tower directory.', 'Use cd followed by tower.', 'cd tower', 'You are now inside the castle tower.'),
    ('CLAIM THE TREASURE', 'Read treasure.txt to complete your adventure.', 'Use cat followed by treasure.txt.', 'cat treasure.txt', 'You have learned navigation and reading text files!'),
]

cwd = '/home/hero'
map_found = False
won = False
xp = 0
step = 0
mistakes = 0

def resolve(path):
    return posixpath.normpath(posixpath.join(cwd, path))

def show_quest():
    if step >= len(QUESTS):
        print('\n*** ALL QUESTS COMPLETE! *** Type status, help, or quit.')
        return
    name, mission, hint, _, _ = QUESTS[step]
    print('\n' + '=' * 49)
    print(f' QUEST {step + 1}/{len(QUESTS)}: {name}')
    print('=' * 49)
    print('MISSION:', mission)
    print('HINT:   ', hint)
    print('Enter a Linux command below. Type hint for more help.')

def run_command(args):
    global cwd, map_found, won, xp
    command, *rest = args
    if command == 'pwd':
        if rest:
            print('Usage: pwd')
            return False
        print(cwd)
        return True
    if command == 'ls':
        if len(rest) > 1:
            print('Usage: ls [directory]')
            return False
        target = resolve(rest[0]) if rest else cwd
        node = WORLD.get(target)
        if node is None:
            print('No such directory.')
            return False
        print('  '.join(node['children']) if node['type'] == 'dir' else posixpath.basename(target))
        return True
    if command == 'cd':
        if len(rest) > 1:
            print('Usage: cd [directory]')
            return False
        target = resolve(rest[0]) if rest else '/home/hero'
        node = WORLD.get(target)
        if node is None:
            print('No such directory.')
            return False
        if node['type'] != 'dir':
            print('Not a directory.')
            return False
        if target.startswith('/home/hero/castle') and not map_found:
            print('The castle gate is locked! Read the forest map first.')
            return False
        cwd = target
        if target == '/home/hero/castle':
            print('The castle gate opens!')
        return True
    if command == 'cat':
        if len(rest) != 1:
            print('Usage: cat <file>')
            return False
        target = resolve(rest[0])
        node = WORLD.get(target)
        if node is None:
            print('No such file.')
            return False
        if node['type'] != 'file':
            print('That is a directory.')
            return False
        print(node['text'])
        if target == '/home/hero/forest/map.txt' and not map_found:
            map_found = True
            print('ITEM FOUND: Lost Map!')
        if target == '/home/hero/castle/tower/treasure.txt' and not won:
            won = True
            print('TREASURE DISCOVERED!')
        return True
    print('Unknown game command. Real system commands are never executed.')
    return False

def main():
    global step, xp, mistakes
    print('\n' + '#' * 49)
    print('         LINUX QUEST: THE LOST MAP')
    print('       A BEGINNER LINUX COMMAND RPG')
    print('#' * 49)
    print('Practice commands safely in a simulated world.')
    print('Type help, hint, quest, status, inventory, or quit.')
    show_quest()
    while True:
        try:
            line = input(f'\nhero@quest:{cwd}$ ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nFarewell, adventurer!')
            break
        if not line:
            continue
        try:
            args = shlex.split(line)
        except ValueError as error:
            print('Input error:', error)
            continue
        if not args:
            continue
        command = args[0]
        if command in ('quit', 'exit'):
            print('Farewell, adventurer!')
            break
        if command == 'help':
            print('Linux: pwd, ls, cd [directory], cat [file]')
            print('Game: hint, quest, status, inventory, clear, help, quit')
            continue
        if command == 'quest':
            show_quest()
            continue
        if command == 'hint':
            if step < len(QUESTS):
                print('EXTRA HINT: Try typing:', QUESTS[step][3])
            else:
                print('All quests are complete!')
            continue
        if command == 'status':
            print(f'Level: {1 + xp // 100} | XP: {xp} | Completed: {step}/{len(QUESTS)}')
            continue
        if command == 'inventory':
            print('Items:', 'Lost Map' if map_found else '(empty)')
            continue
        if command == 'clear':
            print('\033[2J\033[H', end='')
            show_quest()
            continue
        # Only the expected command advances the tutorial, even if other valid commands work.
        expected = QUESTS[step][3] if step < len(QUESTS) else None
        correct_for_quest = expected is not None and args == expected.split()
        success = run_command(args)
        if success and correct_for_quest:
            explanation = QUESTS[step][4]
            xp += 10
            step += 1
            mistakes = 0
            print(f'\n[+] CORRECT! +10 XP | Total XP: {xp}')
            print('LEARN:', explanation)
            if step == len(QUESTS):
                xp += 60
                print('\n*** QUEST COMPLETE! BONUS +60 XP! ***')
                print(f'FINAL SCORE: {xp} XP | Level {1 + xp // 100}')
            else:
                show_quest()
        elif step < len(QUESTS):
            mistakes += 1
            if success:
                print('That command works, but it does not finish your current mission.')
            else:
                print('Not quite. Your mission is still active.')
            print('HINT:', QUESTS[step][2])
            if mistakes >= 2:
                print('Need the exact command? Type hint.')

if __name__ == '__main__':
    main()
