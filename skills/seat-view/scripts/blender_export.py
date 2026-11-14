"""Optional Blender adapter: read scene.json, write venue.blend and venue.glb.

blender --background --factory-startup --python blender_export.py -- \
  --scene out/scene.json --output out/blender
"""
import argparse
import json
import math
import sys
from pathlib import Path


def main():
    import bpy
    from mathutils import Vector

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if not bpy.app.background or bpy.data.filepath:
        raise RuntimeError('Run in a fresh background session with --factory-startup; never an active project.')
    scene_data = json.loads(args.scene.read_text(encoding='utf-8'))
    if scene_data.get('schema_version') != 1:
        raise ValueError('Expected generated scene.json schema_version 1')
    # Rebuild from its validated spec rather than trusting arbitrary mesh arrays.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from scene import build_scene
    scene_data = build_scene(scene_data['spec'])
    if any((args.output / name).exists() for name in ('venue.blend', 'venue.glb')):
        raise FileExistsError('Output contains venue.blend or venue.glb; choose a new directory to preserve edits.')
    args.output.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1
    scene.render.resolution_x, scene.render.resolution_y = 1440, 1000
    scene.render.resolution_percentage = 100
    try:
        scene.render.engine = 'BLENDER_EEVEE_NEXT'  # Blender 4.x
    except TypeError:
        scene.render.engine = 'BLENDER_EEVEE'  # Blender 5.x
    scene.world.color = (.15, .15, .15)
    scene.view_settings.view_transform = 'Standard'
    materials = {}

    def convert(point):
        return (point[0], -point[2], point[1])

    for item in scene_data['meshes']:
        color = item['color']
        if color not in materials:
            material = bpy.data.materials.new(color)
            rgb = [int(color[i:i+2], 16)/255 for i in (1,3,5)]
            # JSON colors are sRGB; Blender material values are linear.
            linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
            material.diffuse_color = (*linear, 1)
            material.use_nodes = True
            bsdf = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
            bsdf.inputs['Base Color'].default_value = (*linear,1)
            bsdf.inputs['Roughness'].default_value = .72
            materials[color] = material
        mesh = bpy.data.meshes.new(item['name'])
        mesh.from_pydata([convert(p) for p in item['vertices']], [], item['faces'])
        mesh.update()
        obj = bpy.data.objects.new(item['name'], mesh)
        scene.collection.objects.link(obj)
        obj.data.materials.append(materials[color])
    for view in scene_data['views']:
        data = bpy.data.cameras.new(view['id'])
        data.sensor_fit = 'VERTICAL'
        data.sensor_height = 24
        data.lens = data.sensor_height / (2 * math.tan(math.radians(view['fov_vertical_deg']) / 2))
        data.clip_start, data.clip_end = .05, 2000
        obj = bpy.data.objects.new('view-' + view['id'], data)
        scene.collection.objects.link(obj)
        obj.location = convert(view['position'])
        direction = Vector(convert(view['target'])) - obj.location
        obj.rotation_euler = direction.to_track_quat('-Z','Y').to_euler()
        if scene.camera is None:
            scene.camera = obj
    light_data = bpy.data.lights.new('soft-sun', 'SUN')
    light_data.energy, light_data.angle = 2, .35
    light = bpy.data.objects.new('soft-sun', light_data)
    scene.collection.objects.link(light)
    light.rotation_euler = (math.radians(25), math.radians(-20), math.radians(-25))
    bpy.ops.wm.save_as_mainfile(filepath=str((args.output/'venue.blend').resolve()))
    bpy.ops.export_scene.gltf(filepath=str((args.output/'venue.glb').resolve()), export_format='GLB',
                              export_cameras=True, export_lights=False, export_yup=True)
    print(f'Seat View exported: {args.output / "venue.blend"}, {args.output / "venue.glb"}')


if __name__ == '__main__':
    main()
