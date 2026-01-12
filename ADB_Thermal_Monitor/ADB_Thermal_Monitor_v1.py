import threading
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
#import psutil
import subprocess
import time

speed = 2
size = 11
window_size = [300,60]#以列表形式存储窗口大小数据
#UI_number = 1

# ---- 保留你原来的 CPU/RAM 初始化风格（不过 CPU 部分将复用为 thermal 显示） ----
#cpulist = psutil.cpu_percent(interval=1, percpu=True)
#core_num = len(cpulist)#获取核心数量

def main():
    global cpu_text
    global num
    #global UI_number
    temp_monitor_window=tk.Tk()
    #设定界面相关参数
    temp_monitor_window.title('ADB Health Monitor')
    temp_monitor_window.columnconfigure(0,minsize=50)
    temp_monitor_window.configure(bg='#1e1e1e')
    temp_monitor_window.geometry(f'{window_size[0]}x60+50+30')
    #temp_monitor_window.resizable(0,0)
    temp_monitor_window.overrideredirect(True)
    temp_monitor_window.attributes("-topmost", True)

    # 字符变量初始化区（保留原名）
    cpu_text = tk.StringVar()
    cpu_text.set('CPU:--.-%')   # 这个文本我们可以不再频繁更新（保留以防兼容）
    ram_usage = tk.StringVar()
    ram_usage.set('RAM: --.-%')

    # ======================== 将“每核显示”替换为“thermal_zone 显示” =========================
    # 设计目标：最小改动 UI，复用 create_widgets / updata_labels 的结构
    def _adb_run(cmd_list, timeout=3):
        """简洁的 adb wrapper，返回 (stdout, stderr) 元组；捕获常见异常。"""
        try:
            p = subprocess.run(cmd_list, capture_output=True, text=True, timeout=timeout)
            return p.stdout or "", p.stderr or ""
        except subprocess.TimeoutExpired:
            return "", "adb timeout"
        except FileNotFoundError:
            return "", "adb not found"
        except Exception as e:
            return "", str(e)

    def fetch_android_cpu_usage():
        """
        通过读取 /proc/stat 两次计算 Android 设备总体 CPU 占用百分比。
        返回 float（0..100）或 None（失败）。
        """
        # 第一次采样
        out1, err1 = _adb_run(['adb', 'shell', 'su', '-c', "cat /proc/stat | head -n 1"], timeout=2)
        if err1:
            return None
        #time.sleep(speed)
        out2, err2 = _adb_run(['adb', 'shell', 'su', '-c', "cat /proc/stat | head -n 1"], timeout=2)
        if err2:
            return None

        def parse_cpu_line(line):
            parts = line.strip().split()
            if len(parts) < 5:
                return None
            # parts[0] == 'cpu'
            vals = [int(x) for x in parts[1:]]
            # idle = idle + iowait (tokens index 3 and 4 after 'cpu')
            idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
            total = sum(vals)
            return idle, total

        p1 = parse_cpu_line(out1)
        p2 = parse_cpu_line(out2)
        if not p1 or not p2:
            return None
        idle1, total1 = p1
        idle2, total2 = p2
        diff_idle = idle2 - idle1
        diff_total = total2 - total1
        if diff_total <= 0:
            return None
        usage = (1.0 - (diff_idle / diff_total)) * 100.0
        return round(max(0.0, min(100.0, usage)), 1)

    def fetch_android_ram_usage():
        """
        读取 Android /proc/meminfo，返回使用百分比或 None。
        使用 MemTotal 与 MemAvailable（若无 Available 则退回于计算方式）。
        """
        out, err = _adb_run(['adb', 'shell', 'su', '-c', "cat /proc/meminfo"], timeout=3)
        if err or not out:
            return None
        total = None
        avail = None
        for line in out.splitlines():
            if line.startswith('MemTotal:'):
                try:
                    total = int(line.split()[1])  # kB
                except:
                    total = None
            elif line.startswith('MemAvailable:'):
                try:
                    avail = int(line.split()[1])  # kB
                except:
                    avail = None
            if total and avail:
                break
        if total is None:
            return None
        if avail is None:
            # 尝试用 MemFree+Buffers+Cached 作为退路
            memfree = buffers = cached = 0
            for line in out.splitlines():
                if line.startswith('MemFree:'):
                    try: memfree = int(line.split()[1])
                    except: pass
                elif line.startswith('Buffers:'):
                    try: buffers = int(line.split()[1])
                    except: pass
                elif line.startswith('Cached:'):
                    try: cached = int(line.split()[1])
                    except: pass
            avail = memfree + buffers + cached
            if not avail:
                return None
        used = total - avail
        pct = used / total * 100.0
        return round(max(0.0, min(100.0, pct)), 1)

    def temp_to_color(temp_c):
        """
        分段渐变颜色映射:
        <=30 蓝青
        30-45 青蓝->绿
        45-60 绿->黄
        60-80 黄->橙
        >=80 红
        """
        if temp_c is None:
            return '#a4a4a4'  # 无数据 -> 灰色

        if temp_c <= 30:
            return '#00ffff'  # 青蓝
        elif temp_c <= 45:
            # 青蓝 (#00ffff) -> 绿 (#00ff00)
            ratio = (temp_c - 30) / 15.0
            r = 0
            g = int(128 * ratio) + 127
            b = int(255 * (1 - ratio))
            return f'#{r:02x}{g:02x}{b:02x}'
        elif temp_c <= 60:
            # 绿 (#00ff00) -> 黄 (#ffff00)
            ratio = (temp_c - 45) / 15.0
            r = int(255 * ratio)
            g = 255
            b = 0
            return f'#{r:02x}{g:02x}{b:02x}'
        elif temp_c <= 75:
            # 黄 (#ffff00) -> 橙 (#ff8000)
            ratio = (temp_c - 60) / 15.0
            r = 255
            g = int(255 - 127 * ratio)
            b = 0
            return f'#{r:02x}{g:02x}{b:02x}'
        else:
            return '#ff0000'  # 红
        
    errrr = False
    def fetch_thermal_info():
        """
        通过 adb 获取 thermal_zone type 与 temp。
        返回列表 [(type_str, temp_float_or_None, err_str_or_None), ...]
        如果 adb/命令失败，返回 [('ERROR', None, '错误信息'), ...]（单行）
        """
        nonlocal errrr
        #global UI_number
        try:
            # run types
            proc_types = subprocess.run(
                ['adb', 'shell', 'su', '-c', 'cat /sys/class/thermal/thermal_zone*/type'],
                capture_output=True, text=True, timeout=3
            )
            proc_temps = subprocess.run(
                ['adb', 'shell', 'su', '-c', 'cat /sys/class/thermal/thermal_zone*/temp'],
                capture_output=True, text=True, timeout=3
            )

            
            # 若命令 stderr 有输出，视为可能的权限/其他错误
            if (proc_types.stderr and proc_types.stderr.strip()) or (proc_temps.stderr and proc_temps.stderr.strip()):
                # 合并 stderr 信息显示
                err_msg = (proc_types.stderr or '') + (proc_temps.stderr or '')
                print(err_msg)
                if 'su: inaccessible or not found' in err_msg or 'su: not found' in err_msg:
                    messagebox.showerror('ADB Health Monitor','错误:SU异常，请检查root权限，安装并刷入Magisk！')
                    return False
                elif 'no devices/emulators found' in err_msg:
                    errrr = True
                    text_1 = tk.Label(temp_monitor_window, foreground='#ffffff', background='#1f1f1f', text='正在等待设备连接...')# 创建一个Label控件，用于显示底部消息栏
                    text_1.place(height=80, width=window_size[0]-20-20,x=20,y=35)
                    temp_monitor_window.update()
                elif 'more than one device/emulator':
                    errrr = True
                    text_1 = tk.Label(temp_monitor_window, foreground='#ffffff', background='#1f1f1f', text='多于一个设备，请选择')# 创建一个Label控件，用于显示底部消息栏
                    text_1.place(height=80, width=window_size[0]-20-20,x=20,y=35)
                    temp_monitor_window.update()
            elif errrr:
                #UI_number = 0
                time.sleep(1)
                temp_monitor_window.after(0, temp_monitor_window.destroy)
                #text_1.destroy()
                errrr = False
                print(errrr)
            #err_msg = err_msg.strip().splitlines()[0] if err_msg.strip() else "Unknown adb error"
                return [('ERROR', None, err_msg) in err_msg]

            types = [t.strip() for t in proc_types.stdout.strip().splitlines() if t.strip()!='']
            temps_raw = [t.strip() for t in proc_temps.stdout.strip().splitlines() if t.strip()!='']

            # 如果 types 无法读取但 temps 有值，还是要尽量显示索引
            n = max(len(types), len(temps_raw))
            result = []
            for i in range(n):
                tname = types[i] if i < len(types) else f'zone{i}'
                temp_val = None
                if i < len(temps_raw):
                    raw = temps_raw[i]
                    try:
                        val = int(raw)
                        # 若看起来像 milli°C（大于 1000），转为 °C
                        if abs(val) > 1000:
                            temp_val = round(val/1000.0, 1)
                        else:
                            temp_val = round(float(val), 1)
                    except Exception:
                        # 有些设备返回非数值（比如空、N/A），标为 None
                        temp_val = None
                result.append((tname, temp_val, None))
            return result

        except subprocess.TimeoutExpired:
            return [('ERROR', None, 'adb timeout')]
        except FileNotFoundError:
            return [('ERROR', None, 'adb not found')]
        except Exception as e:
            return [('ERROR', None, str(e))]

    # create_widgets: 根据 thermal 数量创建标签（尽量与原布局一致）
    def create_widgets():
        global window_height
        global thermal_count
        global labels
        labels = []

        # 初始上去尝试获取一次信息以决定 label 数量
        info = fetch_thermal_info()
        # 如果返回的是错误单行，显示一行错误
        if len(info) == 1 and info[0][0] == 'ERROR':
            thermal_count = 1
            display_list = [('ERROR', None, info[0][2])]
        else:
            thermal_count = len(info)
            display_list = info

        widget_width = 120
        widget_height = 15
        left_margin = 20
        right_margin = 20
        top_margin = 65
        bottom_margin = 30
        vertical_spacing = 5

        for i, (name, temp, err) in enumerate(display_list):
            if err:
                text = f"{name}: {err}"
            else:
                text = f"{name}: {temp if temp is not None else '--'}°C"
            label = tk.Label(temp_monitor_window, text=text, width=widget_width, height=widget_height,
                             font=('微软雅黑','8'), background='#1e1e1e', fg='#a4a4a4')
            labels.append(label)

        row = 0
        col = 0
        for i in range(len(labels)):
            labels[i].place(x=left_margin + col * (widget_width + 0),
                            y=top_margin + row * (widget_height + vertical_spacing),
                            width=widget_width, height=widget_height)
            col += 1
            if col == 2:
                col = 0
                row += 1

        window_height = top_margin + (row+1) * (widget_height + vertical_spacing) + bottom_margin
        # 避免太短
        if window_height < 120:
            window_height = 120
        temp_monitor_window.geometry(f"{window_size[0]}x{window_height}")

    # updata_labels: 更新已有 labels 的文本（每次仅改 text，不销毁标签，避免闪烁）
    def updata_labels():
        info = fetch_thermal_info()
        # 如果之前创建的 labels 数量与现在不匹配，重建（这是少量重写，必要）
        if not labels:
            create_widgets()
        # 错误单行
        if len(info) == 1 and info[0][0] == 'ERROR':
            # 若 labels 数 !=1，重建
            if len(labels) != 1:
                create_widgets()
            labels[0].config(text=f"ERROR: {info[0][2]}")
        else:
            # 如果数量变化，重建
            if len(info) != len(labels):
                create_widgets()
                # 尝试再次获取 to sync
                info = fetch_thermal_info()

            for i, item in enumerate(info):
                name, temp, err = item
                if err:
                    text = f"{name}: {err}"
                else:
                    text = f"{name}: {temp if temp is not None else '--'}°C"
                # 防越界
                if i < len(labels):
                    #labels[i].config(text=text)
                    # 如果是 ERROR 行，用醒目红色；否则按温度映射到颜色
                    if text.startswith("ERROR"):
                        labels[i].config(text=text, fg='#ff5555')
                    else:
                        # 解析出温度（示例： 'soc_thermal: 79.0°C' 或 'soc_thermal: --°C'）
                        # info 里已经有 temp 值，理想情况下直接使用 info；如果要从 text 解析也行：
                        try:
                            # 假设 info 与 labels 同步，优先使用 info
                            _, temp_val, _ = info[i]
                        except Exception:
                            temp_val = None
                        color = temp_to_color(temp_val)
                        labels[i].config(text=text, fg=color)

        # 使用 speed 作为刷新间隔（秒）
        temp_monitor_window.after(int(max(0.2, speed)*1000), updata_labels)

    # ============= 保留你原来的自制窗口管理器与菜单等 =============
    def Exit():
        temp_monitor_window.destroy()

    def set_speed(the_speed):
        global speed
        speed = the_speed

    def set_size(the_size):
        global size
        size = the_size
        try:
            cpu_OU.destroy()
        except Exception:
            pass
        cpu(size)

    def MouseDown(event):
        global mousX, mousY
        mousX=event.x
        mousY=event.y

    set_button = tk.Menubutton(temp_monitor_window, activeforeground="#f9f9f9",foreground='#f9f9f9',
                                    activebackground="#b6b6b6",background='#2d2d2d',
                                    text="⋮", font=('微软雅黑',16),borderwidth=0, direction='below')
    set_button.place(relheight=1, width=20,relx=0,rely=0)
    menu = tk.Menu(set_button, tearoff=False, borderwidth=0)
    set_button.config(menu=menu)
    speed_menu = tk.Menu(menu, tearoff=False)
    size_menu = tk.Menu(menu, tearoff=False)
    menu.add_cascade(label="更新速度", menu=speed_menu)
    menu.add_cascade(label="字号", menu=size_menu)
    speed_menu.add_command(label="1/2s  极高(高占用)", command=lambda: set_speed(0.5))
    speed_menu.add_command(label="1s    高", command=lambda: set_speed(1))
    speed_menu.add_command(label="2s    中（默认）", command=lambda: set_speed(2))
    speed_menu.add_command(label="3s    低", command=lambda: set_speed(3))
    speed_menu.add_command(label="4s    极低", command=lambda: set_speed(4))
    size_menu.add_command(label="8", command=lambda: set_size(8))
    size_menu.add_command(label="9", command=lambda: set_size(9))
    size_menu.add_command(label="10", command=lambda: set_size(10))
    size_menu.add_command(label="11（默认）", command=lambda: set_size(11))
    size_menu.add_command(label="12", command=lambda: set_size(12))
    size_menu.add_command(label="13", command=lambda: set_size(13))
    size_menu.add_command(label="14", command=lambda: set_size(14))

    # 右栏 / 退出键 / 标题保持原样
    rightLabel=tk.Label(temp_monitor_window,background='#2d2d2d')
    rightLabel.place(relheight=1, width=20,x=window_size[0]-20,y=0)
    Exitbuttonfont = tkFont.Font(size=12, weight=tkFont.BOLD)
    Exitbutton=tk.Button(temp_monitor_window, foreground='#f9f9f9',activebackground="red",
                        background='#2d2d2d',command=Exit,text='×',font=Exitbuttonfont,borderwidth=0)
    Exitbutton.place(relheight=1, width=20,x=window_size[0]-20,y=0)
    Exitbutton.bind('<Enter>', lambda event: Exitbutton.config(bg='#e81123'))
    Exitbutton.bind('<Leave>', lambda event: Exitbutton.config(bg='#2d2d2d'))

    def MouseMove_ADB_HM_title(event):
        w=ADB_HM_TITLE.winfo_x()
        h=ADB_HM_TITLE.winfo_y()
        temp_monitor_window.geometry(f'+{event.x_root - mousX-w}+{event.y_root - mousY-h}')

    ADB_HM_TITLE = tk.Label(temp_monitor_window, text='ADB Health Monitor', background='#323232', fg='#a4a4a4', font=('黑体','16'))
    ADB_HM_TITLE.place(x=20, y=0, height=35, width=window_size[0]-20-20)
    ADB_HM_TITLE.bind("<B1-Motion>",MouseMove_ADB_HM_title)
    ADB_HM_TITLE.bind("<Button-1>",MouseDown)

    # ============ RAM 更新（保留你原来的函数，线程方式） ============
    def updata_RAM(UI_number):
        """将 ram_usage 显示为 Android 设备的 RAM 使用率（例如 'RAM: 42.1%'）"""
        try:
            android_ram = fetch_android_ram_usage()
            #print(UI_number,num)
            if android_ram is None and UI_number == num:
                ram_usage.set('RAM: --.-%')
            elif UI_number == num:
                ram_usage.set(f'RAM: {android_ram:.1f}%')
        except Exception as e:
            if UI_number == num:
                ram_usage.set('RAM: --.-%')
            # 可选：
            print(e)

    def updata_cpu_usage(UI_number):
        """将 cpu_text 显示为 Android 设备的总体 CPU 使用率（例如 'CPU: 12.3%'）"""
        try:
            android_cpu = fetch_android_cpu_usage()
            #print(UI_number,num)
            if android_cpu is None and UI_number == num:
                cpu_text.set('CPU: --.-%')
            elif UI_number == num:
                cpu_text.set('CPU:' + str(android_cpu).rjust(5) + '%')
        except Exception as e:
            if UI_number == num:
                cpu_text.set('CPU: --.-%')
            # 可选：打印错误用于调试
            print("fetch android cpu error:", e)

    def updata():
        # 线程只负责 RAM 与原 CPU（以免破坏你的原始逻辑）
        print('updata',num)
        UI_number = num
        print
        while UI_number == num:
            updata_cpu_usage(UI_number)
            updata_RAM(UI_number)
            time.sleep(speed)

    updata_thread = threading.Thread(target=updata)
    updata_thread.daemon = True
    updata_thread.start()

    # cpu 显示区（保留）
    def cpu(sz):
        global cpu_OU
        cpu_OU = tk.Label(temp_monitor_window, textvariable=cpu_text, background='#1e1e1e', fg='#a4a4a4', font=('微软雅黑',sz))
        cpu_OU.place(x=20, y=35, height=30, width=window_size[0]-20-20)

    cpu(11)

    # 创建 thermal widgets（替代原 create_widgets）
    create_widgets()

    # 启动周期性更新 thermal labels（使用 after，和你原本的 updata_labels 名称一致）
    temp_monitor_window.after(1000, updata_labels)

    # RAM 显示（保留）
    RAM_label = tk.Label(temp_monitor_window, textvariable=ram_usage, background='#1e1e1e', fg='#a4a4a4', font=('微软雅黑','11'))
    RAM_label.place(x=20, y=window_height - 30, height=30, width=window_size[0]-20-20)

    
    temp_monitor_window.mainloop()
    return True


status = True
num = 0
while status:
    num += 1
    print(num)
    status = main()
    if status:
        print('rebuild UI')