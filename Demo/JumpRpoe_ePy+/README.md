# epy plus 使用內建 Acc sensor 檢測運動動作 搭配 App
## 狀態顯示
紅LED -- 藍芽未連接
綠LED -- 藍芽已連接
黃LED -- Python 程式運作中

開機啟動 --
前五秒 自我校正 偵測 Z 軸 (正反面) ,伴隨五次響聲

## BLE command list --
    - app --> device  : "get_cycle\n"  (開始遊戲)
    - device --> app : "send,#num\n"  (送#num次數到 App)
    - app --> device  :"set end\n" (結束遊戲)
    - app --> device : "disc\n" (中斷藍芽連接)

    

