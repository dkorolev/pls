[![Self-test the HEAD](https://github.com/dkorolev/pls/actions/workflows/run_selftest.yml/badge.svg)](https://github.com/dkorolev/pls/actions/workflows/run_selftest.yml)

# `pls`

The build system for `CMakeLists.txt` projects, mostly C and C++. Designed for predictability and ease of use.

## Setup

You will need `pls` in your path. Cloning this repo and `alias`-ing it in your `.bashrc` / `.zshrc` would do.

Alternatively, if you have a Python environment set up, `pip3 install plsbuild` does the trick.

If `pls version` or `pls v` works, you're good.

You will also need the usual shenanigans of course, the C++ compiler and `cmake`.

## Links

For a quick start, scroll down to the Examples section. The more detailed manual is (`TODO(dkorolev)`: Links.):

* Goals, assumptions, and principles.
* Operational logic.
* The complete feature set.

## Examples

Most examples here assume an otherwise empty directory.

If this directory is a git repo (cloned, or `git init .`), the `.gitignore` magic will work its way too.

### Trivial

For the following `example.cc`:

```
#include <iostream>

int main() {
  std::cout << "Hello, World!" << std::endl;
}
```

Just running `pls build` and `pls run` would do exactly what you assume.

The binary will be created in `.debug/example` for `pls build`. Also, `TODO(dkorolev):` there should be a release target.

Note that these runs of `pls` will create a `CMakeLists.txt`, so that you can open your favorite CMake-aware IDE and run / trace into this code. VS Code would do just fine.

Also, if this `CMakeLists.txt` was created by `pls`, it will be added to `.gitignore`. If this is not the intended behavior, check it in, or just manually remove it from `.gitignore`. This would do.

The idea behind `pls` is that if the user intends to have a `CMakeLists.txt` file, this user-provided `CMakeLists.txt` file will be kept. If not, then the user likely does not want `CMakeLists.txt`, so the "trivial" boilerplate `CMakeLists.txt` that is being created should be treated as ephemeral. Simplicity first is key.

Also, by default `pls` looks into the root project directory and its `src/` subdirectory. Dirs beyond these two are non-standard, and require an explicit mention in `pls.json`, see below. `TODO(dkorolev):` Implement and test this.

### Dependency

Now, let's use a trivial dependency.

```
#include <iostream>

#include "pls.h"

PLS_IMPORT("trivial_cmake_lib", "https://github.com/dkorolev/trivial_cmake_lib");

#include "trivial_cmake_lib.h"

int main() {
  std::cout << "2+2=" << trivial_cmake_lib_add(2, 2) << std::endl;
}
```

This works as a standalone example, with `pls build` or `pls run`.

Besides, after the first run of `pls`, either `pls build` or `pls run`, the created `CMakeLists.txt` can be used with an IDE.

Note that you do not need the `"pls.h"` file. The `pls`-provided build setup handles this. `TODO(dkorolev):` Make sure it works for non-`pls` users to some day.

When it comes to where the `PLS_IMPORT` "directive" should go in the code, just make sure it takes place before `#include`-ing any headers from the libraries to be imported. Otherwise the preprocessor will fail on missing header files, will never get to processing the `PLS_IMPORT` statements, and the auto-import magic will not work.

The semicolon after `PLS_IMPORT` is optional.

Behind the scenes, in the "true" build, the `PLS_IMPORT` macro is only checking that the passed-in parameters are compile-time strings. During the build phase, the `PLS_IMPORT` directive is parsed differently, so that the dependencies are extracted by `pls`.

### The `pls.json` File

While `pls` strives for simplicity, `PLS_IMPORT()` in code is not the only, or even the recommended way to define dependencies.

The long-form way is to use the `pls.json` file:

```
{
  "import": {
    "trivial_cmake_lib": "https://github.com/dkorolev/trivial_cmake_lib"
  }
}
```

For toy projects, it is probably an overkill, sice `PLS_IMPORT()` would do the trick. If you are maintaining a library and a non-zero portion of your users are using `pls`, you may want to have a `pls.json` file.

Also, `TODO(dkorolev):` need to support some `pls add ...` command to add dependencies into `pls.json` automatically.

### Nested Dependencies

When running `pls build` (or `pls install`, or `pls b` or `pls i` for short), the dependencies will be installed recursively. They will be cloned into `.pls/deps`, symlinked into the root directory of the repository, and `.gitignore`-d accordingly.

Effectively, `pls`-installed dependencies are designed to be "included" straight away as `add_subdirectory(dep_name)` from the project's `CMakeLists.txt`. If the project does have its own `CMakeLists.txt`, it should require these dependencies as such. If it does not, the respective `CMakeLists.txt` will be created by `pls`, included in the project, and `.gitignore`-d, since it is meant to be ephemeral.

Recursively, if and when a particular respective dependency does not have the `CMakeLists.txt` file by itself, it will also be created the same way, as well as all the sub-dependencies for this particular dependency, if they are listed in the `.cc` file(s) via `PLS_IMPORT()`, or in the `pls.json` file directly.

The `pls` tool does not attempt to parse existing `CMakeLists.txt` files. When a dependency has the `CMakeLists.txt` file, `pls` assumes this is the terminal dependency that should be `add_subdirectory()`-d by itself.

`TODO(dkorolev):` To clone dependencies alongside it, to be used by this external library, we need some `"inject": ...` syntax in `pls.json`.

Also, when creating these dependencies, `pls` will wrap each and every one into a "singleton" `CMakeLists.txt`, with another layer of indirection via symlinking the `impl` directory. This is to make sure that if a dependency is used more than once, there are no errors on the `cmake` level.

### Remains To Do

* Test targets.
* Debug vs. release.
* Versioning and conflicts.
* Proper "unit" tests, Github actions, links to them.
* Branch protection so that I drop the habit of pushing straight into `main`. =)
