---
name: seat-view
description: Create an interactive 3D concert seat-view preview from a stadium or arena name, stage layout, and candidate viewing positions. Use for 演唱会选座、场馆视角模拟、看台视角对比 or a 坐哪儿-style preview, with optional Blender export. Produces an evidence-labeled approximation; does not book tickets or certify visibility from an official seat number.
license: MIT
compatibility: "Python 3.9+ and a modern WebGL browser. Real-venue research needs web tools. Blender is optional."
---

# Seat View · 坐哪儿视角预演

Turn “what will this concert look like from here?” into a local, interactive preview with three comparable positions. Keep the first useful result small: a researched bowl approximation, a generic stage, and traceable assumptions.

## Start with the user's question

Resolve the venue and city. Ask only when names refer to materially different venues. Use the requested concert/date and stage layout when supplied; otherwise use a clearly labeled hypothetical end stage. Do not invent the event's production layout.

If the user just wants to try the skill, run the fictional demo immediately:

```bash
python3 "<skill-directory>/scripts/build.py" --demo --output "./seat-view-output"
```

Replace `<skill-directory>` with the directory containing this file. Use `python` instead of `python3` where appropriate. Open the generated `index.html` directly in a modern browser. The demo needs no account, server, network, Blender, or Python packages.

## Research the real venue

Read [references/research.md](references/research.md) when using a real venue. Prefer venue operators, architects, engineering publications, and the event organizer's dated seating plan. Record a source for each factual geometry claim; distinguish measured dimensions, image-derived estimates, and unknowns.

The generator makes an elliptical, stepped bowl. It cannot reproduce every venue silhouette, roof, official section boundary, or concert production. Explain material mismatches before presenting the result as useful for that venue. If research is unavailable, keep progressing with a generic preview and disclose that the venue has not been researched.

Never convert a ticket section/row/seat number into an exact camera position without a supported mapping. For this version, use labels such as “lower side stand · approximate position”; generated tier and row indices describe this model only.

## Generate a preview

Read [references/spec.md](references/spec.md), then adapt [assets/demo-venue.json](assets/demo-venue.json) into an input JSON. Preserve the user's desired stage and comparison positions within the supported geometry. For missing dimensions, choose plausible working estimates and record them in `evidence` and `assumptions`.

Choose three meaningfully different positions unless the user requests otherwise: lower side, lower opposite, and upper opposite. Compare them using the same stage target and fixed 50° vertical field of view. A larger drawing of the performer caused by a different lens is not a better seat.

```bash
python3 "<skill-directory>/scripts/build.py" --spec "./venue.json" --output "./seat-view-output"
```

The result contains:

- `index.html`: self-contained interactive preview, with no remote asset requests.
- `venue.json`: reproducible input and its evidence ledger.
- `scene.json`: generated meshes, camera positions, and geometric measurements.
- `brief.md`: source and assumption summary.

If opening a local file is restricted by the browser, serve it locally:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory "./seat-view-output"
```

## Check the useful result

Inspect the generated overview and every selected view when browser tools are available. Check that the stage fits the bowl, the performer is visible, cameras sit above their terraces, and view labels match the intended sides. Check a narrow viewport if the result will be viewed on a phone. Report any unverified visual checks when browser tools are unavailable.

Describe distance and depression angle as model measurements. Human apparent size, obstruction, sound, ticket value, and the actual show experience are not certified by this preview. The simplified model omits people, handrails, towers, screens or roofs unless explicitly modeled; absence of those objects is not evidence of a clear sightline.

## Optional Blender handoff

Use [references/blender.md](references/blender.md) when the user requests editable Blender geometry or GLB export. First produce the working browser preview. Blender is an optional enhancement, not a prerequisite for trying this skill.

## Deliver

Link the preview and reproducible files, summarize the comparison, and name the assumptions that most affect the result. Keep the distinction between a fictional demonstration and a researched approximation visible. Offer the next useful refinement—such as supplying the event seating map—only when it addresses a concrete uncertainty. Publishing files to GitHub or another host is a separate action from generating a local preview.
