#!/usr/bin/env python3

# TODO(dkorolev): Bugfix that `pls c[lean]` should not try to install any deps!
# TODO(dkorolev): Make top-level symlinks relative, not absolute!
# TODO(dkorolev): Add that cache file, to know when to re-scan the sources and when to re-install the deps.

# REMAINS FOR v0.0.1 to be "complete":
# * Generate the `CMakeLists.txt` if not exists.
# * Provide the `pls.h` file by this tool.
# * Wrap each dependency into a singleton.
# * Basic tests, and a Github action running them.
# * During the call to `pls clean` it should not `git clone` anything; need to use some state/cache file!

# TODO(dkorolev): Add `setup.py` so that `pls` can be installed into the system via `pip3 install pls`.
# TODO(dkorolev): Test `--dotpls` for real.
# TODO(dkorolev): Should `.debug` and `.release` be symlinks to `.pls/.debug` and `.pls/.release`?
# TODO(dkorolev): CMAKE_BUILD_TYPE, NDEBUG, and test for these.
# TODO(dkorolev): Add `pls runwithcoredump` ?
# TODO(dkorolev): Check for broken symlinks, they need to be re-cloned.
# TODO(dkorolev): Figure out bash/zsh completion.

import os
import sys
import subprocess
import argparse
import json
from collections import deque
from collections import defaultdict
from dataclasses import dataclass, field

parser = argparse.ArgumentParser(description="PLS: The trivial build system for C++ and beyond, v0.01")
parser.add_argument("--verbose", "-v", action="store_true", help="Increase output verbosity")
parser.add_argument("--dotpls", type=str, default=".pls", help="The directory to use for output if not `./.pls`.")
flags, cmd = parser.parse_known_args()

if os.getenv("PLS_VERBOSE") is not None:
    flags.verbose = True

def safe_readlink(path):
    try:
        return os.readlink(path)
    except OSError:
        return path

def safe_get_base_dir_for_static(file, resolved_file):
    # NOTE(dkorolev): This works for all four cases:
    # 1) when `pls` is installed via `pip`,
    # 2) when `pls` is a symlink in some `/usr/local/bin/pls`,
    # 3) when invoking `pls` via absolute path, i.e. `~/github/dkorolev/pls/pls/pls version`, and
    # 4) when invoking `pls` via a relative path, i.e. `../pls/pls/pls version`.
    resolved_dir = os.path.dirname(resolved_file)
    return resolved_dir if resolved_dir else os.path.dirname(file)

base_dir = safe_get_base_dir_for_static(__file__, safe_readlink(__file__))
self_static_dir = os.path.join(base_dir, "static")


def read_static_file(fn):
    with open(os.path.join(self_static_dir, fn)) as file:
        return file.read()


version = read_static_file('version').strip()

# To clone git repos from a local path, not Github, for faster tests, for more reproducibility, and not to spam Github.
# TODO(dkorolev): Probably look in `..`, and/or in the dir(s) specified in `pls.json`.
github_https_prefix = "https://github.com/"
injected_github_path = os.getenv("PLS_INJECT_GITHUB")
if injected_github_path:
    injected_github_path = f"file://{injected_github_path}"

pls_h_dir = f"{flags.dotpls}/pls_h_dir"
pls_h = os.path.join(pls_h_dir, "pls.h")
pls_h_contents = read_static_file("dot_pls/pls_h_dir/pls.h")

cc_instrument_sh = f"{flags.dotpls}/cc_instrument.sh"
cc_instrument_sh_contents = read_static_file("dot_pls/cc_instrument.sh")

git_clone_sh = f"{flags.dotpls}/git_clone.sh"
cc_git_clone_sh_contents = read_static_file("dot_pls/git_clone.sh")

pls_export_gdb_or_lldb_sh = f"{flags.dotpls}/export_gdb_or_lldb.sh"
pls_export_gdb_or_lldb_sh_contents = read_static_file("dot_pls/export_gdb_or_lldb.sh")


def singleton_cmakelists_txt_contents(lib_name):
    lib_name_uppercase = lib_name.upper()
    return f"""cmake_minimum_required(VERSION 3.14.1)
project(singleton_{lib_name_uppercase} C CXX)
get_property(VALUE GLOBAL PROPERTY "HAS_SINGLETON_LIBRARY_{lib_name_uppercase}")
if(NOT VALUE)
  set_property(GLOBAL PROPERTY "HAS_SINGLETON_LIBRARY_{lib_name_uppercase}" TRUE)
  add_subdirectory(impl)
endif()
"""


def pls_fail(msg):
    # TODO(dkorolev): Write the failure message to an env-provided file, for "unit"-testing `pls`.
    print(msg)
    sys.exit(1)


def check_not_in_pls_dir():
    if os.path.isfile("pls.py") or os.path.isfile("pls"):
        pls_fail("PLS: You are probably running `pls` from the wrong directory. Navigate to your project directory first.")

modules = {}


@dataclass
class PerDirectoryStatus:
    deps: set = field(default_factory=lambda: set())
    project_name: str = "pls_project"
    executables: dict = field(default_factory=dict)
    executable_deps: defaultdict = field(default_factory=lambda: defaultdict(set))
    add_to_gitignore = []
    need_cmakelists_txt: bool = False


per_dir = defaultdict(PerDirectoryStatus)

full_abspath = os.path.abspath(".")
per_dir[full_abspath].add_to_gitignore.append(flags.dotpls)
per_dir[full_abspath].add_to_gitignore.append(".debug")
per_dir[full_abspath].add_to_gitignore.append(".release")


def create_symlink_with_cmakelists_txt(dst_dir, lib_name, lib_cloned_dir):
    # TODO(dkorolev): Creating the symlink should involve the `.gitignore` magic.
    final_dst_path = os.path.join(dst_dir, lib_name)
    if not os.path.isdir(final_dst_path):
        wrapper_top_dir = os.path.join(flags.dotpls, "singleton_deps")
        # TODO(dkorolev): So, the top-level symlinks created can be relative paths, the rest should be absolute. Fix this.
        wrapper_dir = os.path.join(os.path.abspath(wrapper_top_dir), lib_name)
        os.makedirs(wrapper_dir, exist_ok=True)
        wrapper_dir_impl = os.path.join(wrapper_dir, "impl")
        if not os.path.isdir(wrapper_dir_impl):
            os.symlink(os.path.abspath(lib_cloned_dir), wrapper_dir_impl, target_is_directory=True)
        os.symlink(wrapper_dir, final_dst_path, target_is_directory=True)
        cmakelists_path = os.path.join(wrapper_dir, "CMakeLists.txt")
        if not os.path.isfile(cmakelists_path):
            with open(cmakelists_path, "w") as file:
                file.write(singleton_cmakelists_txt_contents(lib_name))


already_traversed_src_dirs = set()


def traverse_source_tree(src_dir="."):
    # TODO(dkorolev): Traverse recursively.
    # TODO(dkorolev): `libraries`? And a command to `run` them, if only with `objdump -s`?
    queue_list = deque()
    queue_set = set()

    def add_to_queue(src_dir):
        abs_src_dir = os.path.abspath(src_dir)
        queue_list.append(abs_src_dir)
        queue_set.add(abs_src_dir)

    add_to_queue(src_dir)
    while queue_list:
        src_dir = queue_list.popleft()
        if src_dir not in already_traversed_src_dirs and (src_dir == "." or os.path.isdir(src_dir)):
            if flags.verbose:
                print(f"PLS: Analyzing `{src_dir}`.")
            libs_to_import = set()
            already_traversed_src_dirs.add(src_dir)
            pls_json_path = os.path.join(src_dir, "pls.json")
            if os.path.isfile(pls_json_path):
                pls_json = None
                with open(pls_json_path, "r") as file:
                    try:
                        pls_json = json.loads(file.read())
                    except json.decoder.JSONDecodeError as e:
                        pls_fail(f"PLS: Failed to parse `{pls_json_path}`: {e}.")
                if "import" in pls_json:
                    for lib, repo in pls_json["import"].items():
                        # TODO(dkorolev): Fail on branch mismatch.
                        modules[lib] = repo
                        libs_to_import.add(lib)

            def process_sources_in_dir(true_src_dir, prefix=""):
                for src_name in os.listdir(true_src_dir):
                    if src_name.endswith(".cc"):
                        executable_name = src_name.rstrip(".cc")
                        # TODO(dkorolev): This looks like a terrible hack, but would do for now.
                        if not "lib_" in executable_name and not "_lib" in executable_name:
                            per_dir[src_dir].executables[executable_name] = prefix + src_name
                        pls_commands = []
                        full_src_name = os.path.join(true_src_dir, src_name)
                        result = subprocess.run(
                            [
                                "bash",
                                cc_instrument_sh,
                                full_src_name,
                                os.path.join(os.path.abspath(flags.dotpls), "pls_h_dir"),
                            ],
                            capture_output=True,
                            text=True,
                        )
                        for line in result.stdout.split("\n"):
                            stripped_line = line.rstrip(";").strip()
                            if stripped_line:
                                try:
                                    pls_commands.append(json.loads(stripped_line))
                                except json.decoder.JSONDecodeError as e:
                                    pls_fail(
                                        f"PLS internal error: Can not parse `{stripped_line}` while processing `{full_src_name}`."
                                    )
                        for pls_cmd in pls_commands:
                            if "pls_project" in pls_cmd:
                                # TODO(dkorolev): Parse the project name from `pls.json` as well.
                                per_dir[src_dir].project_name = pls_cmd["pls_project"]
                            elif "pls_import_deprecate_me" in pls_cmd:
                                pls_import = pls_cmd["pls_import"]
                                if "lib" in pls_import and "repo" in pls_import:
                                    # TODO(dkorolev): Add branches. Fail if they do not match while installing the dependencies recursively.
                                    # TODO(dkorolev): Maybe create and add to `#include`-s path the `pls.h` file from this tool?
                                    # TODO(dkorolev): Variadic macro templates for branches.
                                    lib, repo = pls_import["lib"], pls_import["repo"]
                                    modules[lib] = repo
                                    libs_to_import.add(lib)
                                    per_dir[src_dir].executable_deps[executable_name].add(lib)
                            elif "pls_use_current" in pls_cmd:
                                if pls_cmd["pls_use_current"]:
                                    modules["C5T"] = "https://github.com/C5T/current"
                                    libs_to_import.add("C5T")
                                    per_dir[src_dir].executable_deps[executable_name].add("C5T")

            process_sources_in_dir(src_dir)
            src_src_dir = os.path.join(src_dir, "src")
            if os.path.isdir(src_src_dir):
                process_sources_in_dir(src_src_dir, "src/")
            for lib in libs_to_import:
                print(f"PLS: Requirement `{lib}` from `{src_dir}`.")
                per_dir[src_dir].deps.add(lib)
            for lib in libs_to_import:
                if lib not in queue_set:
                    add_to_queue(os.path.join(flags.dotpls, "deps", lib))
                    repo = modules[lib]
                    lib_dir = f"{flags.dotpls}/deps/{lib}"
                    if os.path.isdir(os.path.join(src_dir, lib)):
                        if flags.verbose:
                            print(f"PLS: Has symlink to `{lib}`, will use it.")
                    else:
                        if not os.path.isdir(lib_dir):
                            if flags.verbose:
                                print(f"PLS: Need to clone `{lib}` from `{repo}`.")
                            if injected_github_path and repo.startswith(github_https_prefix):
                                new_repo = f"{injected_github_path}/{repo[len(github_https_prefix):]}"
                                if flags.verbose:
                                    print(f"PLS: Injecting `{repo}` -> `{new_repo}`.")
                                repo = new_repo
                            result = subprocess.run(["bash", git_clone_sh, repo, lib])
                            if result.returncode != 0:
                                pls_fail(f"PLS: Clone of {repo} failed.")
                            per_dir[full_abspath].add_to_gitignore.append(lib)
                        else:
                            if flags.verbose:
                                print(f"PLS: Has module `{lib}`, will use it.")
                        if not os.path.isdir(lib_dir):
                            pls_fail(f"PLS internal error: repl {repo} cloned into {lib}, but can not be located.")
                        create_symlink_with_cmakelists_txt(dst_dir=".", lib_name=lib, lib_cloned_dir=lib_dir)
                        create_symlink_with_cmakelists_txt(dst_dir=src_dir, lib_name=lib, lib_cloned_dir=lib_dir)


def update_dependencies():
    if os.path.isfile("CMakeLists.txt"):
        if flags.verbose:
            print("PLS: Has `CMakeLists.txt`, will use it.")
    else:
        if flags.verbose:
            print("PLS: No `CMakeLists.txt`, will generate it, and will add it to `.gitignore`.")
        per_dir[full_abspath].need_cmakelists_txt = True
        per_dir[full_abspath].add_to_gitignore.append("CMakeLists.txt")

    # TODO(dkorolev): A better name for this function.
    def apply_gitignore_changes_and_more():
        for full_dir, full_dir_data in per_dir.items():
            if full_dir_data.need_cmakelists_txt:
                # TODO(dkorolev): Libraries would work too, not just executables.
                if not full_dir_data.executables:
                    pls_fail("PLS: To run `pls install/build/run` please make sure to have at least one source file.")
                with open(os.path.join(full_dir, "CMakeLists.txt"), "w") as file:
                    file.write("# NOTE: This `CMakeLists.txt` is autogenerated by `pls`.\n")
                    file.write("#       It is perfectly OK to edit, if only to remove this header.\n")
                    # TODO(dkorolev): Time to introduce `.pls/cache.json`, at least to keep track of which `CMakeLists.txt`-s to clean!
                    file.write(
                        "#       Just keep in mind that a) it is `.gitignore`-d now, and b) it will be deleted on `pls clean`.\n"
                    )
                    file.write("\n")
                    file.write("cmake_minimum_required(VERSION 3.14.1)\n")
                    file.write("\n")
                    file.write(f"project({full_dir_data.project_name} C CXX)\n")
                    file.write("\n")
                    file.write("set(CMAKE_CXX_STANDARD 17)\n")
                    file.write("set(CMAKE_CXX_STANDARD_REQUIRED True)\n")
                    file.write("\n")
                    file.write('# This is for `#include "pls.h"` to work.\n')
                    file.write('include_directories("${CMAKE_SOURCE_DIR}/.pls/pls_h_dir/")\n')
                    if full_dir_data.deps:
                        file.write("\n")
                        for dep in full_dir_data.deps:
                            file.write(f"add_subdirectory({dep})\n")
                    if full_dir_data.executables:
                        for exe, src in full_dir_data.executables.items():
                            file.write("\n")
                            file.write(f"add_executable({exe} {src})\n")
                            if exe in full_dir_data.executable_deps:
                                libs = " ".join(sorted(list(full_dir_data.executable_deps[exe])))
                                file.write(f"target_link_libraries({exe} { libs })\n")
            gitignore_lines = sorted(full_dir_data.add_to_gitignore)
            gitignore_file = os.path.join(full_dir, ".gitignore")
            skip_this_gitignore = False
            need_newline_in_gitignore = False
            all_lines = set(gitignore_lines)
            present = set()
            if os.path.isfile(gitignore_file):
                need_newline_in_gitignore = True
                with open(gitignore_file, "r") as file:
                    for line in file:
                        s = line.strip().rstrip("/")
                        if s in all_lines:
                            present.add(s)
                if len(all_lines) == len(present):
                    if flags.verbose:
                        print(f"PLS: Everything is as it should be in `{gitignore_file}`.")
                    skip_this_gitignore = True
                else:
                    if flags.verbose:
                        print(f"PLS: Adding missing lines to `{gitignore_file}`.")
            else:
                if flags.verbose:
                    print(f"PLS: Creating `{gitignore_file}`.")
            if not skip_this_gitignore:
                lines = []
                if need_newline_in_gitignore:
                    lines.append("\n")
                lines.append("# Added automatically by `pls`. Okay to push to git.\n")
                for line in gitignore_lines:
                    if line not in present:
                        lines.append(f"{line}\n")
                with open(gitignore_file, "a") as file:
                    file.writelines(lines)

    os.makedirs(flags.dotpls, exist_ok=True)

    if not os.path.isfile(cc_instrument_sh):
        with open(cc_instrument_sh, "w") as file:
            file.write(cc_instrument_sh_contents)
        os.chmod(cc_instrument_sh, 0o755)

    if not os.path.isfile(git_clone_sh):
        with open(git_clone_sh, "w") as file:
            file.write(cc_git_clone_sh_contents)
        os.chmod(git_clone_sh, 0o755)

    if not os.path.isfile(pls_export_gdb_or_lldb_sh):
        with open(pls_export_gdb_or_lldb_sh, "w") as file:
            file.write(pls_export_gdb_or_lldb_sh_contents)
        os.chmod(pls_export_gdb_or_lldb_sh, 0o755)

    if not os.path.isdir(pls_h_dir):
        os.makedirs(pls_h_dir, exist_ok=True)
    if not os.path.isfile(pls_h):
        with open(pls_h, "w") as file:
            file.write(pls_h_contents)

    traverse_source_tree()

    # TODO(dkorolev): Exclude the manually-added symlinks to the libraries, in `static/.vscode/settings.json`.
    if not os.path.isdir(".vscode"):
        if flags.verbose:
            print("PLS: Adding `.vscode` to `.gitignore`, as it was not here before.")
        per_dir[full_abspath].add_to_gitignore.append(".vscode")
    os.makedirs(".vscode", exist_ok=True)
    self_static_vscode_dir = os.path.join(self_static_dir, "dot_vscode")
    for dot_vs_code_static_file in os.listdir(self_static_vscode_dir):
        dst_static_file = os.path.join(".vscode", dot_vs_code_static_file)
        if not os.path.isfile(dst_static_file):
            with open(dst_static_file, "w") as file:
                file.write(read_static_file(os.path.join(self_static_vscode_dir, dot_vs_code_static_file)))

    apply_gitignore_changes_and_more()


if __name__ == "__main__" and not cmd:
    # TODO(dkorolev): Differentiate between debug and release?
    # TODO(dkorolev): The "selfupdate" command, in case `pls` is `alias`-ed into a cloned repo?
    # TODO(dkorolev): `test` to run the tests, and also `release_test`.
    print("PLS: Requires a command, the most common ones are `build`, `run`, `clean`, and `version`.")
    sys.exit(0)


def cmd_version(unused_args):
    print(f"PLS {version} NOT READY YET")


def cmd_clean(args):
    check_not_in_pls_dir()
    traverse_source_tree()
    previously_broken_symlinks = set()
    for lib, _ in modules.items():
        if os.path.islink(lib):
            if not os.path.exists(os.readlink(lib)):
                previously_broken_symlinks.add(lib)
    result = subprocess.run(["rm", "-rf", ".pls", ".debug", ".release"])
    for lib, _ in modules.items():
        if os.path.islink(lib) and not os.path.exists(os.readlink(lib)) and not lib in previously_broken_symlinks:
            if flags.verbose:
                print(f"PLS: Unlinking the now-broken link to `{lib}`.")
            os.unlink(lib)
    if result.returncode != 0:
        pls_fail("PLS: Could not clean the build.")
    if flags.verbose:
        print("PLS: Clean successful.")


def cmd_install(args):
    check_not_in_pls_dir()
    update_dependencies()
    if flags.verbose:
        print("PLS: Dependencies cloned successfully.")


def cmd_build(args):
    check_not_in_pls_dir()
    update_dependencies()
    # TODO(dkorolev): Debug/release.
    result = subprocess.run(["cmake", "-B", ".debug", f"-DCMAKE_CXX_FLAGS=-I{os.path.abspath(pls_h_dir)}"])
    if result.returncode != 0:
        pls_fail("PLS: cmake configuration failed.")
    result = subprocess.run(["cmake", "--build", ".debug"])
    if result.returncode != 0:
        pls_fail("PLS: cmake build failed.")
    if flags.verbose:
        print("PLS: Build successful.")


def cmd_run(args):
    check_not_in_pls_dir()
    cmd_build([])
    # TODO(dkorolev): Forward the command line? And test it?
    executables = per_dir[os.path.abspath(".")].executables
    if not args:
        if len(executables) == 1:
            result = subprocess.run([f"./.debug/{next(iter(executables.keys()))}"])
        else:
            pls_fail(
                f"PLS: Has more than one executable, specify the name direcly, one of {json.dumps(list(executables.keys()))}."
            )
    else:
        if args[0] in executables:
            result = subprocess.run([f"./.debug/{args[0]}"])
        else:
            pls_fail(f"PLS: Executable `{args[0]}` is not in {json.dumps(list(executables.keys()))}.")


def main():
    cmds = {}
    cmds["version"] = cmd_version
    cmds["v"] = cmd_version
    cmds["clean"] = cmd_clean
    cmds["c"] = cmd_clean
    cmds["install"] = cmd_install
    cmds["i"] = cmd_install
    cmds["build"] = cmd_build
    cmds["b"] = cmd_build
    cmds["run"] = cmd_run
    cmds["r"] = cmd_run

    cmd0 = cmd[0].strip().lower() if cmd else ""
    if cmd0 in cmds:
        cmds[cmd0](cmd[1:])
    else:
        print(f"PLS: The command `{cmd0}` is not recognized, try `pls --help`.")
        sys.exit(0)


if __name__ == "__main__":
    main()
