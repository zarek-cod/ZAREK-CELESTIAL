
"""Audit source meshes, PBR payloads, both export formats and static/animated fit."""
from pathlib import Path
from math import hypot
import hashlib
import json
import struct
import bpy
import bmesh
from mathutils.bvhtree import BVHTree

A=Path(__file__).resolve().parents[1]
C=A.parent/"01-divine-crown/blender/DivineCrown_UGC_R15_fit.blend"
MAN=A.parents[1]/"referencias/oficiales/ClassicMannequin.fbx"


def open_model(variant):
    bpy.ops.wm.open_mainfile(filepath=str(A/f"blender/EternalHalo_{variant}.blend"))
    return [o for o in bpy.context.scene.objects if o.type=="MESH"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def topology(objects):
    out={"meshes":len(objects),"triangles":0,"vertices":0,"shells":0,
         "open_edges":0,"nonmanifold_edges":0,"degenerate_faces":0,"inward_shells":0}
    for obj in objects:
        me=obj.data
        me.calc_loop_triangles()
        out["triangles"]+=len(me.loop_triangles)
        out["vertices"]+=len(me.vertices)
        bm=bmesh.new()
        bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        out["open_edges"]+=sum(e.is_boundary for e in bm.edges)
        out["nonmanifold_edges"]+=sum(not e.is_manifold for e in bm.edges)
        out["degenerate_faces"]+=sum(f.calc_area()<1e-11 for f in bm.faces)
        remaining=set(bm.faces)
        while remaining:
            first=remaining.pop()
            stack=[first]
            volume=0
            while stack:
                f=stack.pop()
                for j in range(1,len(f.verts)-1):
                    volume+=f.verts[0].co.dot(f.verts[j].co.cross(f.verts[j+1].co))/6
                for e in f.edges:
                    for neighbor in e.link_faces:
                        if neighbor in remaining:
                            remaining.remove(neighbor)
                            stack.append(neighbor)
            out["shells"]+=1
            out["inward_shells"]+=volume<=0
        bm.free()
    return out


def geometry(objects):
    va=[]
    po=[]
    deps=bpy.context.evaluated_depsgraph_get()
    for original in objects:
        obj=original.evaluated_get(deps)
        me=obj.to_mesh()
        me.calc_loop_triangles()
        offset=len(va)
        va.extend(obj.matrix_world @ v.co for v in me.vertices)
        po.extend(tuple(offset+i for i in t.vertices) for t in me.loop_triangles)
        obj.to_mesh_clear()
    return va,po


def limit(vertices):
    return [[round(fn(v[j] for v in vertices),6) for j in range(3)] for fn in (min,max)]


def tree(geo):
    return BVHTree.FromPolygons(*geo,all_triangles=True,epsilon=0.0)


def uv_check(obj):
    mesh=obj.data
    mesh.calc_loop_triangles()
    uv=mesh.uv_layers.active.data
    count=[0,0,0]
    area=[0.0,0.0,0.0]
    bad=0
    for tri in mesh.loop_triangles:
        coords=[uv[i].uv for i in tri.loops]
        center=sum(p.y for p in coords)/3
        i=0 if center<.45 else (1 if center<.82 else 2)
        count[i]+=1
        a,b,c=coords
        area[i]+=abs((b-a).cross(c-a))*.5
        bad+=abs((b-a).cross(c-a))<1e-11
    normalized=all(-1e-6<=value<=1.000001 for loop in uv for value in loop.uv)
    assert normalized and bad==0 and len(mesh.uv_layers)==1
    assert count[:2]==[1728,1280],count
    assert abs(area[0]-.944*(.434-.035))<1e-5
    assert abs(area[1]-.944*(.790-.474))<1e-5
    return {"sets":len(mesh.uv_layers),"all_in_0_1":normalized,"degenerate_uv_triangles":bad,
            "triangles_by_atlas_region":count,"ring_uv_area":[round(x,7) for x in area[:2]],
            "layout":"Two full, separate rectangular bands with periodic seams. Detail faces intentionally share flat swatches."}


def inspect_glb(path,expected):
    data=path.read_bytes()
    magic,version,total=struct.unpack_from("<4sII",data)
    assert magic==b"glTF" and version==2 and total==len(data)
    length,kind=struct.unpack_from("<I4s",data,12)
    assert kind==b"JSON"
    payload=json.loads(data[20:20+length])
    bin_length,bin_type=struct.unpack_from("<I4s",data,20+length)
    assert bin_type==b"BIN\x00"
    start=28+length
    mats=payload["materials"]
    assert len(mats)==1 and len(payload["meshes"])==expected
    mat=mats[0]
    assert not mat.get("doubleSided",False) and mat.get("alphaMode","OPAQUE")=="OPAQUE"
    pbr=mat["pbrMetallicRoughness"]
    texture_indices=[pbr["baseColorTexture"]["index"],pbr["metallicRoughnessTexture"]["index"],
                     mat["normalTexture"]["index"],mat["emissiveTexture"]["index"]]
    assert len(set(texture_indices))==4
    images={}
    for name,idx in zip(("base_color","metallic_roughness","normal","emission_rgb"),texture_indices):
        tex=payload["textures"][idx]
        buf=payload["bufferViews"][payload["images"][tex["source"]]["bufferView"]]
        pixel=data[start+buf.get("byteOffset",0):start+buf.get("byteOffset",0)+buf["byteLength"]]
        assert pixel.startswith(b"\x89PNG\r\n\x1a\n")
        images[name]=list(struct.unpack_from(">II",pixel,16))
    assert images=={"base_color":[1024,1024],"metallic_roughness":[256,256],"normal":[256,256],"emission_rgb":[256,256]}
    return images


def roundtrip(variant,expected_triangles,expected_meshes,expected_bounds):
    out={}
    for ext in ("fbx","glb"):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        path=A/f"exportaciones/EternalHalo_{variant}.{ext}"
        if ext=="fbx":
            bpy.ops.import_scene.fbx(filepath=str(path),use_anim=False)
        else:
            bpy.ops.import_scene.gltf(filepath=str(path))
        meshes=[obj for obj in bpy.context.scene.objects if obj.type=="MESH"]
        vert,tri=geometry(meshes)
        bounds=limit(vert)
        assert len(meshes)==expected_meshes
        assert len(tri)==expected_triangles,(ext,len(tri),expected_triangles)
        assert max(abs(a-b) for a,b in zip(sum(bounds,[]),sum(expected_bounds,[])))<1e-4,(ext,bounds,expected_bounds)
        assert all(len(o.data.uv_layers)==1 and len(o.data.materials)==1 for o in meshes)
        out[ext]={"meshes":len(meshes),"names":[o.name for o in meshes],
                  "triangles":len(tri),"bounds_blender":bounds,"sha256":sha(path)}
        if ext=="glb":
            out[ext]["pbr_images"]=inspect_glb(path,expected_meshes)
    return out


def comparison(a,b):
    ta,tb=tree(a),tree(b)
    cross=len(ta.overlap(tb))
    clearance=min(min(tb.find_nearest(v)[3] for v in a[0]),min(ta.find_nearest(v)[3] for v in b[0]))
    return {"intersecting_triangle_pairs":cross,
            "closest_sampled_vertex_to_surface_studs":round(clearance,6)}


def checks():
    report={"blender":bpy.app.version_string}
    ugc=open_model("UGC")
    report["UGC"]=topology(ugc)
    assert len(ugc)==1 and len(ugc[0].data.materials)==1
    assert report["UGC"]["triangles"]<=4000
    for key in ("open_edges","nonmanifold_edges","degenerate_faces","inward_shells"):
        assert not report["UGC"][key],key
    report["atlas_UV"]=uv_check(ugc[0])
    g=geometry(ugc)
    ub=limit(g[0])
    all_axes=[1.5,1.5,2]
    assert all(abs(x)<all_axes[j] for limits in ub for j,x in enumerate(limits))
    report["Classic_Hat"]={"bounds_blender":ub,"position_reference":[0,0,0],
                           "dimensions_roblox_XYZ":[round(ub[1][axis]-ub[0][axis],6) for axis in (0,2,1)],
                           "allowed_roblox_XYZ":[3,4,3],"uses_1_blender_unit_per_stud":True}
    report["exports_UGC"]=roundtrip("UGC",report["UGC"]["triangles"],1,ub)

    master=open_model("MASTER")
    report["MASTER"]=topology(master)
    high=geometry(master)
    assert not any(report["MASTER"][key] for key in ("open_edges","nonmanifold_edges","degenerate_faces","inward_shells"))
    god=open_model("GOD_MODE")
    report["GOD_MODE"]=topology(god)
    god_geo=geometry(god)
    assert len(bpy.data.objects["Zenith_Pivot"].children)==1
    assert len(bpy.data.objects["Meridian_Pivot"].children)==1
    assert len([o for o in bpy.context.scene.objects if "_FX_" in o.name])==8
    world_min=[]
    report["GOD_MODE"]["rotation_frames_sampled"]=[]
    maximum=0
    scene=bpy.context.scene
    collections=[bpy.data.collections[name] for name in ("Zenith","Meridian")]
    for name,c in zip(("Zenith","Meridian"),collections):
        vertices,_=geometry([o for o in c.objects if o.type=="MESH"])
        basis=bpy.data.objects[f"{name}_Pivot"].matrix_world
        matrix=basis.inverted()
        tilt_z=hypot(basis[2][0],basis[2][1])
        # Complete rotation envelope, including every vertex of each electrical arc and star.
        world_min.append(min(basis.translation.z+basis[2][2]*p.z-tilt_z*hypot(p.x,p.y)
                             for p in (matrix@v for v in vertices)))
    for frame in range(1,241,8):
        scene.frame_set(frame)
        geos=[geometry([o for o in c.objects if o.type=="MESH"]) for c in collections]
        maximum=max(maximum,len(tree(geos[0]).overlap(tree(geos[1]))))
        report["GOD_MODE"]["rotation_frames_sampled"].append(frame)
    report["GOD_MODE"]["maximum_band_intersection_pairs_sampled"]=maximum
    assert maximum==0,maximum
    report["exports_GOD_MODE"]=roundtrip("GOD_MODE",report["GOD_MODE"]["triangles"],2,limit(god_geo[0]))

    bpy.ops.wm.open_mainfile(filepath=str(C))
    crown=geometry([bpy.data.objects["DivineCrown_UGC"]])
    head=geometry([bpy.data.objects["Head_Geo"]])
    body=geometry([o for o in bpy.context.scene.objects if o.name.endswith("_Geo")])
    assert len([o for o in bpy.context.scene.objects if o.name.endswith("_Geo")])==15
    assert abs(max(v.z for v in head[0]))<1e-4
    crown_top=max(v.z for v in crown[0])
    report["fit"]={"source_crown_blend_sha256":sha(C),"official_mannequin_fbx_sha256":sha(MAN),
                   "crown_top_z":round(crown_top,6),"ugc_over_crown":comparison(g,crown),
                   "master_over_crown":comparison(high,crown),"ugc_over_R15":comparison(g,body),
                   "master_over_R15":comparison(high,body),
                   "ugc_vertical_separation":round(min(v.z for v in g[0])-crown_top,6),
                   "master_vertical_separation":round(min(v.z for v in high[0])-crown_top,6),
                   "god_mode_clearance_through_full_rotation":round(min(world_min)-crown_top,6),
                   "hair_space_design":{"radius_from_head_center_studs":.83,"height_above_attachment_studs":.78,
                                          "basis":"Conservative volume below the lowest halo vertex in all variants; hair mesh not available."}}
    for key in ("ugc_over_crown","master_over_crown","ugc_over_R15","master_over_R15"):
        assert report["fit"][key]["intersecting_triangle_pairs"]==0,key
    for key in ("ugc_vertical_separation","master_vertical_separation","god_mode_clearance_through_full_rotation"):
        assert report["fit"][key]>0,key

    report["maps"]={}
    for p in sorted((A/"texturas").glob("*.png")):
        data=p.read_bytes()
        width,height,depth,ctype=struct.unpack_from(">IIBB",data,16)
        assert width==height==(1024 if p.stem=="BaseColor" else 256)
        assert depth==8 and ctype==(0 if p.stem in ("Metalness","Roughness","EmissiveMask") else 2)
        report["maps"][p.name]={"width":width,"height":height,"bit_depth":depth,
                                "channels":"gray" if ctype==0 else "RGB","sha256":sha(p)}
    report["scope"]="Blender validation only. Studio import and AFT for Eternal Halo, real hair fit, and Marketplace remain pending."
    return report


if __name__=="__main__":
    report=checks()
    output=json.dumps(report,ensure_ascii=False,indent=2)
    (A/"validacion/resultados.json").write_text(output+"\n",encoding="utf-8")
    print(output)
    print("ETERNAL_HALO_VALIDATION_PASS",flush=True)
