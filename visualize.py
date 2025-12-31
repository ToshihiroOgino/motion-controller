import matplotlib.pyplot as plt
import numpy as np
import sys

input_file_path: str = sys.argv[1] if len(sys.argv) > 1 else ""

if input_file_path == "":
    print(f"Usage: python {sys.argv[0]} <input_file_path>")
    sys.exit(1)

data = np.loadtxt(input_file_path, delimiter=",", dtype=int, skiprows=1)

# 列の抽出
timestamps = data[:, 0]  # マイクロ秒（記録開始からのオフセット）
states = data[:, 1]  # 0 or 1

# --- 波形データの作成 ---
# タイムスタンプで状態が変わるので、各状態が続く期間を計算
# 波形を描くために、状態変化点での座標を作成
plot_x = []
plot_y = []

for i in range(len(data)):
    if i == 0:
        # 最初の点は開始時刻(0)から
        plot_x.append(0)
        plot_y.append(states[i])
    
    # 状態変化点
    plot_x.append(timestamps[i])
    plot_y.append(states[i-1] if i > 0 else states[i])
    plot_x.append(timestamps[i])
    plot_y.append(states[i])

# 最後の状態を終了まで表示
if len(timestamps) > 0:
    plot_x.append(timestamps[-1])
    plot_y.append(states[-1])

plot_x = np.array(plot_x)
plot_y = np.array(plot_y)

# --- プロット ---
plt.figure(figsize=(12, 4))
plt.plot(plot_x, plot_y, linewidth=1.5)

# 見やすくするための設定
plt.title("IR Signal")
plt.xlabel("Time (μs)")
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
