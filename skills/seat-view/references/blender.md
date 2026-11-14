# Optional Blender export

Read this when editable `.blend` geometry or `.glb` output is requested. The browser preview is the normal first result. The exporter reuses its scene meshes and cameras so both outputs share one geometry source.

## Export the generated scene

Use the installed Blender executable in background mode:

```bash
blender --background --factory-startup --python "/path/to/seat-view/scripts/blender_export.py" -- \
  --scene "/path/to/preview/scene.json" \
  --output "/path/to/preview/blender"
```

On macOS, the executable may be `/Applications/Blender.app/Contents/MacOS/Blender`; on other systems use the installed executable's path. If Blender is unavailable, deliver the working preview and input files. Do not make the user install Blender just to see the demo.

Run the script in a fresh background process. Do not execute scene-resetting export scripts inside an open Blender document that might contain unsaved work.

## Geometry agreement

The preview uses X right, Y up, and Z toward the audience. Blender coordinates are `(x, -z, y)`, preserving a right-handed orientation with Z up. Cameras look at the same target and use the same vertical field of view as the browser. Check framing with the same aspect ratio before comparing images.

The exported bowl remains a procedural approximation. Exporting does not add measured architecture, an official seating map, or an actual tour stage. Refine those only when the user requests it and supplies or authorizes useful reference material.

## Check and hand off

Confirm that both exported files exist and can be opened when tools permit. Inspect an overview and one seat camera. If you change geometry in Blender, explain that the browser preview will not automatically inherit those edits; keep the original `venue.json` and `scene.json` alongside the result for reproducibility.

For refinement, prioritize the elements that change a viewing comparison: bowl profile, tier heights, stage footprint, and camera placement. Roof ornaments, lighting shows, dense crowds, and architectural exterior detail are separate work rather than requirements for this skill's first result.
