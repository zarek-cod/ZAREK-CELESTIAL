"""Verify V5's two Blender round trips and inspect the GLB tangent-space and atlas data."""
import hashlib
import json
from pathlib import Path
import struct
import sys

import bpy
import numpy as np

ASSET = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ASSET.parent / "v4/scripts"))
from verificar_v4 import bounds, mesh_data, topology

STEM = "CelestialHair_V5"


def glb_payloads(data):
    magic, version, length, size, rest = struct.unpack_from("<4sIII4s", data)
    assert (magic, version, length, rest) == (b"glTF", 2, len(data), b"JSON")
    doc = json.loads(data[20:20 + size])
    mesh, = doc["meshes"]
    primitive, = mesh["primitives"]
    assert {"POSITION", "TEXCOORD_0", "NORMAL", "TANGENT"} <= primitive["attributes"].keys()
    material, = doc["materials"]
    pbr = material["pbrMetallicRoughness"]
    assert pbr["metallicFactor"] == 0 and material["normalTexture"].get("scale", 1) == 1
    mapping = {"Color": pbr["baseColorTexture"], "Normal": material["normalTexture"],
               "Rugosidad": pbr["metallicRoughnessTexture"]}
    output = {}
    for name, texture in mapping.items():
        image = doc["images"][doc["textures"][texture["index"]]["source"]]
        view = doc["bufferViews"][image["bufferView"]]
        offset = 28 + size + view.get("byteOffset", 0)
        payload = data[offset:offset + view["byteLength"]]
        assert payload[:8] == b"\x89PNG\r\n\x1a\n"
        resolution = struct.unpack_from(">II", payload, 16)
        expected = 1024 if name == "Color" else 512
        assert resolution == (expected, expected), (name, resolution)
        original = (ASSET / "texturas" / f"{STEM}_{name}.png").read_bytes()
        if name in {"Color", "Normal"}:
            assert payload == original, name
        output[name] = {"resolucion": list(resolution), "sha256": hashlib.sha256(payload).hexdigest(),
                        "coincide_png_individual": payload == original}
    return output


def run():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET / "blender" / f"{STEM}_UGC.blend"))
    source = bpy.data.objects[f"{STEM}_UGC"]
    spec = topology(source)
    assert source.data.has_custom_normals and spec["triangles"] <= 4000
    expected = bounds(mesh_data([source])[0])
    assert (-1.5 <= expected[0][0] and expected[1][0] <= 1.5 and
            -1.5 <= expected[0][1] and expected[1][1] <= 2 and
            -3 <= expected[0][2] and expected[1][2] <= 2), expected
    report = {"topologia": spec, "bounds_blender": expected, "reimportaciones": {}}
    for extension in ("fbx", "glb"):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        path = ASSET / "exportaciones" / f"{STEM}_UGC.{extension}"
        if extension == "fbx":
            bpy.ops.import_scene.fbx(filepath=str(path), use_anim=False)
        else:
            bpy.ops.import_scene.gltf(filepath=str(path))
        imported, = [item for item in bpy.context.scene.objects if item.type == "MESH"]
        assert len(imported.data.uv_layers) == len(imported.data.materials) == 1
        points, triangles, *_ = mesh_data([imported])
        assert len(triangles) == spec["triangles"]
        bbox = bounds(points)
        assert np.allclose(bbox, expected, atol=1e-4), bbox
        data = path.read_bytes()
        reimport = {"mallas": 1, "triangulos": len(triangles), "bounds": bbox,
                    "normales_personalizadas": imported.data.has_custom_normals,
                    "sha256": hashlib.sha256(data).hexdigest()}
        if extension == "glb":
            reimport["atlas_pbr"] = glb_payloads(data)
        report["reimportaciones"][extension] = reimport
    output = json.dumps(report, indent=2)
    (ASSET / "validacion" / "archivos.json").write_text(output + "\n", encoding="utf8")
    print("V5_ROUND_TRIP", output)


if __name__ == "__main__":
    run()
