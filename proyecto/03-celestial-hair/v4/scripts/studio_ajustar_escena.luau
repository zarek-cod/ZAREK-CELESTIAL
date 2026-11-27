-- Run in local edit mode after studio_crear_escena.luau.
-- Match the relative centers measured in the static Blender assembly.
local stage=assert(workspace:FindFirstChild("ZAREK_V4_PRESENTACION"))
assert(not stage:GetAttribute("RevisadoV4"), "La colocación ya se ajustó.")
local references=game:GetService("ServerStorage"):FindFirstChild("Origenes_V4")
local baseplate=workspace:FindFirstChild("Baseplate")
if baseplate and references then baseplate.Parent=references end
local function handleOf(accessory)
    local h=assert(accessory:FindFirstChildWhichIsA("MeshPart",true))
    return h,assert(h:FindFirstChildWhichIsA("Attachment")),assert(h:FindFirstChild("AccessoryWeld"))
end
local function shift(h,anchor,weld,delta)
    anchor.CFrame=anchor.CFrame-h.CFrame:VectorToObjectSpace(delta)
    weld.C0=anchor.CFrame
end
local function parts(rig)
    local result={}
    for _, object in rig:GetChildren() do
        if object:IsA("Accessory") then
            if object.AccessoryType==Enum.AccessoryType.Hair then result.hair=object
            elseif object.Name=="Zenith" then result.halo=object
            elseif object.Name:find("Foundation",1,true) then result.crown=object end
        end
    end
    return result
end
for i=1,3 do
    local rig=stage.R15[string.format("%02d_R15",i)]
    local acc=parts(rig)
    local hair=handleOf(acc.hair)
    if acc.crown then
        local h,a,w=handleOf(acc.crown)
        local dy=hair.Position.Y+.65655-h.Position.Y
        shift(h,a,w,Vector3.new(0,dy,0))
        print("ZAREKV4_FIT",i,"corona_dy",dy,"hair_anchor",hair:FindFirstChild("HairAttachment").Name)
    end
    if acc.halo then
        local h,a,w=handleOf(acc.halo)
        local dy=hair.Position.Y+1.4488-h.Position.Y
        shift(h,a,w,Vector3.new(0,dy,0))
        print("ZAREKV4_FIT",i,"halo_dy",dy)
    end
    local offset=Vector3.new(i==1 and 11.4 or i==3 and -11.4 or 0,0,0)
    rig:PivotTo(rig:GetPivot()+offset)
    for _, shot in stage.Camaras:GetChildren() do
        if shot.Name:sub(-1)==tostring(i) then
            shot.Value=shot.Value+offset
            if i==3 then
                shot.Value=shot.Value+Vector3.new(0,.17,0)
                shot:SetAttribute("FOV",37)
            end
        end
    end
end
for _, p in stage:GetChildren() do
    if p:IsA("BasePart") then
        local x=p.Position.X
        if p.Name:find("Pedestal",1,true) or p.Name:find("Filete",1,true)
            or p.Name:find("Principal",1,true) or p.Name:find("Recorte",1,true) then
            if x < -3 then p.Position+=Vector3.new(11.4,0,0)
            elseif x > 3 then p.Position-=Vector3.new(11.4,0,0) end
        end
    end
end
stage.InicioLocal.Duration=0
stage.InicioLocal.Position=Vector3.new(0,-12,-19)
stage.Camaras.General.Value=CFrame.lookAt(Vector3.new(0,5.0,-16.5),Vector3.new(0,3.62,0))
workspace.CurrentCamera.CFrame=stage.Camaras.General.Value
workspace.CurrentCamera.Focus=CFrame.new(0,3.62,0)
stage:SetAttribute("RevisadoV4",true)
game:GetService("Selection"):Set({})
print("ZAREKV4_FIT_LISTO",#stage.R15:GetChildren(),#stage.Camaras:GetChildren())
