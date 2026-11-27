-- Run in the CelestialHair_Test.rbxl copy after AFT produced the local Hair accessory.
local Storage = game:GetService("ServerStorage")
local Lighting = game:GetService("Lighting")
local Players = game:GetService("Players")
local StarterPlayer = game:GetService("StarterPlayer")
assert(not workspace:FindFirstChild("ZAREK_V4_PRESENTACION"), "El escenario V4 ya existe.")

local function attachmentOf(accessory)
    return accessory:FindFirstChildWhichIsA("Attachment", true)
end

local hair, crown, halo
for _, item in workspace:GetChildren() do
    if item:IsA("Accessory") then
        local anchor = attachmentOf(item)
        if anchor and anchor.Name == "HairAttachment" then
            hair = item
        elseif item.Name == "Zenith" then
            halo = item
        elseif item.Name:find("Foundation",1,true) then
            crown = item
        end
    end
end
assert(hair and crown and halo, "Faltan Pelo generado mediante AFT, Divine Crown o Eternal Halo.")
local hairPart = hair:FindFirstChildWhichIsA("MeshPart",true)
local surface = hairPart and hairPart:FindFirstChildWhichIsA("SurfaceAppearance")
assert(surface, "El MeshPart generado por AFT debe conservar SurfaceAppearance.")
hair.Name = "CelestialHair_V4_AFT"
hair.AccessoryType = Enum.AccessoryType.Hair
hairPart.Material = Enum.Material.Plastic
hairPart.Color = Color3.new(1,1,1)

local refs = Instance.new("Folder")
refs.Name = "Origenes_V4"
refs.Parent = Storage
for _, item in workspace:GetChildren() do
    if item:IsA("Model") or item:IsA("Accessory") or item:IsA("SpawnLocation") then
        item.Parent = refs
    end
end

local stage = Instance.new("Folder")
stage.Name = "ZAREK_V4_PRESENTACION"
stage.Parent = workspace

local function block(name,size,position,color,material,into)
    local p = Instance.new("Part")
    p.Name,p.Size,p.Position,p.Color,p.Material = name,size,position,color,material
    p.Anchored = true
    p.TopSurface,p.BottomSurface = Enum.SurfaceType.Smooth,Enum.SurfaceType.Smooth
    p.Parent = into or stage
    return p
end

local slate = Color3.fromRGB(20,26,39)
local silver = Color3.fromRGB(113,132,161)
local blue = Color3.fromRGB(42,114,240)
block("Ciclorama · pared",Vector3.new(90,31,1),Vector3.new(0,11,13),slate,Enum.Material.SmoothPlastic)
block("Ciclorama · suelo",Vector3.new(90,1,85),Vector3.new(0,-.65,1),slate,Enum.Material.SmoothPlastic)
local rigs = Instance.new("Folder")
rigs.Name = "R15"
rigs.Parent = stage
local cameras = Instance.new("Folder")
cameras.Name = "Camaras"
cameras.Parent = stage

local function viewpoint(name,position,focus,fov)
    local value = Instance.new("CFrameValue")
    value.Name = name
    value.Value = CFrame.lookAt(position,focus)
    value:SetAttribute("FOV",fov)
    value.Parent = cameras
end

local function keyLight(name,spot,focus,color,power,radius,angle)
    local mount=block(name,Vector3.new(.15,.15,.15),spot,color,Enum.Material.SmoothPlastic)
    mount.LocalTransparencyModifier=1
    mount.Transparency=1
    mount.CanCollide=false
    mount.CanQuery=false
    mount.CFrame=CFrame.lookAt(spot,focus)
    local lamp=Instance.new("SpotLight")
    lamp.Face=Enum.NormalId.Front
    lamp.Color,lamp.Brightness,lamp.Range,lamp.Angle=color,power,radius,angle
    lamp.Shadows=true
    lamp.Parent=mount
end

local function equip(rig, original)
    local cloned=original:Clone()
    local handle=assert(cloned:FindFirstChildWhichIsA("MeshPart",true) or cloned:FindFirstChildWhichIsA("BasePart",true))
    local mount=assert(attachmentOf(cloned))
    local head=rig:FindFirstChild("Head")
    local target=assert(head:FindFirstChild(mount.Name),mount.Name)
    for _, item in cloned:GetDescendants() do
        if item:IsA("Weld") or item:IsA("WeldConstraint") then item.Parent=nil end
    end
    handle.Anchored=false
    handle.CanCollide=false
    handle.CanTouch=false
    handle.CanQuery=false
    handle.Massless=true
    handle.CFrame=target.WorldCFrame*mount.CFrame:Inverse()
    cloned.Parent=rig
    local weld=Instance.new("Weld")
    weld.Name="AccessoryWeld"
    weld.Part0,weld.Part1=handle,head
    weld.C0,weld.C1=mount.CFrame,target.CFrame
    weld.Parent=handle
    return cloned
end

local locations={-5.7,0,5.7}
local titles={"01  CELESTIAL HAIR","02  + DIVINE CROWN","03  + ETERNAL HALO"}
for i,x in ipairs(locations) do
    local description=Instance.new("HumanoidDescription")
    local clay=Color3.fromRGB(148,153,166)
    description.HeadColor,description.TorsoColor=clay,clay
    description.LeftArmColor,description.RightArmColor=clay,clay
    description.LeftLegColor,description.RightLegColor=clay,clay
    local rig=Players:CreateHumanoidModelFromDescriptionAsync(description,Enum.HumanoidRigType.R15)
    rig.Name=string.format("%02d_R15",i)
    rig.Parent=rigs
    rig:PivotTo(CFrame.new(x,3.10,0))
    rig.HumanoidRootPart.Anchored=true
    rig.Humanoid.DisplayDistanceType=Enum.HumanoidDisplayDistanceType.None
    equip(rig,hair)
    if i>=2 then equip(rig,crown) end
    if i>=3 then equip(rig,halo) end

    local podium=block(string.format("Pedestal %02d",i),Vector3.new(4.55,.54,3.8),Vector3.new(x,.17,.35),slate,Enum.Material.SmoothPlastic)
    block("Filete de plata",Vector3.new(4.54,.045,3.81),podium.Position+Vector3.new(0,.25,0),silver,Enum.Material.SmoothPlastic)
    local tag=Instance.new("SurfaceGui")
    tag.Face=Enum.NormalId.Front
    tag.CanvasSize=Vector2.new(750,85)
    tag.LightInfluence=0
    tag.Parent=podium
    local label=Instance.new("TextLabel")
    label.Size=UDim2.fromScale(1,1)
    label.BackgroundTransparency=1
    label.Text=titles[i]
    label.Font=Enum.Font.GothamMedium
    label.TextColor3=Color3.fromRGB(213,224,250)
    label.TextScaled=true
    label.Parent=tag

    local head=rig.Head.Position
    viewpoint("Frente_"..i,head+Vector3.new(0,.55,-6.05),head+Vector3.new(0,.47,0),34)
    viewpoint("TresCuartos_"..i,head+Vector3.new(2.8,1.2,-5.9),head+Vector3.new(0,.45,0),34)
    viewpoint("Nuca_"..i,head+Vector3.new(1.1,.80,6.0),head+Vector3.new(0,.43,0),34)
    keyLight("Principal "..i,head+Vector3.new(-2.5,2.6,-3.90),head,Color3.fromRGB(255,248,237),3.1,10,82)
    keyLight("Recorte "..i,head+Vector3.new(2.1,1.9,2.75),head,blue,2.5,9,72)
end
viewpoint("General",Vector3.new(0,5.2,-18),Vector3.new(0,3.50,0),44)

Lighting.ClockTime=13.7
Lighting.Brightness=1.37
Lighting.Ambient=Color3.fromRGB(128,135,153)
Lighting.OutdoorAmbient=Color3.fromRGB(148,149,164)
Lighting.EnvironmentSpecularScale=.30
Lighting.EnvironmentDiffuseScale=.60

local controller=Instance.new("LocalScript")
controller.Name="PresentacionV4"
controller.Parent=StarterPlayer.StarterPlayerScripts
local spawn=Instance.new("SpawnLocation")
spawn.Name="InicioLocal"
spawn.Position=Vector3.new(0,.5,-19)
spawn.Anchored=true
spawn.Transparency=1
spawn.Neutral=true
spawn.Parent=stage
game:GetService("Selection"):Set({rigs:FindFirstChild("03_R15")})
print("ZAREK_V4_ESCENA",#rigs:GetChildren(),hair.AccessoryType.Name,
    attachmentOf(hair).Name,#cameras:GetChildren(),surface.ClassName)
