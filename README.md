# nanopore-tools

## squiggle matching tools Roadmap

This roadmap outlines our plan to focus on creating Docker containers for a variety of tools dedicated to signal matching, commonly known as squiggle matching. These tools are essential for analyzing raw signal data in genomics and other fields. Below are the tools we plan to work on, with links to their respective repositories or relevant resources, where applicable.

### Mapping

#### Rawalign
[Rawalign](https://github.com/CMU-SAFARI/RawAlign) 

#### UNCALLED (different from UNCALLED4)
[UNCALLED](https://github.com/skovaka/UNCALLED)

#### UNCALLED 4
[UNCALLED 4](https://github.com/skovaka/uncalled4)

#### Sigmap
[SigMap](https://github.com/haowenz/sigmap)

#### RawHash
[RawHash](https://github.com/CMU-SAFARI/RawHash) 

### Classification

#### Sigmoni
[Sigmoni](https://github.com/vshiv18/sigmoni).

#### BaseLess
[BaseLess](https://github.com/cvdelannoy/baseLess)

#### SquiggleNet
[SquiggleNet](https://github.com/welch-lab/SquiggleNet)

#### ReadCurrent
[ReadCurrent](https://github.com/Ming-Ni-Group/ReadCurrent)

#### RISER
[RISER](https://github.com/comprna/riser)


## 🐳 Docker Tag Format

Some Docker image is tagged with:

* The version of the tool (from its Git history)
* The version of the main repo: [`SquiDBase/nanopore-tools`](https://github.com/SquiDBase/nanopore-tools)

### 🔖 Format

```
haliliceylanua/<tool-name>:<tool-version>-<main-repo-commit>
```

### 🧪 Example

```
haliliceylanua/uncalled:v2.3-3-g58dbec6-9e989bb
```

### 🔍 Breakdown

* `v2.3-3-g58dbec6`: from the tool’s Git (e.g., `UNCALLED`)

  * 3 commits after tag `v2.3`
  * Commit `58dbec6`
* `9e989bb`: commit from `nanopore-tools` (main repo)
