# -*- coding: utf-8 -*-

from .. import modConfig
from baseServer import (
    BaseServer, Listen, CF, LID, serverApi
)

class ServerListen(BaseServer):
    def __init__(self, namespace, systemName):
        # 初始化村庄检测相关变量
        BaseServer.__init__(self, namespace, systemName)
        self.Searching = False  # 是否正在搜索村庄
        self.visited = set()    # 已访问过的方块坐标
        self.village_blocks = set()  # 检测到的村庄方块
        self.multiVillageDetected = False  # 是否检测到多村融合
        self.checkQueue = []    # 待检测队列
        self.dimension = 0      # 维度ID
        self.helper_entities = []  # 辅助实体列表
        self.eid_to_spawnpos = {}  # 实体ID到坐标映射
        self.start_pos = None   # 搜索起始坐标
        self.startY = None      # 搜索起始Y坐标
        self.max_checks = 200000  # 最大检测次数
        self.checks_done = 0    # 已检测次数
        self.max_y_delta = 64   # Y轴最大偏移
        self.phase = 1          # 搜索阶段
        self.bounds = None      # 村庄边界
        self.refine_axis = None
        self.refine_direction = None
        self.pid = None         # 玩家ID
        self.speed = 50         # 搜索速度
        self.isAllPlayer = False # 是否所有玩家可见
        self.Killing = False    # 是否正在清理辅助实体
        # 定时清理辅助实体
        CF.CreateGame(LID).AddRepeatedTimer(60,self.KillHelper)

    @Listen("ServerChatEvent")
    def ServerChatEvent(self,args):
        # 聊天事件监听，关闭渲染命令
        pid = args["playerId"]
        message = args["message"]
        if message == "关闭渲染":
            self.CallClient(pid,"CloseRender",{})

    @Listen("CustomCommandTriggerServerEvent")
    def CustomCommandTriggerServerEvent(self,args):
        # 自定义命令触发监听
        if args["command"] == "village":
            pid = args["origin"].get("entityId",None)
            if pid:
                self.CallClient(pid,"OnVillageCommand",{})
            else:
                args["return_failed"] = True

    def KillHelper(self,args=None):
        # 清理所有辅助实体
        self.Killing = True
        eid_list = CF.CreateGame(LID).GetLoadActors()
        for eid in eid_list:
            if CF.CreateEngineType(eid).GetEngineTypeStr() == "village_view:helper":
                self.DestroyEntity(eid)
        self.Killing = False

    @staticmethod
    def PosToStr(x, y, z):
        # 坐标转字符串
        return "{}_{}_{}".format(int(x), int(y), int(z))

    @staticmethod
    def StrToPos(posStr):
        # 字符串转坐标
        return map(int, posStr.split("_"))

    @staticmethod
    def GetAdjacentPositions(x, y, z):
        # 获取六个方向的邻居坐标
        return [
            (x + 1, y, z), (x - 1, y, z),
            (x, y + 1, z), (x, y - 1, z),
            (x, y, z + 1), (x, y, z - 1)
        ]

    @staticmethod
    def GetAdjacentPositionsStep(x, y, z, step):
        # 获取指定步长的邻居坐标
        return [
            (x + step, y, z), (x - step, y, z),
            (x, y + step, z), (x, y - step, z),
            (x, y, z + step), (x, y, z - step)
        ]

    def CheckVillage(self, args):
        # 开始村庄检测
        pid = args["__id__"]
        speed = args["speed"]
        # 设置检测速度
        if speed == "slow":
            self.speed = 50
        elif speed == "normal":
            self.speed = 150
        elif speed == "fast":
            self.speed = 250
        # 如果正在清理辅助实体，延迟检测
        if self.Killing:
            CF.CreateGame(LID).AddTimer(1,self.CheckVillage,args)
            return
        self.isAllPlayer = args["isAllPlayer"]
        if self.Searching:
            CF.CreateGame(LID).SetTipMessage(serverApi.GenerateColor("RED") + "正在搜索中，请稍后")
            print("正在搜索中，请稍后")
            return
        CF.CreateGame(LID).SetTipMessage(serverApi.GenerateColor("GREEN") + "开始搜索,请确保村庄正在加载中，并且耐心等待...")
        self.Searching = True
        self.village_blocks = set()
        self.visited = set()
        self.checkQueue = []
        self.helper_entities = []
        self.eid_to_spawnpos = {}
        self.multiVillageDetected = False
        self.checks_done = 0
        self.pid = pid

        # 获取玩家当前位置作为搜索起点
        pos = CF.CreatePos(pid).GetPos()
        x, y, z = serverApi.GetIntPos(pos)
        self.dimension = CF.CreateDimension(pid).GetEntityDimensionId()
        self.start_pos = (x, y, z)
        self.startY = y

        self.checkQueue.append((x, y, z))
        self.phase = 1

    def _SpawnHelperAt(self, pos):
        # 在指定位置生成辅助实体进行村庄检测
        if self.multiVillageDetected or not self.Searching:
            return
        if self.checks_done >= self.max_checks:
            CF.CreateGame(LID).SetTipMessage(serverApi.GenerateColor("RED") + "达到搜索上限，退出搜索")
            print("达到搜索上限，退出搜索")
            self._OutputResult()
            return
        x, y, z = pos
        if abs(y - self.startY) > self.max_y_delta:
            return
        posStr = self.PosToStr(x, y, z)
        if posStr in self.visited:
            return
        self.visited.add(posStr)
        eid = self.CreateEngineEntityByTypeStr(
            "village_view:helper",
            (x + 0.5, y, z + 0.5),
            (0, 0),
            self.dimension
        )
        self.helper_entities.append(eid)
        self.eid_to_spawnpos[eid] = posStr
        self.checks_done += 1

    @Listen("EntityDefinitionsEventServerEvent")
    def EntityDefinitionsEventServerEvent(self, args):
        # 辅助实体检测结果事件监听
        eid = args.get("entityId")
        if not eid:
            return
        if CF.CreateEngineType(eid).GetEngineTypeStr() != "village_view:helper":
            return

        pos = CF.CreatePos(eid).GetPos()
        x, y, z = serverApi.GetIntPos(pos)
        posStr = self.PosToStr(x, y, z)
        eventName = args.get("eventName", "")

        if self.phase == 1:
            # 第一阶段，步长为3的扫描
            if eventName == "xiaobo:in_village":
                self.village_blocks.add(posStr)
                for new_pos in self.GetAdjacentPositionsStep(x, y, z, 3):
                    if self.PosToStr(*new_pos) not in self.visited:
                        self.checkQueue.append(new_pos)
        elif self.phase == 2:
            # 第二阶段，边界细化
            if eventName == "xiaobo:in_village":
                self.village_blocks.add(posStr)

        # 销毁辅助实体
        self.DestroyEntity(eid)
        if eid in self.helper_entities:
            self.helper_entities.remove(eid)
        if eid in self.eid_to_spawnpos:
            del self.eid_to_spawnpos[eid]

    def _start_refine(self):
        # 开始边界细化阶段
        if not self.village_blocks:
            print("⚠ 第一阶段没有检测到村庄方块，跳过细化阶段。")
            self._OutputResult()
            return
        xs, ys, zs = [], [], []
        for posStr in self.village_blocks:
            x, y, z = self.StrToPos(posStr)
            xs.append(x)
            ys.append(y)
            zs.append(z)
        self.bounds = [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)]
        self.phase = 2
        min_x, max_x, min_y, max_y, min_z, max_z = self.bounds
        print("⚠ 第一阶段检测到村庄方块，开始细化阶段")
        print(self.bounds)
        # 六面检测，补充边界
        for i in range(1,4):
            if self.PosToStr(min_x-i,min_y,min_z) not in self.visited:
                self.checkQueue.append((min_x-i,min_y,min_z))
            if self.PosToStr(min_x,min_y-i,min_z) not in self.visited:
                self.checkQueue.append((min_x,min_y-i,min_z))
            if self.PosToStr(min_x,min_y,min_z-i) not in self.visited:
                self.checkQueue.append((min_x,min_y,min_z-i))
            if self.PosToStr(max_x,max_y,max_z-i) not in self.visited:
                self.checkQueue.append((max_x,max_y,max_z+i))
            if self.PosToStr(max_x,max_y-i,max_z) not in self.visited:
                self.checkQueue.append((max_x,max_y+i,max_z))
            if self.PosToStr(max_x-i,max_y,max_z) not in self.visited:
                self.checkQueue.append((max_x+i,max_y,max_z))

    def _OutputResult(self):
        # 输出村庄边界结果
        for eid in list(self.helper_entities):
            self.DestroyEntity(eid)
        self.helper_entities = []
        self.eid_to_spawnpos = {}
        self.Searching = False
        if not self.village_blocks:
            CF.CreateMsg(self.pid).NotifyOneMessage(self.pid, "搜索失败：当前玩家坐标不在村庄内", "§4")
            print("未找到村庄块")
            return
        xs, ys, zs = [], [], []
        for posStr in self.village_blocks:
            x, y, z = self.StrToPos(posStr)
            xs.append(x)
            ys.append(y)
            zs.append(z)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        CF.CreateGame(LID).SetTipMessage(serverApi.GenerateColor("GREEN") + "搜索结束")
        msg = """村庄边界如下：
        X: {} ~ {}
        Y: {} ~ {}
        Z: {} ~ {}""".format(min_x, max_x, min_y, max_y, min_z, max_z)
        CF.CreateGame(LID).SetNotifyMsg(msg, serverApi.GenerateColor('RED'))
        msg = """铁傀儡刷新边界如下：
        X: {} ~ {}
        Y: {} ~ {}
        Z: {} ~ {}""".format((min_x + max_x) / 2 -8, (min_x + max_x)/ 2 +8,
                              ( min_y + max_y )/ 2-6,  ( min_y + max_y )/ 2+6, 
                              ( min_z + max_z) / 2-8,( min_z + max_z) / 2+8)
        CF.CreateGame(LID).SetNotifyMsg(msg, serverApi.GenerateColor('BLUE'))
        msg = """村庄中心坐标:({},{},{})""".format((min_x + max_x) / 2,( min_y + max_y )/ 2,( min_z + max_z) / 2)
        CF.CreateGame(LID).SetNotifyMsg(msg, serverApi.GenerateColor('YELLOW'))
        msg = "请注意：模组目前不支持多村融合搜索,作者正在技术攻破中..."
        CF.CreateGame(LID).SetNotifyMsg(msg, serverApi.GenerateColor('WHITE'))
        msg = "如果需要关闭渲染边框请输入“关闭渲染”"
        CF.CreateGame(LID).SetNotifyMsg(msg, serverApi.GenerateColor('WHITE'))
        print("✅ 村庄边界如下：")
        print("X: {} ~ {}".format(min_x, max_x))
        print("Y: {} ~ {}".format(min_y, max_y))
        print("Z: {} ~ {}".format(min_z, max_z))
        print(self.isAllPlayer)
        # 渲染边界到客户端
        if not self.isAllPlayer:
            self.CallClient(self.pid, "RenderVillage", {
                "min_x": min_x, "max_x": max_x,
                "min_y": min_y, "max_y": max_y,
                "min_z": min_z, "max_z": max_z
            })
        else:
            self.BroadcastToAllClient("RenderVillage", {
                "min_x": min_x, "max_x": max_x,
                "min_y": min_y, "max_y": max_y,
                "min_z": min_z, "max_z": max_z})

    def Update(self):
        # 每tick更新，批量生成辅助实体加快检测
        if not self.Searching:
            return
        max_spawn_per_tick = 200
        spawn_count = 0
        if self.checkQueue:
            while self.checkQueue and spawn_count < max_spawn_per_tick:
                next_pos = self.checkQueue.pop(0)
                self._SpawnHelperAt(next_pos)
                spawn_count += 1
        elif not self.helper_entities:
            if self.phase == 1:
                self._start_refine()
            else:
                self._OutputResult()
        
    def Destroy(self):
        # 销毁时的清理操作（预留）
        pass