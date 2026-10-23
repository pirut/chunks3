#!/usr/bin/env python3
"""Copies the cubic engine out of an Earth Platform checkout into this library.

Earth Platform keeps developing the engine (package io.earthplatform.minecraft.cubic, without its
earth, play and jet subpackages) until it switches over to depending on Chunks3. Until then this
script is how the library follows it: run it against an Earth checkout and commit the result.

    python3 tools/import_from_earth.py ../earth-platform

It replaces src/main/java/io/github/pirut/chunks3, the matching tests and the engine's resources,
renames the packages, the mod id, mixin names and -D flags, and keeps the names worlds have saved
on disk (portal data, player tags) as Earth Platform wrote them, so its worlds load unchanged.
"""
import os
import re
import shutil
import sys

ENGINE = 'io/earthplatform/minecraft/cubic'
LIBRARY = 'io/github/pirut/chunks3'
EARTH_ONLY = ('earth/', 'play/', 'jet/')
# Saved in worlds and player data: changing them would lose what Earth Platform worlds hold.
SAVED_NAMES = ['"earthplatform.cubic_home"', '"earthplatform_cubic_portals"',
               '"earthplatform:twilight_return"', '"earthplatform:aether_return"']


def transform(text):
    kept = {}
    for i, name in enumerate(SAVED_NAMES):
        token = '\0SAVED%d\0' % i
        kept[token] = name
        text = text.replace(name, token)
    text = text.replace('io.earthplatform.minecraft.cubic', 'io.github.pirut.chunks3')
    text = text.replace('public static final String MOD_ID = "earthplatform";', 'public static final String MOD_ID = "chunks3";')
    text = text.replace('earthplatform$', 'chunks3$')
    text = text.replace('earthplatform.cubic.mixins.json', 'chunks3.mixins.json')
    text = text.replace('"earthplatform.', '"chunks3.').replace('-Dearthplatform.', '-Dchunks3.')
    for token, name in kept.items():
        text = text.replace(token, name)
    return text


def copy_tree(earth, side):
    source = os.path.join(earth, 'minecraft/src', side, 'java', ENGINE)
    target = os.path.join('src', side, 'java', LIBRARY)
    if os.path.isdir(target):
        shutil.rmtree(target)
    copied = 0
    for folder, _, files in os.walk(source):
        relative = os.path.relpath(folder, source)
        relative = '' if relative == '.' else relative + '/'
        if relative.startswith(EARTH_ONLY):
            continue
        for name in files:
            if not name.endswith('.java'):
                continue
            with open(os.path.join(folder, name), encoding='utf-8') as f:
                text = transform(f.read())
            out = os.path.join(target, relative, name)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, 'w', encoding='utf-8') as f:
                f.write(text)
            copied += 1
    return copied


def copy_resources(earth):
    resources = os.path.join(earth, 'minecraft/src/main/resources')
    with open(os.path.join(resources, 'earthplatform.cubic.mixins.json'), encoding='utf-8') as f:
        config = transform(f.read())
    os.makedirs('src/main/resources/assets/chunks3/textures/block', exist_ok=True)
    with open('src/main/resources/chunks3.mixins.json', 'w', encoding='utf-8') as f:
        f.write(config)
    shutil.copyfile(os.path.join(resources, 'assets/earthplatform/textures/block/far_white.png'),
                    'src/main/resources/assets/chunks3/textures/block/far_white.png')


def check():
    leftovers = []
    for folder, _, files in os.walk('src'):
        for name in files:
            if name.endswith('.java') or name.endswith('.json'):
                path = os.path.join(folder, name)
                with open(path, encoding='utf-8') as f:
                    text = f.read()
                for line_number, line in enumerate(text.splitlines(), 1):
                    if re.search(r'io\.earthplatform|EarthPlatformMod', line):
                        leftovers.append('%s:%d: %s' % (path, line_number, line.strip()))
    if leftovers:
        sys.exit('Earth Platform names left over:\n' + '\n'.join(leftovers))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    earth = sys.argv[1]
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    main_files = copy_tree(earth, 'main')
    test_files = copy_tree(earth, 'test')
    copy_resources(earth)
    # The library's own entry point; Earth Platform's is its own mod class.
    with open('tools/Chunks3Mod.java.txt', encoding='utf-8') as f:
        mod_class = f.read()
    with open(os.path.join('src/main/java', LIBRARY, 'Chunks3Mod.java'), 'w', encoding='utf-8') as f:
        f.write(mod_class)
    check()
    print('Copied %d engine files and %d tests from %s' % (main_files, test_files, earth))


if __name__ == '__main__':
    main()
