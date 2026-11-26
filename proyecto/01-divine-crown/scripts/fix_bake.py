from pathlib import Path
p=Path(r'C:\Users\joels\Desktop\ZAREK-CELESTIAL\proyecto\01-divine-crown\scripts\build_crown.py')
s=p.read_text(encoding='utf-8')
s=s.replace("tx.rotation_euler=(pi/2,0,pi)","tx.rotation_euler=(pi/2,0,0)")
s=s.replace("bpy.ops.object.bake(type='DIFFUSE');save_image(im,A/'texturas/DivineCrown_BaseColor.png')", "colorlinks=[]\n    for mat in low.data.materials:\n        nt=mat.node_tree;pb=nt.nodes.get('Principled BSDF');out=nt.nodes.get('Material Output');em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=pb.inputs['Base Color'].default_value;nt.links.new(em.outputs[0],out.inputs['Surface']);colorlinks.append((nt,pb,out,em))\n    bpy.ops.object.bake(type='EMIT')\n    for nt,pb,out,em in colorlinks:nt.links.new(pb.outputs['BSDF'],out.inputs['Surface']);nt.nodes.remove(em)\n    save_image(im,A/'texturas/DivineCrown_BaseColor.png')")
old="mult=nt.nodes.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1\n    nt.links.new(base.outputs['Color'],mult.inputs[1]);nt.links.new(tex(emiss,-600,-650).outputs['Color'],mult.inputs[2]);nt.links.new(mult.outputs[0],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.65"
new="import numpy as np\n    smallbase=im.copy();smallbase.scale(256,256);bc=np.array(smallbase.pixels[:],dtype=np.float32).reshape(-1,4);mask=np.array(emiss.pixels[:],dtype=np.float32).reshape(-1,4);bc[:,:3]*=mask[:,:3];bc[:,3]=1\n    emcolor=image_new('EmissionColor',256);emcolor.pixels.foreach_set(bc.ravel());save_image(emcolor,A/'texturas/DivineCrown_EmissiveColor.png')\n    nt.links.new(tex(emcolor,-600,-650).outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.65\n    m.use_backface_culling=True"
assert old in s
s=s.replace(old,new)
p.write_text(s,encoding='utf-8')
