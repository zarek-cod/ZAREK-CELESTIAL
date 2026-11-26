-- Execute in Roblox Studio's command bar after importing C as "Scene" with upload off.
local LIMIT = 46
local source
for _, object in workspace:GetChildren() do
    if object:IsA("Model") and (object.Name == "Scene" or object.Name == "CelestialHair_V3_C_MASTER") then
        local meshCount = 0
        for _, part in object:GetDescendants() do
            if part:IsA("MeshPart") then
                meshCount += 1
            end
        end
        if meshCount == LIMIT then source = object break end
    end
end
assert(source, "Import the C MASTER with all 46 meshes into the local Workspace.")
local avatar = workspace:FindFirstChild("ZAREK_V3_R15_Studio")
if not avatar then
    local descriptions = Instance.new("HumanoidDescription")
    local skin = Color3.fromRGB(143, 142, 151)
    descriptions.HeadColor, descriptions.TorsoColor = skin, skin
    descriptions.LeftArmColor, descriptions.RightArmColor = skin, skin
    descriptions.LeftLegColor, descriptions.RightLegColor = skin, skin
    avatar = game:GetService("Players"):CreateHumanoidModelFromDescriptionAsync(descriptions, Enum.HumanoidRigType.R15)
    avatar.Name = "ZAREK_V3_R15_Studio"
    avatar.Parent = workspace
    avatar:PivotTo(CFrame.new(30, 4, 0))
    avatar:WaitForChild("HumanoidRootPart").Anchored = true
    local humanoid = avatar:FindFirstChildOfClass("Humanoid")
    humanoid.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
    for _, asset in workspace:GetChildren() do
        if asset:IsA("Accessory") then
            humanoid:AddAccessory(asset:Clone())
        end
    end
end
local head = avatar:WaitForChild("Head")
local humanoid = avatar:FindFirstChildOfClass("Humanoid")
local prior = avatar:FindFirstChild("CelestialHair_V3_C_MASTER")
if prior and prior ~= source then
    prior.Name = "CelestialHair_V3_C_Prueba_Anterior"
    prior.Parent = game:GetService("ServerStorage")
end
local hairAttachment = head:WaitForChild("HairAttachment")
source.Name = "CelestialHair_V3_C_MASTER"
source:PivotTo(hairAttachment.WorldCFrame * CFrame.new(0, .091, 0))
source.Parent = avatar
for _, part in source:GetDescendants() do
    if part:IsA("BasePart") then part.Anchored = true part.CanCollide = false end
end
game:GetService("Selection"):Set({head})
local meshCount, surfaceCount, accessoryCount, weldCount = 0, 0, 0, 0
for _, item in source:GetDescendants() do
    if item:IsA("MeshPart") then meshCount += 1 end
    if item:IsA("SurfaceAppearance") then surfaceCount += 1 end
end
for _, item in avatar:GetChildren() do
    if item:IsA("Accessory") then
        accessoryCount += 1
        local handle = item:FindFirstChild("Handle")
        if handle and handle:FindFirstChild("AccessoryWeld") then weldCount += 1 end
    end
end
print("ZAREK_V3_STUDIO", humanoid.RigType.Name, "C meshes", meshCount,
    "surfaces", surfaceCount, "cloned accessories", accessoryCount, "welds", weldCount)
