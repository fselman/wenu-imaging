# Native distribution options — 25 October 2026

Fernando requests a short user guide directly under docs, separation from detailed
developer qualification, and review of a shared Mac/Linux package manager before
continuing the observational comparison. No package manager is selected or installed
by this documentation change.

## Roles

CMake configures/builds/installs the source. find_package locates dependencies;
FetchContent can retrieve explicitly declared dependencies. Neither automatically
infers every missing package or provisions an OS/compiler. A dependency provider
can integrate a package manager. CPack generates installers/archives; it is not a
general dependency resolver. These tools complement a package manager.

The current native build already bundles Eclipse/qfits. Its build needs the C
compiler/toolchain, CMake/build tool and funpack for distributed BPM generation;
Python is a test dependency, not an installed mefpp runtime requirement. The full
Pycavi application has a different dependency set, including Python modules,
external astronomy executables and reference datasets. Do not conflate them.

## Candidates

| Tool | Relevant role | Assessment for this project |
|---|---|---|
| Conda / micromamba | Language-independent binary packages and isolated environments | Recommended first evaluation for user distribution: one native recipe plus a compatible Python/application environment; already familiar to Fernando |
| Conan | C/C++ package recipes, dependencies and binary packages, CMake integration | Strong candidate if the native library dependency graph grows; does not alone define the entire Pycavi application environment |
| vcpkg | C/C++ dependency ports/manifests and binary caching across Mac/Linux/Windows | Another native-development option; not a requirement merely because CMake is used |
| Spack | Scientific/HPC packages, compiler variants and environments | Particularly relevant to chapman3 and toolchain qualification; assess whether its operational overhead is justified for user distribution |
| CPack | Platform-specific installers/source or binary archives | Possible simple standalone mefpp delivery; package/dependency metadata, resources and relocation still need explicit implementation and tests |

One shared recipe/workflow does not mean one executable for every system. Build
separate artifacts for macOS Intel, macOS arm64 and Linux targets, then Windows
when its native support is qualified. Verify minimum OS/SDK and Linux glibc
compatibility; a current Linux binary is not automatically usable on chapman3's
glibc 2.17. Package-manager availability and recipe versions need actual target
qualification, not an assumed platform pass.

## Recommendation for review

Retain CMake/CTest as the canonical build/test layer. First evaluate a Conda
native-mefpp recipe and an environment definition for the full application,
consumable by Conda/micromamba. Keep the core C code and bundled numerical
libraries unchanged. Resolve dependencies declared by the recipe, not hidden
configure-time downloads or implicit changes to working environments.

The recipe must build/install using CMake and deliver executable, PAFs, already
uncompressed BPMs, original licenses and usable provenance. funpack can then be a
build dependency for mask preparation rather than an end-user runtime requirement.
Use supported platform variants and a controlled source/version identity. Review
prefix relocation and the existing prefix-sensitive manifest/installer before
claiming the current CMake payload is directly Conda-packageable.

For user acceptance, create a fresh environment from the package using only the
short documented commands. Verify dependency resolution, executable/resources,
relocation, installed functionality, removal/update behavior and unchanged working
installations on Mac and chapman3. Keep source builds available for developers.
Do not publish illustrative conda/micromamba commands as runnable installation
instructions before the recipe, channel and actual binaries exist. Assess which
external engines and indexes are packaged versus configured separately; a package
manager cannot supply an undeclared or unavailable dependency automatically.

This review is part of Stage 1 distribution usability, distinct from the completed
private source-install checks. It does not authorize toolchain upgrades, binary
publication, a new package manager installation or replacement of current engines.

## Documentation organization

- docs/installation.md: short user entry point and availability/prerequisites.
- docs/developer/installation.md: detailed Python installation.
- docs/developer/native-installation.md: detailed native build/install/qualification.
- docs/developer/README.md: topic-grouped developer index, current work first.
- Dated audits/corrections/pilots: evidence records, not the user install route.

Start by grouping navigation and removing competing user entry points. A later
physical reorganization into topical subdirectories should inventory inbound links
and update AGENTS, guides, historical references and indexes together, preserving
stable entry points. No bulk relocation of historical records is performed here.

## Official references checked for this review

- [CMake 3.29 dependencies](https://cmake.org/cmake/help/v3.29/guide/using-dependencies/index.html)
  and [CPack](https://cmake.org/cmake/help/v3.29/module/CPack.html).
- [Conda](https://docs.conda.io/), [non-Python packages](https://conda.org/learn/faq)
  and [recipe model](https://docs.conda.io/projects/conda-build/en/stable/concepts/recipe.html).
- [Micromamba](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html).
- [Conan](https://docs.conan.io/2/).
- [vcpkg](https://learn.microsoft.com/en-us/vcpkg/get_started/overview).
- [Spack](https://spack.readthedocs.io/en/latest/getting_started.html).
