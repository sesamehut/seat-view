# Preview input and geometry

Start from [../assets/demo-venue.json](../assets/demo-venue.json). Use JSON numbers, not unit-bearing strings. All dimensions are meters; the schema version is `1`.

## Fields

| Field | Meaning |
| --- | --- |
| `name` | User-facing scene name; mark approximations clearly |
| `kind` | `generic` for fictional/unsupported geometry; `researched` for a source-informed approximation |
| `units` | Must be `m` |
| `bowl.radius_x` | Inner bowl semi-axis along X |
| `bowl.radius_y` | Second semi-axis of the bowl's 2D footprint; maps to the scene's ground-plane Z direction |
| `bowl.tiers` | Ordered tiers from inner/lower to outer/upper |
| `tiers[].rows` | Number of generated terraces in that tier |
| `tiers[].row_depth` | Horizontal radial depth of a terrace |
| `tiers[].row_rise` | Height gained between adjacent rows |
| `tiers[].base_height` | Elevation of the tier's first terrace |
| `tiers[].gap_before` | Radial gap before the tier starts |
| `stage.layout` | `end`, `thrust`, or `center`; each is a generic stage |
| `stage.width`, `depth`, `height` | Main stage dimensions |
| `views` | Candidate cameras, each with unique `id`, readable `label`, `tier`, `row`, and `azimuth_deg` |
| `evidence` | Claim-level records: `field`, `status`, `source_url`, and `note` |
| `sources` | Source records: `title`, `url`, and `accessed` (ISO date) |
| `assumptions` | Plain-language limitations visible with the output |

Evidence `field` accepts `bowl`, `stage`, `views`, or an exact geometry leaf such as `bowl.radius_x`, `bowl.tiers[0].rows`, and `stage.layout`. `name` and intermediate paths such as `bowl.tiers` are not evidence fields; put venue identity in source notes. Every evidence record includes `source_url` (an empty string for an unsupported estimate). A `verified` record needs a URL also listed in `sources`.

The input validator rejects malformed, nonfinite, unsupported, and excessive values. Correct its actionable error rather than suppressing validation. Use the bundled demo's scale as a starting point; parameters are deliberately bounded to keep the result manageable.

## Coordinates and camera interpretation

Scene coordinates are right-handed, with X to the right, Y upward, and Z toward the opposite stand. End/thrust stages sit on the negative-Z side. Camera azimuth `0` is the positive-Z opposite stand, `90` is positive X, `180` is behind the end stage, and `270` is negative X.

Tier and row indices are **1-based generated model indices**, not ticket sections or official row numbers. For example, tier `2`, row `8` selects the eighth generated terrace of the second tier. Describe it as “upper tier · approximate position” unless an independent mapping exists.

Every view uses the same performer target and 50° vertical field of view. Distance is the straight-line distance from camera to target; depression angle is the angle below the horizontal toward that target and can be negative when looking upward. These are geometry calculations, not seat ratings.

The generic performer is 1.75 m tall. The stage target and meshes are generated consistently for the chosen layout. The generator does not estimate camera-phone zoom, facial recognition, acoustic quality, crowd occlusion, or a ticket's value.

## Reproducible generation

```bash
python3 scripts/build.py --spec /path/to/venue.json --output /path/to/preview
```

Run this from the skill directory or use the script's absolute path. The builder emits `index.html`, `venue.json`, `scene.json`, and `brief.md`. The HTML embeds its renderer and scene; it does not fetch the input or remote assets when opened. A local server is optional:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory /path/to/preview
```

This serves on the local machine, not a public share URL. For a revised preview, edit the input JSON and generate into a new output directory; the builder preserves existing deliverables. Preserve sources and assumptions when changing dimensions; a visual improvement does not upgrade the evidence status.
