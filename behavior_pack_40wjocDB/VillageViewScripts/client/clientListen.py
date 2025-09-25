# -*- coding: utf-8 -*-

from .. import modConfig
from baseClient import (
    BaseClient, Listen, CF, LID, PID, clientApi
)


class ClientListen(BaseClient):

    def __init__(self, namespace, systemName):
        BaseClient.__init__(self, namespace, systemName)
        self.chooseMenuNode = None
        self.placeHudNode = None
        self.placeData = {}
        self.framesList1 = []
        self.framesList2= []
        self.framesList3 = []
        self.undoPlaceData = []
        self.ListenForEvent(modConfig.MOD_NAME,modConfig.SERVER_SYSTEM,"RenderVillage",self,self.RenderVillage)

    @Listen("UiInitFinished")
    def UiInitFinished(self, args):
        clientApi.RegisterUI(
            modConfig.MOD_NAME,
            "VillageView",
            modConfig.UI_BASE_PATH + "VillageView.VillageView",
            "village_view.main"
        )
    def RenderVillage(self,args):
        min_x = args["min_x"]
        max_x = args["max_x"]
        mix_y = args["min_y"]
        max_y = args["max_y"]
        mix_z = args["min_z"]
        max_z = args["max_z"]
        self.placeData['size'] = (max_x - min_x, max_y - mix_y, max_z - mix_z)
        self.placeData['placePos'] = (min_x, mix_y, mix_z)
        self.placeData['centerPos'] = ((min_x + max_x) / 2,( mix_y + max_y )/ 2,( mix_z + max_z) / 2)
        self.placeData['ironPos'] = ((min_x + max_x) / 2 -8,( mix_y + max_y )/ 2-6,( mix_z + max_z) / 2-8)
        self.RefreshEffect()
    def RefreshEffect(self):
        #销毁之前序列帧
        self.CloseRender()
        #村庄边界        
        sizeX, sizeY, sizeZ = self.placeData['size']
        offsetX, offsetY, offsetZ = sizeX / 2.0, sizeY / 2.0, sizeZ / 2.0
        sX, sY, sZ = self.placeData['placePos']
        coverFramePos = [(sX + offsetX, sY + offsetY, sZ + 0.01), (sX + 0.01, sY + offsetY, sZ + offsetZ),
                         (sX + offsetX, sY + 0.01, sZ + offsetZ), (sX + offsetX, sY + offsetY, sZ + sizeZ - 0.01),
                         (sX + sizeX - 0.01, sY + offsetY, sZ + offsetZ),
                         (sX + offsetX, sY + sizeY - 0.01, sZ + offsetZ)]
        lineFramePos = [(sX + offsetX, sY, sZ), (sX + offsetX, sY + sizeY, sZ), (sX + offsetX, sY + sizeY, sZ + sizeZ),
                        (sX + offsetX, sY, sZ + sizeZ),
                        (sX, sY + offsetY, sZ), (sX + sizeX, sY + offsetY, sZ), (sX + sizeX, sY + offsetY, sZ + sizeZ),
                        (sX, sY + offsetY, sZ + sizeZ),
                        (sX, sY, sZ + offsetZ), (sX + sizeX, sY, sZ + offsetZ), (sX + sizeX, sY + sizeY, sZ + offsetZ),
                        (sX, sY + sizeY, sZ + offsetZ)]
        coverFrameRotate = [(0, 0, 0), (0, 90, 0), (90, 0, 0),
                            (0, 0, 0), (0, 90, 0), (90, 0, 0)]
        lineFrameRot = [(0, 0, 90), (0, 0, 0), (90, 0, 0)]
        coverFrameScale = [(offsetX, offsetY, 1), (offsetZ, offsetY, 1), (offsetX, offsetZ, 1),
                           (offsetX, offsetY, 1), (offsetZ, offsetY, 1), (offsetX, offsetZ, 1)]
        lineFrameScale = [(1, sizeX, 1), (1, sizeY, 1), (1, sizeZ, 1)]
        # self.framesList1 = [self.CreateEngineSfxFromEditor(
        #     'effects/building_frame.json', coverFramePos[i], coverFrameRotate[i], coverFrameScale[i]) for i in range(6)]
        self.framesList1 += [self.CreateEngineSfxFromEditor(
            'effects/building_frame_line.json', lineFramePos[i], lineFrameRot[i // 4], lineFrameScale[i // 4]) for i in
            range(12)]
        for frame in self.framesList1:
            frameAniControlComp = CF.CreateFrameAniControl(frame)
            frameAniControlComp.SetMixColor((1, 0, 0, 0.8))
            frameAniControlComp.SetDeepTest(False)
            frameAniControlComp.Play()
        #村庄中心
        sizeX, sizeY, sizeZ = 1,1,1
        offsetX, offsetY, offsetZ = sizeX / 2.0, sizeY / 2.0, sizeZ / 2.0
        sX, sY, sZ = self.placeData['centerPos']
        coverFramePos = [(sX + offsetX, sY + offsetY, sZ + 0.01), (sX + 0.01, sY + offsetY, sZ + offsetZ),
                         (sX + offsetX, sY + 0.01, sZ + offsetZ), (sX + offsetX, sY + offsetY, sZ + sizeZ - 0.01),
                         (sX + sizeX - 0.01, sY + offsetY, sZ + offsetZ),
                         (sX + offsetX, sY + sizeY - 0.01, sZ + offsetZ)]
        lineFramePos = [(sX + offsetX, sY, sZ), (sX + offsetX, sY + sizeY, sZ), (sX + offsetX, sY + sizeY, sZ + sizeZ),
                        (sX + offsetX, sY, sZ + sizeZ),
                        (sX, sY + offsetY, sZ), (sX + sizeX, sY + offsetY, sZ), (sX + sizeX, sY + offsetY, sZ + sizeZ),
                        (sX, sY + offsetY, sZ + sizeZ),
                        (sX, sY, sZ + offsetZ), (sX + sizeX, sY, sZ + offsetZ), (sX + sizeX, sY + sizeY, sZ + offsetZ),
                        (sX, sY + sizeY, sZ + offsetZ)]
        coverFrameRotate = [(0, 0, 0), (0, 90, 0), (90, 0, 0),
                            (0, 0, 0), (0, 90, 0), (90, 0, 0)]
        lineFrameRot = [(0, 0, 90), (0, 0, 0), (90, 0, 0)]
        coverFrameScale = [(offsetX, offsetY, 1), (offsetZ, offsetY, 1), (offsetX, offsetZ, 1),
                           (offsetX, offsetY, 1), (offsetZ, offsetY, 1), (offsetX, offsetZ, 1)]
        lineFrameScale = [(1, sizeX, 1), (1, sizeY, 1), (1, sizeZ, 1)]
        self.framesList2 += [self.CreateEngineSfxFromEditor(
            'effects/building_frame.json', coverFramePos[i], coverFrameRotate[i], coverFrameScale[i]) for i in range(6)]
        self.framesList2 += [self.CreateEngineSfxFromEditor(
            'effects/building_frame_line.json', lineFramePos[i], lineFrameRot[i // 4], lineFrameScale[i // 4]) for i in
            range(12)]
        for frame in self.framesList2:
            frameAniControlComp = CF.CreateFrameAniControl(frame)
            frameAniControlComp.SetMixColor((1, 1, 0, 0.12))
            frameAniControlComp.SetDeepTest(False)
            frameAniControlComp.Play()
        #铁傀儡
        sizeX, sizeY, sizeZ = 17,13,17
        offsetX, offsetY, offsetZ = sizeX / 2.0, sizeY / 2.0, sizeZ / 2.0
        sX, sY, sZ = self.placeData['ironPos']
        coverFramePos = [(sX + offsetX, sY + offsetY, sZ + 0.01), (sX + 0.01, sY + offsetY, sZ + offsetZ),
                         (sX + offsetX, sY + 0.01, sZ + offsetZ), (sX + offsetX, sY + offsetY, sZ + sizeZ - 0.01),
                         (sX + sizeX - 0.01, sY + offsetY, sZ + offsetZ),
                         (sX + offsetX, sY + sizeY - 0.01, sZ + offsetZ)]
        lineFramePos = [(sX + offsetX, sY, sZ), (sX + offsetX, sY + sizeY, sZ), (sX + offsetX, sY + sizeY, sZ + sizeZ),
                        (sX + offsetX, sY, sZ + sizeZ),
                        (sX, sY + offsetY, sZ), (sX + sizeX, sY + offsetY, sZ), (sX + sizeX, sY + offsetY, sZ + sizeZ),
                        (sX, sY + offsetY, sZ + sizeZ),
                        (sX, sY, sZ + offsetZ), (sX + sizeX, sY, sZ + offsetZ), (sX + sizeX, sY + sizeY, sZ + offsetZ),
                        (sX, sY + sizeY, sZ + offsetZ)]
        coverFrameRotate = [(0, 0, 0), (0, 90, 0), (90, 0, 0),
                            (0, 0, 0), (0, 90, 0), (90, 0, 0)]
        lineFrameRot = [(0, 0, 90), (0, 0, 0), (90, 0, 0)]
        coverFrameScale = [(offsetX, offsetY, 1), (offsetZ, offsetY, 1), (offsetX, offsetZ, 1),
                           (offsetX, offsetY, 1), (offsetZ, offsetY, 1), (offsetX, offsetZ, 1)]
        lineFrameScale = [(1, sizeX, 1), (1, sizeY, 1), (1, sizeZ, 1)]
        # self.framesList3 += [self.CreateEngineSfxFromEditor(
        #     'effects/building_frame.json', coverFramePos[i], coverFrameRotate[i], coverFrameScale[i]) for i in range(6)]
        self.framesList3 += [self.CreateEngineSfxFromEditor(
            'effects/building_frame_line.json', lineFramePos[i], lineFrameRot[i // 4], lineFrameScale[i // 4]) for i in
            range(12)]
        for frame in self.framesList3:
            frameAniControlComp = CF.CreateFrameAniControl(frame)
            frameAniControlComp.SetMixColor((0, 0, 1, 0.8))
            frameAniControlComp.SetDeepTest(False)
            frameAniControlComp.Play()
    def CloseRender(self,args=None):
                #销毁之前序列帧
        if self.framesList1:
            for frame in self.framesList1:
                self.DestroyEntity(frame)
                self.framesList1 = []
        if self.framesList2:
            for frame in self.framesList2:
                self.DestroyEntity(frame)
                self.framesList2 = []
        if self.framesList3:
            for frame in self.framesList3:
                self.DestroyEntity(frame)
                self.framesList3 = []
    def OnVillageCommand(self,args):
        self.UINode = clientApi.PushScreen(modConfig.MOD_NAME,"VillageView")
    def CheckVillage(self,args):
        speed = self.UINode.speed
        isAllPlayer = self.UINode.is_all_player
        clientApi.PopTopUI()
        self.CallServer("CheckVillage", {"__id__":PID,"speed":speed,"isAllPlayer":isAllPlayer})
    @Listen("RightClickBeforeClientEvent")
    def RightClickBeforeClientEvent(self, args):
        itemDict = CF.CreateItem(PID).GetCarriedItem()
        if itemDict and itemDict["newItemName"] == "minecraft:stick":
            self.UINode = clientApi.PushScreen(modConfig.MOD_NAME,"VillageView")
            
    @Listen("HoldBeforeClientEvent")
    def HoldBeforeClientEvent(self, args):
        itemDict = CF.CreateItem(PID).GetCarriedItem()
        if itemDict and itemDict["newItemName"] == "minecraft:stick":
            self.UINode = clientApi.PushScreen(modConfig.MOD_NAME,"VillageView")


    
