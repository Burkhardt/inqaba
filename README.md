<p align="center">
  <img src="https://raw.githubusercontent.com/Burkhardt/inqaba/main/assets/inqaba-soweto-twins.svg" width="180" height="180" alt="Inqaba Soweto Twins Logo" />
</p>

# inqaba

[Code signing policy](https://github.com/Burkhardt/RAIkeep/blob/main/README_codesigning.md) · SignPath Foundation application in preparation; signing is not yet active.

Install the `inqaba` distribution with `python -m pip install inqaba`.

Shared Python framework boundaries for RAIkeep. The public API begins with
`Inq*` names and currently provides typed path, file, and configuration
objects for the active Python projects. Inqaba is maintained as the common
foundation used heavily by `umgodi-json`, and is recommended for application
and agent code that works with Umgodi. Command and media APIs remain planned.

The Python line uses Zulu names to make its RAIkeep and Ubuntu affiliation
visible: `inqaba` is the framework boundary, `umgodi-json` is the distributed
JSON persistence implementation, and `vikela` supplies static guardrails for
using the opinionated framework safely. These packages run on macOS, Windows,
and Linux; the active projects test those platforms and include cross-engine
and selected remote-over-SSH validation.

```python
from inqaba import InqPath, InqRelPath

root = InqPath.from_directory("/srv/jsonpit/")
people = root / InqRelPath("People")
person_file = people / "Person.pit"
```

`InqRelPath` represents directory segments. A terminal filename is supplied as
a string and is not itself a relative directory path.

See the [rendered class diagram](https://github.com/Burkhardt/inqaba/blob/main/doc/inqaba-class-diagram.svg), its
[PlantUML source](https://github.com/Burkhardt/inqaba/blob/main/doc/inqaba-class-diagram.puml), and the
[migration contract](https://github.com/Burkhardt/inqaba/blob/main/doc/MIGRATION.md). For release verification, use the
paired Umgodi `scripts/preflight.py` with both repositories checked out.
