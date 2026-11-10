# Filesystem and configuration boundary

Inqaba owns configuration discovery, the JSON5 subset parser, filesystem traversal,
and durable file writes. Umgodi consumes these APIs for CLI inputs, persistence,
flags, receipts, maintenance and audit.

`InqPath` represents an absolute directory. `InqRelPath` supplies relative
directory intent; `directory / InqRelPath("People/")` returns `InqPath`.
`directory / "Person.pit"` returns `InqFile`. No operator returns a raw pathlib
object. `as_path()` is the explicit interoperability escape hatch.

`InqEntry` is the common PathLike implementation and the adapter for CLI inputs
whose file/directory kind is not yet known. Enumeration produces typed directory
or file objects. Its filesystem methods are explicitly listed, with no dynamic
forwarding to pathlib. Domain APIs should choose InqPath or InqFile when known.

`InqConfig.load()` retains the previous Python discovery and fallback behavior.
Configured roots are InqPath objects. Umgodi's old OsConfig export is a compatibility
reference to this single implementation, not a second singleton. JSON5 parsing
supports the prior Python subset; it does not claim full JSON5 conformance.

Canonical writes use `write_durable()`: truncate/write/flush/fsync at the existing
pathname. Sibling temporary replacement remains a separate explicit operation.

This migration covers the filesystem/configuration boundary. It does not yet
implement the complete C# OsLib, RaiUtils and RaiImage surface or their full
cloud-operation restrictions.

Regenerate the class inventories with `scripts/class_diagram.py`, then render
with PlantUML. The diagrams describe actual source classes and inheritance.
