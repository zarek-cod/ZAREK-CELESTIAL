from pathlib import Path
import sys,bpy
from mathutils import Vector
probe=Path(__file__).resolve().with_name("produce.py")
sys.path.insert(0,str(probe.parent))
import produce
bpy.ops.wm.read_factory_settings(use_empty=True)
assemblies = []
for code,delta in [('A',-1.5),('B',1.5)]:
    with bpy.data.libraries.load(str(produce.ASSET/"blender"/f"CelestialHair_V3_{code}_MASTER.blend"),link=False) as (source,target):
        target.collections=[x for x in source.collections if x.startswith(f"MASTER V3 {code} ")]
    collection=target.collections[0]
    bpy.context.scene.collection.children.link(collection)
    for obj in collection.all_objects:
        obj.location += Vector((delta,0,0))
    assemblies.extend(collection.all_objects)
    for mat in {obj.data.materials[0] for obj in collection.all_objects}:
        shader=mat.node_tree.nodes.get("Principled BSDF")
        for link in list(shader.inputs["Normal"].links):
            mat.node_tree.links.remove(link)
for obj in assemblies:
    obj.select_set(True)
bpy.context.view_layer.objects.active=assemblies[0]
bpy.ops.export_scene.gltf(filepath=str(produce.SCRATCH/"V3_AB_MASTER_Studio.glb"),export_format="GLB",
    use_selection=True,export_apply=True,export_animations=False)
