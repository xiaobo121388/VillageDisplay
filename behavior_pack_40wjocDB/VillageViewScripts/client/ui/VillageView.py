# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
from ... import modConfig

ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()
CF = clientApi.GetEngineCompFactory()
LID = clientApi.GetLevelId()
CT = clientApi.GetSystem(modConfig.MOD_NAME, modConfig.CLIENT_SYSTEM)


class VillageView(ScreenNode):

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.speed = "slow"
        self.is_all_player = False
    def Create(self):
        buttonUIControl = self.GetBaseUIControl("/image/title/button").asButton()
        buttonUIControl.AddTouchEventParams({"isSwallow":True})
        buttonUIControl.SetButtonTouchUpCallback(self.close)
        buttonUIControl = self.GetBaseUIControl("/image/button").asButton()
        buttonUIControl.AddTouchEventParams({"isSwallow":True,"speed":self.speed,"isAllPlayer":self.is_all_player})
        buttonUIControl.SetButtonTouchUpCallback(CT.CheckVillage)

    def close(self, args):
        clientApi.PopTopUI()
    @ViewBinder.binding(ViewBinder.BF_ToggleChanged, "#village_view")
    def OnItemToggleChecked(self, args):
        toggleIndex = args["index"]
        if toggleIndex == 0 :
            self.speed = "slow"
        elif toggleIndex == 1 :
            self.speed = "normal"
        else :
            self.speed = "fast"
    @ViewBinder.binding(ViewBinder.BF_ToggleChanged, "#village_view_all_player")
    def OnItemToggleChecked(self, args):
        state = args["state"]
        # baseUIControl = self.GetBaseUIControl("/image/tip")
        # baseUIControl.SetVisible(False)
        if state == True :
            if clientApi.GetHostPlayerId() == clientApi.GetLocalPlayerId():
                self.is_all_player = True

            else:
                print("[!] 当前不是自己，无法开启所有玩家模式")
                baseUIControl = self.GetBaseUIControl("/image/tip")
                baseUIControl.SetVisible(True)
                switchToggleUIControl = self.GetBaseUIControl("/image/switch_toggle(2)").asSwitchToggle()
                switchToggleUIControl.SetToggleState(False)

        else :
            self.is_all_player = False

