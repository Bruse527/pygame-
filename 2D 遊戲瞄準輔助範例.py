import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator

# 玩家輸入角度 (x) 與目標方向 (y)
# 假設有三個目標，分別在 30°, 90°, 150°
player_input = np.array([0, 30, 90, 150, 180])
target_direction = np.array([0, 30, 90, 150, 180])

# 使用單調三次插值 (PCHIP) 確保函數平滑且單調
interp = PchipInterpolator(player_input, target_direction)

# 模擬輸入範圍
x_vals = np.linspace(0, 180, 500)
y_vals = interp(x_vals)

# 引入「虛擬目標大小」：增加目標附近的權重
def aim_assist(x, targets, radius=10):
    """
    x: 玩家輸入角度
    targets: 目標角度列表
    radius: 虛擬目標大小 (影響瞄準吸附範圍)
    """
    for t in targets:
        if abs(x - t) < radius:
            return t  # 自動吸附到目標
    return interp(x)

# 測試瞄準輔助
test_inputs = [25, 85, 140]
for inp in test_inputs:
    print(f"玩家輸入 {inp}° → 瞄準方向 {aim_assist(inp, [30, 90, 150])}°")

# 畫圖展示
plt.plot(x_vals, y_vals, label="平滑瞄準曲線")
plt.scatter([30, 90, 150], [30, 90, 150], color="red", label="目標")
plt.xlabel("玩家輸入角度")
plt.ylabel("角色瞄準方向")
plt.legend()
plt.title("2D 遊戲瞄準輔助示範")
plt.show()