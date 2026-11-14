# Contributing

Make one view more useful, then show how you checked it.

Run the standard-library tests from the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 skills/seat-view/scripts/build.py --demo --output ./preview-test
```

Open the output at desktop and phone widths; check the overview, every seat view, source panel, and PNG export. For changes affecting Blender, export the same `scene.json` and verify mesh orientation, camera targets, and framing there too.

Include the input JSON, expected behavior, and actual behavior in a bug report. Do not submit private ticket information, credentials, purchased models, or source images without redistribution rights. Prefer authoritative source URLs plus your own measurements and an explanation of how they were derived.

For a new venue, separate structural evidence from show-specific stage evidence. Estimated dimensions must remain marked as estimated. A source confirming capacity does not verify bowl dimensions or seat coordinates.

Keep the default path usable with Python's standard library and an offline browser. Add dependencies only when a concrete capability needs them. Keep detailed instructions in references rather than growing the Skill entrypoint.

Contributions are submitted under the repository's MIT license. Third-party code and assets must retain their own compatible license and provenance.
