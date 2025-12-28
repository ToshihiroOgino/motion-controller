import matplotlib.pyplot as plt
import numpy as np
import sys

input_file_path: str = sys.argv[1] if len(sys.argv) > 1 else ""

if input_file_path == "":
    print(f"Usage: python {sys.argv[0]} <input_file_path>")
    sys.exit(1)

data = np.loadtxt(input_file_path, delimiter=",", dtype=int, skiprows=1)


# 列の抽出
states = data[:, 0]  # 0 or 1
durations = data[:, 1]  # us

# --- 波形データの作成 ---
# 累積時間を計算して、各区間の開始・終了時刻を作成
time_cumsum = np.cumsum(durations)
time_starts = np.insert(time_cumsum[:-1], 0, 0)
time_ends = time_cumsum

# 矩形波を描くために、各区間の「開始点」と「終了点」の座標を交互に並べる
# X軸: [Start1, End1, Start2, End2, ...]
plot_x = np.column_stack((time_starts, time_ends)).flatten()
# Y軸: [State1, State1, State2, State2, ...]
plot_y = np.column_stack((states, states)).flatten()

# --- プロット ---
plt.figure(figsize=(12, 4))
plt.plot(plot_x, plot_y, linewidth=1.5)

# 見やすくするための設定
plt.title("IR Signal")
plt.xlabel("Time (ms)")
plt.ylabel("State")
plt.yticks([0, 1], ["OFF (0)", "ON (1)"])
plt.grid(True, linestyle="--", alpha=0.7)
plt.ylim(-0.1, 1.1)

# 保存と表示
output_filename = input_file_path.replace(".csv", ".png")
plt.savefig(output_filename)
print(f"画像を保存しました: {output_filename}")

try:
    plt.show()
except:
    pass
