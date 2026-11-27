-- Local preview of the saved Studio presentation. No uploaded content is created.
local Players=game:GetService("Players")
local Lighting=game:GetService("Lighting")
local Input=game:GetService("UserInputService")
local RunService=game:GetService("RunService")
local StarterGui=game:GetService("StarterGui")
local stage=workspace:WaitForChild("ZAREK_V5_PRESENTACION")
local cameras=stage:WaitForChild("Camaras")
local player=Players.LocalPlayer
local activeShot
local viewConnection
local rigFolder=stage:WaitForChild("R15")
local cinema=false
local slot=0
local angle=1
local shots={"Frente_","TresCuartos_","PerfilDerecho_","Nuca_","PerfilIzquierdo_"}
local activeTracks={}
local testId=0
local fallback={Caminar="rbxassetid://507777826",Correr="rbxassetid://507767714",Saltar="rbxassetid://507765000"}
local defaultNames={Caminar="walk",Correr="run",Saltar="jump"}

local gui=Instance.new("ScreenGui")
gui.IgnoreGuiInset=false
gui.Name="ZarekReview"
gui.ResetOnSpawn=false
gui.Parent=player:WaitForChild("PlayerGui")
local quality=UserSettings():GetService("UserGameSettings")
local function reportQuality()
    print("ZAREKV5_CLIENTE", quality.SavedQualityLevel.Name)
end
quality:GetPropertyChangedSignal("SavedQualityLevel"):Connect(reportQuality)
reportQuality()

local status=Instance.new("TextLabel")
status.Name="Estado"
status.AnchorPoint=Vector2.new(.5,1)
status.Position=UDim2.new(.5,0,1,-17)
status.Size=UDim2.new(.85,0,0,38)
status.BackgroundColor3=Color3.fromRGB(13,21,36)
status.BackgroundTransparency=.17
status.TextColor3=Color3.fromRGB(222,232,251)
status.TextSize=17
status.Font=Enum.Font.Gotham
status.Parent=gui

local hint="V5  ·  0–3 Cámaras  ·  V Ángulo  ·  L Luz  ·  7 Caminar  ·  8 Correr  ·  9 Saltar"
local function frame()
    local key=slot==0 and "General" or shots[angle]..slot
    local shot=cameras:WaitForChild(key)
    activeShot=shot
    for i, rig in rigFolder:GetChildren() do
        local visible=slot==0 or slot==tonumber(rig.Name:sub(1,2))
        for _, object in rig:GetDescendants() do
            if object:IsA("BasePart") then object.LocalTransparencyModifier=visible and 0 or 1 end
        end
    end
    status.Text=(cinema and "Cinematográfica" or "Neutra").."    |    "..hint
end

local function light()
    Lighting.ClockTime=cinema and 18.25 or 14
    Lighting.Brightness=cinema and .90 or 1.37
    Lighting.Ambient=cinema and Color3.fromRGB(72,81,116) or Color3.fromRGB(145,145,151)
    Lighting.OutdoorAmbient=cinema and Color3.fromRGB(90,105,141) or Color3.fromRGB(156,155,157)
    Lighting.EnvironmentSpecularScale=cinema and .47 or .30
    for _, lightPart in stage:GetChildren() do
        local lamp=lightPart:FindFirstChildWhichIsA("SpotLight")
        if lamp and lightPart.Name:find("Recorte",1,true) then
            lamp.Brightness=cinema and 4.5 or 1.6
            lamp.Color=cinema and Color3.fromRGB(49,111,255) or Color3.fromRGB(250,248,255)
        end
    end
    frame()
end

local function getAnimation(rig,name)
    local animate=rig:FindFirstChild("Animate")
    local configured=animate and animate:FindFirstChild(defaultNames[name])
    local clip=configured and configured:FindFirstChildWhichIsA("Animation",true)
    local anim=Instance.new("Animation")
    anim.AnimationId=clip and clip.AnimationId or fallback[name]
    return anim
end

local function weldError(rig)
    local greatest=0
    local count=0
    for _, part in rig:GetChildren() do
        if part:IsA("Accessory") then
            local handle=part:FindFirstChildWhichIsA("MeshPart",true)
            local point=handle and handle:FindFirstChildWhichIsA("Attachment")
            local socket=point and rig.Head:FindFirstChild(point.Name)
            if socket then
                count+=1
                greatest=math.max(greatest,(point.WorldPosition-socket.WorldPosition).Magnitude)
            end
        end
    end
    return greatest,count
end

local function play(name)
    testId+=1
    local current=testId
    for _, track in activeTracks do track:Stop(.12) end
    table.clear(activeTracks)
    local played=0
    for _, rig in rigFolder:GetChildren() do
        local animator=rig.Humanoid:FindFirstChildOfClass("Animator")
        if animator then
            local track=animator:LoadAnimation(getAnimation(rig,name))
            track.Priority=Enum.AnimationPriority.Action
            track.Looped=true
            track:Play(.16,1,name=="Correr" and 1.12 or 1)
            table.insert(activeTracks,track)
        end
    end
    task.spawn(function()
        local maximum=0
        local anchorCount=0
        local sample=0
        for i=1,20 do
            task.wait(.09)
            if testId~=current then return end
            if i==10 then
                for _, track in activeTracks do if track.IsPlaying and track.Length>0 then played+=1 end end
            end
            for _, rig in rigFolder:GetChildren() do
                local err,count=weldError(rig)
                maximum=math.max(maximum,err)
                anchorCount=math.max(anchorCount,count)
            end
            sample+=1
        end
        local summary=string.format("%s  ·  %d/3 clips  ·  %d muestras  ·  desvío máx. %.5f studs",name,played,sample,maximum)
        print("ZAREKV5_ANIM",name,"clips",played,"samples",sample,"maxStuds",maximum,"maxAnchors",anchorCount)
        status.Text=summary
    end)
end

Input.InputBegan:Connect(function(key,busy)
    if busy then return end
    local code=key.KeyCode
    if code==Enum.KeyCode.Zero then slot=0 frame()
    elseif code==Enum.KeyCode.One then slot=1 angle=1 frame()
    elseif code==Enum.KeyCode.Two then slot=2 angle=1 frame()
    elseif code==Enum.KeyCode.Three then slot=3 angle=1 frame()
    elseif code==Enum.KeyCode.V then angle=angle%#shots+1 frame()
    elseif code==Enum.KeyCode.L then cinema=not cinema light()
    elseif code==Enum.KeyCode.Seven then play("Caminar")
    elseif code==Enum.KeyCode.Eight then play("Correr")
    elseif code==Enum.KeyCode.Nine then play("Saltar")
    end
end)

local function hideItem(item)
    if item:IsA("BasePart") then
        item.LocalTransparencyModifier=1
    elseif item:IsA("Decal") then
        item.Transparency=1
    elseif item:IsA("ParticleEmitter") or item:IsA("Trail") or item:IsA("Beam") then
        item.Enabled=false
    end
end

local function hidePlayer(character)
    for _, item in character:GetDescendants() do hideItem(item) end
    if viewConnection then viewConnection:Disconnect() end
    viewConnection=character.DescendantAdded:Connect(hideItem)
end

for _, name in {"Chat","PlayerList","Backpack","Health","EmotesMenu"} do
    pcall(function() StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType[name],false) end)
end
if player.Character then hidePlayer(player.Character) end
player.CharacterAdded:Connect(hidePlayer)
RunService:BindToRenderStep("ZarekReviewView",Enum.RenderPriority.Camera.Value+1,function()
    local camera=workspace.CurrentCamera
    if not camera or not activeShot then return end
    camera.CameraType=Enum.CameraType.Scriptable
    camera.FieldOfView=activeShot:GetAttribute("FOV")
    camera.CFrame=activeShot.Value
end)
light()
