import os, math, threading
from concurrent.futures import ProcessPoolExecutor, as_completed
import cv2, numpy as np, pandas as pd
from PIL import Image
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def open_tiff(path):
    img = np.array(Image.open(path))
    if img.ndim == 2: return img.astype(np.float32)
    return np.dot(img[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.float32)

def split_tiles(img, k):
    h, w = img.shape[:2]
    tiles = []
    idx = 1
    for i in range(k): 
        y0 = (i * h) // k
        y1 = ((i + 1) * h) // k if i < k - 1 else h
        for j in range(k): 
            x0 = (j * w) // k
            x1 = ((j + 1) * w) // k if j < k - 1 else w
            tile = img[y0:y1, x0:x1].copy()
            tiles.append((idx, tile, x0, y0))
            idx += 1
    return tiles

def detect_objects(tile_tuple, threshold_sigma=3.0, min_area=5):
    idx, tile, x0, y0 = tile_tuple
    if tile.size == 0:
        return []

    mu = float(np.mean(tile))
    sigma = float(np.std(tile))
    thresh = mu + threshold_sigma * sigma

    bw = (tile > thresh).astype(np.uint8) * 255
    bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

    contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    objs = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue

        M = cv2.moments(cnt)
        if M.get('m00', 0) == 0:
            continue
        cx = M['m10'] / M['m00']
        cy = M['m01'] / M['m00']

        mask = np.zeros_like(tile, dtype=np.uint8)
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        pixels = tile[mask > 0]
        if pixels.size == 0:
            continue
        brightness_sum = float(np.sum(pixels))
        max_pixel = float(np.max(pixels))

        if area < 20 and brightness_sum > 1000:
            obj_type = 'star'
            color = (0, 255, 255)#желтый
        elif area < 50:
            obj_type = 'planet'
            color = (255, 0, 0)#синий
        elif area < 300:
            obj_type = 'comet'
            color = (0, 255, 0)#зеленый
        else:
            obj_type = 'galaxy'
            color = (0, 0, 255)#красный

        objs.append({
            'tile_index': int(idx),
            'type': obj_type,
            'area': float(area),
            'brightness_sum': brightness_sum,
            'max_pixel': max_pixel,
            'centroid_y': float(y0 + cy),
            'centroid_x': float(x0 + cx),
            'color': color,
        })
    return objs

def draw_objects(full_img, objects):
    img_uint8 = np.clip(full_img, 0, 255).astype(np.uint8)
    out = cv2.cvtColor(img_uint8, cv2.COLOR_GRAY2BGR)
    for o in objects:
        x = int(round(o['centroid_x']))
        y = int(round(o['centroid_y']))
        size = int(max(2, math.sqrt(max(1.0, o['area'])))) + 2
        color = tuple(int(c) for c in o.get('color', (255, 255, 255)))
        cv2.rectangle(out, (x - size, y - size), (x + size, y + size), color, 1)
    return out


class AstroApp:
    def __init__(self, root):
        self.root = root
        root.title("Astro Parallel Analyzer")

        frm = ttk.Frame(root, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        self.images_folder = tk.StringVar(value="/Users/ilabublik/Desktop/2sem/system_and_functionalprogramy/2nd_functionprogrammy/images")
        self.output_folder = tk.StringVar(value="/Users/ilabublik/Desktop/2sem/system_and_functionalprogramy/2nd_functionprogrammy/out")
        os.makedirs(self.images_folder.get(), exist_ok=True)
        os.makedirs(self.output_folder.get(), exist_ok=True)

        ttk.Label(frm, text="Папка с TIFF:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.images_folder, width=60).grid(row=0, column=1, sticky="w")
        ttk.Button(frm, text="Выбрать", command=self.choose_images_folder).grid(row=0, column=2)

        ttk.Label(frm, text="Папка для результата:").grid(row=1, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.output_folder, width=60).grid(row=1, column=1, sticky="w")
        ttk.Button(frm, text="Выбрать", command=self.choose_output_folder).grid(row=1, column=2)

        ttk.Label(frm, text="Разрезов (k):").grid(row=2, column=0, sticky="w")
        self.k_var = tk.IntVar(value=5)
        ttk.Entry(frm, textvariable=self.k_var, width=6).grid(row=2, column=1, sticky="w")

        ttk.Label(frm, text="Потоки:").grid(row=2, column=2, sticky="w")
        self.workers_var = tk.IntVar(value=max(1, os.cpu_count() - 1))
        ttk.Entry(frm, textvariable=self.workers_var, width=6).grid(row=2, column=3, sticky="w")

        self.start_btn = ttk.Button(frm, text="Старт", command=self.start)
        self.start_btn.grid(row=3, column=0, pady=8)

        self.progress = ttk.Progressbar(frm, length=360, mode='determinate')
        self.progress.grid(row=3, column=1, columnspan=2, sticky="w")

        self.status_var = tk.StringVar(value="Ожидание")
        ttk.Label(frm, textvariable=self.status_var).grid(row=4, column=0, columnspan=4, sticky="w")

        cols = ('tile_index', 'type', 'area', 'brightness_sum', 'centroid_y', 'centroid_x')
        self.tree = ttk.Treeview(frm, columns=cols, show='headings', height=12)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, anchor='center')
        self.tree.grid(row=5, column=0, columnspan=4, sticky='nsew', pady=8)

        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)
        frm.rowconfigure(5, weight=1)

    def choose_images_folder(self):
        folder = filedialog.askdirectory(initialdir=self.images_folder.get())
        if folder:
            self.images_folder.set(folder)

    def choose_output_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_folder.get())
        if folder:
            self.output_folder.set(folder)

    def start(self):
        folder = self.images_folder.get()
        tiffs = [f for f in os.listdir(folder) if f.lower().endswith(('.tif', '.tiff'))]
        if not tiffs:
            messagebox.showerror("Ошибка", f"В папке {folder} нет TIFF файлов")
            return
        file_path = os.path.join(folder, tiffs[0])

        try:
            k = int(self.k_var.get())
            if k <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Ошибка", "Введите положительное целое k")
            return

        workers = int(self.workers_var.get())
        outdir = self.output_folder.get()
        os.makedirs(outdir, exist_ok=True)

        self.start_btn.config(state='disabled')
        threading.Thread(target=self.run_pipeline, args=(file_path, k, workers, outdir), daemon=True).start()

    def _set_status(self, text):
        self.root.after(0, self.status_var.set, text)

    def _set_progress(self, value, maximum=None):
        def f():
            if maximum is not None:
                self.progress['maximum'] = maximum
            self.progress['value'] = value
        self.root.after(0, f)

    def run_pipeline(self, file_path, k, workers, outdir):
        try:
            self._set_status("Открытие TIFF...")
            img = open_tiff(file_path)
            h, w = img.shape[:2]
            self._set_status(f"Изображение: {w}x{h}")

            tiles = split_tiles(img, k)
            ntiles = len(tiles)
            self._set_progress(0, maximum=ntiles)

            results = []
            self._set_status("Параллельная обработка...")
            with ProcessPoolExecutor(max_workers=workers) as exe:
                futures = [exe.submit(detect_objects, t) for t in tiles]
                done = 0
                for fut in as_completed(futures):
                    done += 1
                    self._set_progress(done)
                    try:
                        tile_objs = fut.result()
                        if tile_objs:
                            results.extend(tile_objs)
                    except Exception as e:
                        print("Worker error:", e)

            if results:
                df = pd.DataFrame(results)
                if 'color' in df.columns:
                    df_csv = df.drop(columns=['color'])
                else:
                    df_csv = df
                csv_path = os.path.join(outdir, "astro_objects_summary.csv")
                df_csv.to_csv(csv_path, index=False)

                vis = draw_objects(img, results)
                vis_path = os.path.join(outdir, "astro_objects_visualization.png")
                cv2.imwrite(vis_path, vis)

                self._populate_tree(df_csv)
                self._set_status(f"Готово. Найдено объектов: {len(df)}. CSV: {csv_path}")
            else:
                self._set_status("Объекты не найдены.")
        except Exception as e:
            self._set_status("Ошибка: " + str(e))
            messagebox.showerror("Ошибка", str(e))
        finally:
            self.start_btn.config(state='normal')
            self._set_progress(0)

    def _populate_tree(self, df):
        def f():
            for r in self.tree.get_children():
                self.tree.delete(r)
            for _, row in df.head(500).iterrows():
                vals = (
                    int(row.get('tile_index', 0)),
                    row.get('type', ''),
                    float(row.get('area', 0.0)),
                    round(float(row.get('brightness_sum', 0.0)), 2),
                    round(float(row.get('centroid_y', 0.0)), 2),
                    round(float(row.get('centroid_x', 0.0)), 2),
                )
                self.tree.insert('', 'end', values=vals)
        self.root.after(0, f)

if __name__ == '__main__':
    root = tk.Tk()
    app = AstroApp(root)
    root.mainloop()
