"""Check V4 FBX/GLB round trips, mesh topology, atlas layout and normal payload."""
from pathlib import Path
import collections
import hashlib
import json
import struct
import sys

import bpy
import bmesh

ASSET=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ASSET.parent/"scripts"))
from validate_hair import mesh_data, bounds

STEM="CelestialHair_V4"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def glb_material(path):
    data=path.read_bytes()
    magic,version,size,json_size,kind=struct.unpack_from("<4sIII4s",data)
    assert (magic,version,size,kind)==(b"glTF",2,len(data),b"JSON")
    doc=json.loads(data[20:20+json_size])
    assert len(doc["materials"])==len(doc["meshes"])==1
    primitive,=doc["meshes"][0]["primitives"]
    assert {"POSITION","NORMAL","TANGENT","TEXCOORD_0"} <= primitive["attributes"].keys()
    material=doc["materials"][0]
    pbr=material["pbrMetallicRoughness"]
    assert pbr["metallicFactor"]==0
    normal=material["normalTexture"]["index"]
    refs={"Color":pbr["baseColorTexture"]["index"],"Normal":normal,
          "Rugosidad":pbr["metallicRoughnessTexture"]["index"]}
    outputs={}
    for name,index in refs.items():
        image=doc["images"][doc["textures"][index]["source"]]
        view=doc["bufferViews"][image["bufferView"]]
        offset=28+json_size+view.get("byteOffset",0)
        payload=data[offset:offset+view["byteLength"]]
        assert payload[:8]==b"\x89PNG\r\n\x1a\n"
        resolution=list(struct.unpack_from(">II",payload,16))
        assert resolution==([1024,1024] if name=="Color" else [256,256])
        outputs[name]={"resolution":resolution,"sha256":sha(payload)}
        if name=="Normal":
            original=(ASSET/"texturas"/f"{STEM}_Normal.png").read_bytes()
            assert payload==original
    return {"tangents":True,"metalness":0,"maps":outputs}


def topology(obj):
    mesh=obj.data
    mesh.calc_loop_triangles()
    assert len(mesh.uv_layers)==len(mesh.materials)==1
    assert all(p.use_smooth for p in mesh.polygons)
    bm=bmesh.new()
    bm.from_mesh(mesh)
    bad=sum(not e.is_manifold for e in bm.edges)
    degenerate=sum(f.calc_area()<1e-12 for f in bm.faces)
    inconsistent=sum(not e.is_contiguous for e in bm.edges)
    bm.free()
    assert bad==degenerate==inconsistent==0,(bad,degenerate,inconsistent)
    tile_counts=collections.Counter()
    uv=mesh.uv_layers.active.data
    uv_bad=0
    for poly in mesh.polygons:
        coords=[uv[i].uv for i in poly.loop_indices]
        tile={(int(c.x*7),int(c.y*7)) for c in coords}
        assert len(tile)==1 and all(0<min(c) and max(c)<1 for c in coords)
        uv_bad+=abs(sum(a.cross(b) for a,b in zip(coords,coords[1:]+coords[:1])))<1e-11
        tile_counts[next(iter(tile))]+=1
    assert not uv_bad,uv_bad
    return {"triangles":len(mesh.loop_triangles),"vertices":len(mesh.vertices),
            "nonmanifold_edges":bad,"noncontiguous_edges":inconsistent,
            "degenerate_faces":degenerate,"tiles":len(tile_counts),"uv_degenerate":uv_bad}


def run():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET/"blender"/f"{STEM}_UGC.blend"))
    obj=bpy.data.objects[f"{STEM}_UGC"]
    spec=topology(obj)
    size=bounds(mesh_data([obj])[0])
    assert spec["triangles"]<=4000
    assert -1.5<=size[0][0]<=size[1][0]<=1.5
    assert -1.5<=size[0][1]<=size[1][1]<=2
    assert -3<=size[0][2]<=size[1][2]<=2
    report={"topology":spec,"bounds_xyz_blender":size,"reimports":{}}
    for extension in ("fbx","glb"):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        path=ASSET/"exportaciones"/f"{STEM}_UGC.{extension}"
        if extension=="fbx":
            bpy.ops.import_scene.fbx(filepath=str(path),use_anim=False)
        else:
            bpy.ops.import_scene.gltf(filepath=str(path))
        meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
        reimported,=meshes
        assert len(reimported.data.uv_layers)==len(reimported.data.materials)==1
        verts,tris,*_=mesh_data(meshes)
        lim=bounds(verts)
        assert len(tris)==spec["triangles"]
        assert max(abs(a-b) for a,b in zip(sum(lim,[]),sum(size,[])))<1e-4
        report["reimports"][extension]={"mesh_count":1,"triangles":len(tris),"bounds":lim,"sha256":sha(path.read_bytes())}
        if extension=="glb":
            report["reimports"][extension]["pbr"]=glb_material(path)
    output=json.dumps(report,indent=2,ensure_ascii=False)
    (ASSET/"validacion"/"archivos.json").write_text(output+"\n",encoding="utf8")
    print("V4_VALIDATION_PASS",output,flush=True)


if __name__=="__main__":
    run()
