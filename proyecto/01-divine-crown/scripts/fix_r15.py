from pathlib import Path
A=Path(r'C:\Users\joels\Desktop\ZAREK-CELESTIAL\proyecto\01-divine-crown')
p=A/'scripts/build_crown.py';s=p.read_text(encoding='utf-8')
s=s.replace("hv=[head.matrix_world@v.co for v in head.data.vertices]", "deps=bpy.context.evaluated_depsgraph_get();he=head.evaluated_get(deps);hm=he.to_mesh();hv=[head.matrix_world@v.co for v in hm.vertices];he.to_mesh_clear()")
old="for o in meshes:\n        mat=o.matrix_world.copy();o.parent=None;o.matrix_world=mat;o.location-=shift\n        o.data.materials.clear();o.data.materials.append(material('R15 reference - porcelain',(.16,.20,.29),.1,.48))"
new="for o in imported:\n        if o.parent not in imported:o.location-=shift\n    bpy.context.view_layer.update()\n    for o in meshes:\n        o.data.materials.clear();o.data.materials.append(material('R15 reference - porcelain',(.16,.20,.29),.1,.48))"
assert old in s;s=s.replace(old,new)
s=s.replace("allv=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];zmin=min(v.z for v in allv)", "allv=[]\n    deps=bpy.context.evaluated_depsgraph_get()\n    for o in meshes:\n        ev=o.evaluated_get(deps);me=ev.to_mesh();allv.extend(o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()\n    zmin=min(v.z for v in allv);scene.objects['STAGE - shadow receiver'].location.z=zmin-.025")
s=s.replace("# Applying a common world transform to meshes after detaching avoids double parent transforms.","# Apply translation only to imported roots; preserve armature and all child transforms.")
p.write_text(s,encoding='utf-8')
p=A/'scripts/validate.py';s=p.read_text(encoding='utf-8')
s=s.replace("hv=[head.matrix_world@v.co for v in head.data.vertices]", "bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();ev=head.evaluated_get(dep);hm=ev.to_mesh();hv=[head.matrix_world@v.co for v in hm.vertices];head_faces=[tuple(p.vertices) for p in hm.polygons];ev.to_mesh_clear()")
s=s.replace("[tuple(p.vertices) for p in head.data.polygons]","head_faces")
p.write_text(s,encoding='utf-8')
print('Corrected R15 armature hierarchy preservation and evaluated-head fit test')
