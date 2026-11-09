<p align="center">
  <img src="https://raw.githubusercontent.com/Burkhardt/inqaba/main/assets/inqaba-soweto-twins.svg" width="180" height="180" alt="Inqaba Soweto Twins Logo" />
</p>

# inqaba

Shared Python framework boundaries for RAIkeep. The public API begins with
`Inq*` names and provides typed path, file, configuration, command, and media
objects for the active Python projects.

```python
from inqaba import InqPath, InqRelPath

root = InqPath.from_directory("/srv/jsonpit/")
people = root / InqRelPath("People")
person_file = people / "Person.pit"
```

`InqRelPath` represents directory segments. A terminal filename is supplied as
a string and is not itself a relative directory path.
