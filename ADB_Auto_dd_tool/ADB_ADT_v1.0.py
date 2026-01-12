import subprocess
import os
from tqdm import tqdm

# --- 配置区域 ---
OUTPUT_DIR = input("备份到:")  # 电脑存放分区的目录
NOT_MAGISK_SUDO = input('是否启用su -c\n(这个需要magisk，或者您也可以关闭这个并且使用其他su，直接回车默认开启，输入任意字符回车关闭。)')
if NOT_MAGISK_SUDO:
    ADDITHON_COMMAND = input('自定义su指令：')
    if ADDITHON_COMMAND:
        ADDITHON_COMMAND = ADDITHON_COMMAND + ' '
else:
    ADDITHON_COMMAND = 'su -c '
BLOCK_SIZE = 4 * 1024 * 1024  # 4MB

# --- 函数：自动获取 /dev/block/by-name 下的分区表字典 ---
def get_partitions():
    print('开始解析...')
    partitions = {}
    try:
        result = subprocess.check_output(
            "adb shell ls -l /dev/block/by-name", shell=True, text=True
        )
        print('解析成功!')
    except subprocess.CalledProcessError:
        print("[!] 无法获取分区信息，请确认设备已连接并启用adb")
        return partitions

    for line in result.strip().splitlines():
        parts = line.split()
        if "->" in parts:
            # 例子：lrwxrwxrwx 1 root root 21 2023-09-01 12:00 boot -> /dev/block/mmcblk0p3
            name = parts[-3]  # 符号链接名（boot）
            path = parts[-1]  # 真正路径（/dev/block/mmcblk0p3）
            partitions[name] = path
    return partitions

'''# --- 基础分区（非 by-name 的特殊设备节点） ---
BASE_PARTITIONS = {
    'mmcblk0': '/dev/block/mmcblk0',
    'mmcblk0boot0': '/dev/block/mmcblk0boot0',
    'mmcblk0boot1': '/dev/block/mmcblk0boot1',
    'mmcblk0rpmb': '/dev/block/mmcblk0rpmb'
}

# --- 合并字典：优先用 by-name，额外加上 boot0/boot1/rpmb ---
PARTITIONS = {**get_partitions(), **BASE_PARTITIONS}'''
PARTITIONS = get_partitions()

# --- 确保输出目录存在 ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 函数：通过管道 dd 分区 ---
def dump_partition(name, device_path):
    output_file = os.path.join(OUTPUT_DIR, f"{name}.img")
    print(f"[+] 开始导出 {name}: {output_file}")

    adb_cmd = f"adb shell {ADDITHON_COMMAND}dd if={device_path} bs={BLOCK_SIZE}"
    print(f'执行:{adb_cmd}')
    with subprocess.Popen(adb_cmd, shell=True, stdout=subprocess.PIPE) as proc:
        with open(output_file, "wb") as f_out:
            pbar = tqdm(unit="B", unit_scale=True, desc=name)
            while True:
                chunk = proc.stdout.read(BLOCK_SIZE)
                if not chunk:
                    break
                f_out.write(chunk)
                pbar.update(len(chunk))
            pbar.close()
    print(f"[+] {name} 导出完成!")

# --- 遍历所有分区 ---
for name, path in PARTITIONS.items():
    try:
        dump_partition(name, path)
    except KeyboardInterrupt:
        print("\n[!] 中断导出")
        break
    except Exception as e:
        print(f"[!] {name} 导出失败: {e}")
