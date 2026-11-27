-- Run in the Command Bar of the local V4 stage copy after generating V5 using AFT.
local storage = game:GetService("ServerStorage")
local stage = assert(workspace:FindFirstChild("ZAREK_V4_PRESENTACION"), "Abre una copia local del escenario V4")
local refs = assert(storage:FindFirstChild("Origenes_V4"))
local sources = {}
for _, obj in workspace:GetChildren() do
    if obj:IsA("Accessory") and obj:FindFirstChild("HairAttachment", true) then
        table.insert(sources, obj)
    end
end
assert(#sources == 1, "Se requiere un único accesorio Pelo recién generado mediante AFT")
local source = sources[1]
local sourceHandle = assert(source:FindFirstChildWhichIsA("MeshPart"))
local surface = assert(sourceHandle:FindFirstChildOfClass("SurfaceAppearance"))
local sourcePoint = assert(sourceHandle:FindFirstChild("HairAttachment"))
assert(surface.ColorMapContent.SourceType ~= Enum.ContentSourceType.None)
assert(surface.NormalMapContent.SourceType ~= Enum.ContentSourceType.None)
assert(surface.RoughnessMapContent.SourceType ~= Enum.ContentSourceType.None)
source.Name = "CelestialHair_V5_AFT"
source.AccessoryType = Enum.AccessoryType.Hair
sourceHandle.Material = Enum.Material.Plastic
sourceHandle.Color = Color3.new(1, 1, 1)
sourceHandle.RenderFidelity = Enum.RenderFidelity.Precise

local shots = {
    Frente = Vector3.new(0, .36, -4.95),
    TresCuartos = Vector3.new(3.02, .73, -4.23),
    PerfilDerecho = Vector3.new(5.05, .43, 0),
    Nuca = Vector3.new(0, .61, 4.95),
    PerfilIzquierdo = Vector3.new(-5.05, .43, 0),
}

local function replaceHair(rig)
    local equipped = rig:FindFirstChild(source.Name)
    if equipped then return equipped:FindFirstChildWhichIsA("MeshPart") end
    local oldHair
    for _, entry in rig:GetChildren() do
        if entry:IsA("Accessory") and entry.AccessoryType == Enum.AccessoryType.Hair then
            oldHair = entry
            break
        end
    end
    assert(oldHair, rig.Name)
    local newHair = source:Clone()
    local handle = newHair:FindFirstChildWhichIsA("MeshPart")
    local point = handle:FindFirstChild("HairAttachment")
    for _, child in handle:GetChildren() do
        if child:IsA("Weld") or child:IsA("WeldConstraint") then child:Destroy() end
    end
    handle.Anchored, handle.Massless = false, true
    handle.CanCollide, handle.CanQuery, handle.CanTouch = false, false, false
    local socket = rig.Head.HairAttachment
    handle.CFrame = socket.WorldCFrame * point.CFrame:Inverse()
    newHair.Parent = rig
    local weld = Instance.new("Weld")
    weld.Name = "AccessoryWeld"
    weld.Part0, weld.Part1, weld.C0, weld.C1 = handle, rig.Head, point.CFrame, socket.CFrame
    weld.Parent = handle
    oldHair.Name = "Cabello_V4_" .. rig.Name
    oldHair.Parent = refs
    print("ZAREKV5_MALLA", rig.Name, handle.Size, point.Name, sourceHandle.RenderFidelity.Name,
          surface.ColorMapContent.SourceType.Name, surface.NormalMapContent.SourceType.Name,
          surface.RoughnessMapContent.SourceType.Name)
    return handle
end

local function seatHeadwear(rig)
    for _, accessory in rig:GetChildren() do
        if accessory:IsA("Accessory") and accessory.AccessoryType ~= Enum.AccessoryType.Hair then
            local handle = accessory:FindFirstChildWhichIsA("MeshPart")
            local anchor = handle and handle:FindFirstChildWhichIsA("Attachment")
            local socket = anchor and rig.Head:FindFirstChild(anchor.Name)
            if socket and not accessory:GetAttribute("ColocacionV5") then
                local isCrown = accessory.Name:find("Foundation", 1, true) ~= nil
                local dy = isCrown and -.030 or 0
                local desired = handle.CFrame + Vector3.new(0, dy, 0)
                anchor.CFrame = desired:ToObjectSpace(socket.WorldCFrame)
                handle.CFrame = desired
                local weld = handle:FindFirstChild("AccessoryWeld") or Instance.new("Weld")
                weld.Name = "AccessoryWeld"
                weld.Part0, weld.Part1, weld.C0, weld.C1 = handle, rig.Head, anchor.CFrame, socket.CFrame
                weld.Parent = handle
                accessory:SetAttribute("ColocacionV5", true)
                if isCrown then print("ZAREKV5_CORONA", rig.Name, dy) end
            end
        end
    end
end

for slot = 1, 3 do
    local rig = stage.R15[string.format("%02d_R15", slot)]
    replaceHair(rig)
    seatHeadwear(rig)
    local point = rig.Head.Position + Vector3.new(0, slot == 3 and .81 or slot == 2 and .35 or .25, 0)
    for name, offset in shots do
        local id = name .. "_" .. slot
        local shot = stage.Camaras:FindFirstChild(id) or Instance.new("CFrameValue")
        shot.Name = id
        shot.Value = CFrame.lookAt(point + offset, point)
        shot:SetAttribute("FOV", slot == 3 and 42 or slot == 2 and 36 or 29)
        shot.Parent = stage.Camaras
    end
end

local layer = workspace:FindFirstChild("Scene")
if layer and layer:IsA("Model") then
    layer.Name = "Importacion_V5_Original"
    layer.Parent = refs
end
source.Parent = refs
stage.Name = "ZAREK_V5_PRESENTACION"
stage:SetAttribute("CoronaDesplazamientoY", -.030)
stage:SetAttribute("VersionCabello", "V5")
local title = stage["Pedestal 01"]:FindFirstChildWhichIsA("SurfaceGui"):FindFirstChildWhichIsA("TextLabel")
title.Text = "01  CELESTIAL HAIR V5"
game:GetService("Selection"):Set({})
print("ZAREKV5_ESCENA", #stage.R15:GetChildren(), #stage.Camaras:GetChildren(), sourcePoint.Name)
