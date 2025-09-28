import os, cv2, requests, numpy as np, pandas as pd
from io import BytesIO
from PIL import Image
from skimage.measure import label, regionprops
from concurrent.futures import ThreadPoolExecutor

#API_KEY = 'DEMO_KEY'  # Замени на свой ключ с https://api.nasa.gov/
API_KEY ='5hGoBN8FcdHs1dd48uvoU6o95YxaUOfZiCFtLisS'
BASE_DIR = '/Users/ilabublik/Desktop/2sem/system_and_functionalprogramy/2nd_functionprogrammy'
IMG_DIR = os.path.join(BASE_DIR, 'images')
OUT_DIR = os.path.join(BASE_DIR, 'out')
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

def download_images(count=10):
    url = f'https://api.nasa.gov/planetary/apod?api_key={API_KEY}&count={count}'
    data = requests.get(url).json()

    if isinstance(data, dict):  # если пришёл один объект
        data = [data]

    paths = []
    for i, d in enumerate(data):
        if d.get('media_type') == 'image' and d['url'].endswith('.jpg'):
            path = os.path.join(IMG_DIR, f'nasa_{i}.png')
            Image.open(BytesIO(requests.get(d["url"]).content)).save(path)
            paths.append(path)
            print(f"Загружено: {path}")
    return paths

def analyze(path):
    gray = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    color = cv2.imread(path)
    if gray is None:
        return []

    _, bin_img = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    stats = []
    for r in regionprops(label(bin_img)):
        b = np.sum(gray[r.coords[:,0], r.coords[:,1]])
        if b < 5:
            continue
        cv2.rectangle(color, (r.bbox[1], r.bbox[0]), (r.bbox[3], r.bbox[2]), (0,0,255), 2)
        stats.append({
            'file': os.path.basename(path),
            'area': r.area,
            'brightness': b,
            'centroid_x': r.centroid[1],
            'centroid_y': r.centroid[0]
        })
    cv2.imwrite(os.path.join(OUT_DIR, f'annotated_{os.path.basename(path)}'), color)
    return stats

def main():
    paths = download_images()
    if not paths:
        print("Не удалось загрузить изображения.")
        return

    with ThreadPoolExecutor() as ex:
        df = pd.DataFrame([s for stats in ex.map(analyze, paths) for s in stats])

    csv_path = os.path.join(OUT_DIR, 'astro_data_stats.csv')
    df.to_csv(csv_path, index=False)
    print(f"Результаты сохранены в {csv_path}")
    
if __name__ == '__main__':
    main()
