import cv2
import numpy as np

class ColorBlockDetector:
    def __init__(self, distance_threshold=30):
        self.distance_threshold = distance_threshold
        self.h = 0
        self.w = 0
        
        # H的范围是0-179, S和V的范围是0-255
        self.color_ranges = {
            # 紫红色/粉色 (对应顶部块)
            'purple_pink': {'hsv_lower': np.array([100, 50, 100]), 'hsv_upper': np.array([160, 255, 255])},
            
            # 棕色/暗橙色 (对应左上块)
            'brown':       {'hsv_lower': np.array([0, 50, 60]),  'hsv_upper': np.array([70, 255, 200])},
            
            # 米黄色/淡米黄 (对应左下、右上块)
            # 这通常是低饱和度、高亮度的橙/黄色
            'beige':       {'hsv_lower': np.array([30, 20, 130]), 'hsv_upper': np.array([80, 50, 255])},
            
            # 白色 (对应右下块)
            # 需要极低的饱和度，极高的亮度
            'white':       {'hsv_lower': np.array([0, 0, 200]),   'hsv_upper': np.array([85, 30, 230])},
        }
        self.color_blocks = []
        # 添加一个实例变量来存储原始图像，供鼠标回调函数使用
        self.original_image = None    

    def detect_color_blocks(self, img):
        """检测颜色块的核心函数"""
        # 高斯模糊，再转HSV
        blurred = cv2.GaussianBlur(img, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        all_detected_blocks = []

         # 计算过滤噪点的阈值
        self.h, self.w = img.shape[:2]
        min_contour_area = self.h * self.w * 0.005
        print(f"  -> 阈值面积 {min_contour_area} ")
        
        for color_name, range_data in self.color_ranges.items():
            print(f"正在检测颜色: {color_name}")
            
            # 1. 创建掩码
            mask = cv2.inRange(hsv, range_data['hsv_lower'], range_data['hsv_upper'])
            
            # 2. 形态学操作
            kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            # 闭操作：先膨胀后腐蚀，用于填充块内的空洞和连接靠近的块
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_close)
            # 开操作：先腐蚀后膨胀，用于去除小的孤立噪点
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_open)

            # 3. 查找轮廓
            # cv2.RETR_EXTERNAL 只查找最外层轮廓，适合块状物体
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            print(f"  -> 找到 {len(contours)} 个轮廓")
           
            for contour in contours:
                area = cv2.contourArea(contour)
                # print(f"  -> 当前轮廓面积: {area}")

                if area > min_contour_area:
                    # 计算轮廓的质心
                    M = cv2.moments(contour)
                    if M["m00"] != 0: # 防止除零错误
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])

                        # 计算中心点周围的RGB均值
                        mean_r, mean_g, mean_b = self.calculate_local_mean_rgb(img, cx, cy, window_size=10)
                        
                        all_detected_blocks.append({
                            'color': color_name,
                            'center': (cx, cy),
                            'area': area,
                            'contour': contour,
                            'mean_rgb': (mean_r, mean_g, mean_b) # 将RGB均值存入字典
                        })
        
        # 去重逻辑
        unique_blocks = []
        for block in all_detected_blocks:
            is_duplicate = False
            for unique_block in unique_blocks:
                if self.is_close(block['center'], unique_block['center']):
                    # 如果是重复的，保留面积大的
                    if block['area'] > unique_block['area']:
                        unique_blocks.remove(unique_block)
                        unique_blocks.append(block)
                    #else:
                        # print(f"      -> 跳过重复块: 颜色={block['color']}, 中心={block['center']}")
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_blocks.append(block)
        
        self.color_blocks = unique_blocks
        return unique_blocks

    def is_close(self, point1, point2):
        distance = np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
        return distance < self.distance_threshold

    def match_blocks_to_positions(self):
        positions = [None, None, None, None, None]
        # 中心点距离过滤阈值
        dist_threshold = self.w * 0.05
        
        if not self.color_blocks:
            return positions

        # 按y轴大小排列色块
        sorted_by_y = sorted(self.color_blocks, key=lambda x: x['center'][1])

        to_remove = set()
        n = len(sorted_by_y)
        
        for i in range(n):
            for j in range(i + 1, n):
                if i in to_remove or j in to_remove:
                    continue

                x1, y1 = sorted_by_y[i]['center']
                x2, y2 = sorted_by_y[j]['center']

                center_dist = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

                if center_dist < dist_threshold:
                    if sorted_by_y[i]['area'] < sorted_by_y[j]['area']:
                        to_remove.add(i)
                        print(f"-> 发现邻近色块！中心距离 {center_dist:.1f} < {dist_threshold:.1f}。剔除面积较小的色块 [位置Y较浅的块]")
                    else:
                        to_remove.add(j)
                        print(f"-> 发现邻近色块！中心距离 {center_dist:.1f} < {dist_threshold:.1f}。剔除面积较小的色块 [位置Y较深的块]")

        filtered_blocks = [block for idx, block in enumerate(sorted_by_y) if idx not in to_remove]

        cnt = len(filtered_blocks)
        if cnt > 5:
            cnt = 5
            
        for i, block in enumerate(filtered_blocks[:cnt]):
            positions[i] = block

        return positions
    
    def calculate_local_mean_rgb(self, img_bgr, center_x, center_y, window_size=10):
        """
        计算指定中心点周围区域的R, G, B均值
        
        :param img_bgr: 输入的BGR图像
        :param center_x: 中心点X坐标
        :param center_y: 中心点Y坐标
        :param window_size: 计算均值的窗口半径 (例如，window_size=10 表示 21x21 的窗口)
        :return: (mean_r, mean_g, mean_b) 元组
        """
        h = self.h
        w = self.w
        
        # 计算窗口边界，确保不超出图像范围
        x1 = max(center_x - window_size, 0)
        x2 = min(center_x + window_size + 1, w)
        y1 = max(center_y - window_size, 0)
        y2 = min(center_y + window_size + 1, h)
        
        # 提取窗口区域
        roi = img_bgr[y1:y2, x1:x2]
        
        # 计算BGR三个通道的均值
        mean_b = np.mean(roi[:, :, 0])
        mean_g = np.mean(roi[:, :, 1])
        mean_r = np.mean(roi[:, :, 2])
        
        return float(mean_r), float(mean_g), float(mean_b)
    
    def mouse_callback(self, event, x, y, flags, param):
        """
        鼠标点击回调函数
        """
        if event == cv2.EVENT_LBUTTONDOWN and self.original_image is not None:
            # 获取BGR值
            bgr = self.original_image[y, x]
            b, g, r = bgr[0], bgr[1], bgr[2]
            
            # 转换为HSV值
            hsv_img = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
            h, s, v = hsv_img[0], hsv_img[1], hsv_img[2]
            
            print(f"--- 鼠标点击信息 ---")
            print(f"坐标: ({x}, {y})")
            print(f"RGB: ({r}, {g}, {b})")
            print(f"HSV: H:{h}, S:{s}, V:{v}")
            print("--------------------")

    def process_image(self, image_path, show_result=True):
        img = cv2.imread(image_path)
        if img is None:
            print(f"错误：无法加载图像 {image_path}")
            return None
        
        # 保存原始图像副本，用于鼠标回调
        self.original_image = img.copy()

        print("开始检测...")
        # 检测
        self.detect_color_blocks(img)
        
        print(f"\n总共检测到 {len(self.color_blocks)} 个不重复的色块")
        if self.color_blocks:
            for block in self.color_blocks:
                r, g, b = block['mean_rgb']
                print(f"  - 颜色: {block['color']}, 中心: {block['center']}, 面积: {int(block['area'])}, 平均RGB: (R:{r:.2f}, G:{g:.2f}, B:{b:.2f})")
        else:
            print("  - 未检测到任何色块")

        # 分配位置
        results = self.match_blocks_to_positions()

        # 打印最终结果
        print("\n--- 按位置排序的结果 ---")
        for i, block in enumerate(results):
            if block:
                r, g, b = block['mean_rgb']
                print(f"位置 {i+1}: 颜色='{block['color']}', 中心={block['center']}, 面积={int(block['area'])}, 平均RGB: (R:{r:.2f}, G:{g:.2f}, B:{b:.2f})")
            else:
                print(f"位置 {i+1}: 未检测到色块")

        if show_result:
            # 可视化
            for i, block in enumerate(results):
                if block is not None:
                    center_x, center_y = block['center']
                    cv2.circle(img, (center_x, center_y), 5, (0, 255, 0), -1)
                    cv2.drawContours(img, [block['contour']], -1, (255, 0, 0), 2)
                    cv2.putText(img, f'P{i+1}', (center_x + 10, center_y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    
            # 创建窗口并设置鼠标回调
            cv2.namedWindow('Color Block Detection Result',cv2.WINDOW_NORMAL)
            cv2.setMouseCallback('Color Block Detection Result', self.mouse_callback)
            
            print("\n--- 提示 ---")
            print("图像已显示。请单击图像上的色块以获取其颜色值 (RGB & HSV)。")
            print("关闭窗口以结束程序。")
            print("----------")

            cv2.resizeWindow("Color Block Detection Result", 500, 600)
            cv2.imshow('Color Block Detection Result', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # 返回结果列表
        result_list = []
        for i, block in enumerate(results):
            if block:
                r, g, b = block['mean_rgb']
                rgb = (int(round(r)), int(round(g)), int(round(b)))
                result_list.append({
                    'position_id': i + 1,
                    'color': block['color'],
                    'center_x': block['center'][0],
                    'center_y': block['center'][1],
                    'area': int(block['area']),
                    'mean_rgb': rgb
                })
            else:
                result_list.append({
                    'position_id': i + 1,
                    'color': None,
                    'center_x': -1,
                    'center_y': -1,
                    'area': 0,
                    'mean_rgb': None
                })
        return result_list

if __name__ == "__main__":
    # 实例化检测器
    detector = ColorBlockDetector()
    
    # 图像路径
    image_path = './media/welcome/tu5.jpg'
    
    # 处理图像
    results = detector.process_image(image_path)
    print("\n--- 最终返回列表 ---")
    print(results)