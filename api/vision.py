import cv2
import numpy as np
import os

class Vision:
    def __init__(self, distance_threshold=15, min_contour_area=50):
        """
        初始化颜色块检测器
        :param distance_threshold: 中心距离阈值，小于此值则判定为重复
        :param min_contour_area: 最小轮廓面积，过滤噪声
        """
        self.distance_threshold = distance_threshold
        self.min_contour_area = min_contour_area
        self.img_global = None
        self.color_blocks = []  # 原始检测结果
        self.position_blocks = [None]*5  # 按位置1-5排列的结果（漏检则为None）
        self.detected_centers = []

    def on_mouse_click(self, event, x, y, flags, param):
        """鼠标点击回调函数，用于显示点击位置的颜色值"""
        if event == cv2.EVENT_LBUTTONDOWN and self.img_global is not None:
            b, g, r = self.img_global[y, x]
            rgb = (int(r), int(g), int(b))
            print(f"点击位置 (x,y): ({x}, {y})")
            print(f"RGB颜色值: {rgb} | BGR: ({int(b)}, {int(g)}, {int(r)})")
            print("-" * 40)

    def _match_blocks_to_positions(self, img_height, img_width):
        """
        以顶部中间色块为基准划分位置：
        位置1(最顶上)：顶部中间的色块
        位置2(左上)：顶部色块左侧 + 上半区域
        位置3(左下)：顶部色块左侧 + 下半区域
        位置4(右上)：顶部色块右侧 + 上半区域
        位置5(右下)：顶部色块右侧 + 下半区域
        """
        self.position_blocks = [None]*5
        if not self.color_blocks:
            return
        
        # 步骤1：找到顶部中间的色块（位置1）
        # 先按y坐标找最顶部的色块，再筛选x坐标最接近图像中心的那个
        img_center_x = img_width / 2
        top_candidates = sorted(self.color_blocks, key=lambda b: b['center'][1])[:3]  # 取y最小的前3个
        top_block = min(top_candidates, key=lambda b: abs(b['center'][0] - img_center_x))
        
        self.position_blocks[0] = {
            **top_block, 
            'position_id': 1, 
            'position_name': '最顶上',
            'center': top_block['center']
        }
        top_cx, top_cy = top_block['center']  # 顶部色块的中心坐标（作为划分基准）
        remaining_blocks = [b for b in self.color_blocks if b != top_block]
        
        # 步骤2：定义4个区域的划分基准
        mid_x = top_cx  # 以顶部色块的x坐标为左右分界（不再用中位数）
        mid_y = img_height *2/5  # 以图像中间为上下分界
        
        # 步骤3：遍历剩余色块，匹配到对应位置
        for block in remaining_blocks:
            cx, cy = block['center']
            # 判定所属区域
            if cx < mid_x:  # 左侧区域
                if cy < mid_y:  # 左上（位置2）
                    self.position_blocks[1] = {**block, 'position_id': 2, 'position_name': '左上'}
                else:  # 左下（位置3）
                    self.position_blocks[2] = {**block, 'position_id': 3, 'position_name': '左下'}
            else:  # 右侧区域
                if cy < mid_y:  # 右上（位置4）
                    self.position_blocks[3] = {**block, 'position_id': 4, 'position_name': '右上'}
                else:  # 右下（位置5）
                    self.position_blocks[4] = {**block, 'position_id': 5, 'position_name': '右下'}

    def detect(self, image_path, color_ranges, show_result=True):
        """
        检测图像中的颜色块，并匹配到5个预设位置（漏检位置留空）
        :param image_path: 图像文件路径
        :param color_ranges: 颜色范围列表
        :param show_result: 是否显示标记后的图像
        :return: 按位置1-5排列的结果列表（None表示漏检）
        """
        # 重置状态
        self.color_blocks = []
        self.position_blocks = [None]*5
        self.detected_centers = []

        # 1. 读取图像
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像文件不存在: {os.path.abspath(image_path)}")

        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图像: {os.path.abspath(image_path)}")
        img_height, img_width = img.shape[:2]  # 获取图像尺寸

        # 2. 转换到 HSV 颜色空间
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 3. 遍历每个颜色范围，提取色块
        for color_info in color_ranges:
            mask = cv2.inRange(hsv, color_info['lower'], color_info['upper'])
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)

            for cnt in contours:
                if cv2.contourArea(cnt) < self.min_contour_area:
                    continue

                x, y, w, h = cv2.boundingRect(cnt)
                center_x = x + w // 2
                center_y = y + h // 2

                # 去重检查
                is_duplicate = False
                for (cx, cy) in self.detected_centers:
                    distance = np.sqrt((center_x - cx)**2 + (center_y - cy)**2)
                    if distance < self.distance_threshold:
                        is_duplicate = True
                        break
                if is_duplicate:
                    continue

                # 记录色块信息
                bgr = img[center_y, center_x]
                rgb = (bgr[2], bgr[1], bgr[0])
                self.color_blocks.append({
                    'name': color_info['name'],
                    'bbox': (x, y, w, h),
                    'center': (center_x, center_y),
                    'rgb': rgb
                })
                self.detected_centers.append((center_x, center_y))

                # 绘制标记
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 1)
                cv2.circle(img, (center_x, center_y), 2, (0, 0, 255), -1)

        # 4. 将检测到的色块匹配到5个预设位置
        self._match_blocks_to_positions(img_height, img_width)

        # 5. 输出结构化结果
        print("=== 按位置1-5的检测结果（None表示漏检）===")
        position_names = ['顶部', '左上', '左下', '右上', '右下']
        for idx, (block, pos_name) in enumerate(zip(self.position_blocks, position_names)):
            position_id = idx + 1  # 直接从索引计算位置ID
            if block:
                print(f"位置{position_id}({pos_name}): {block['name']} | 中心坐标: {block['center']} | RGB: {block['rgb']}")
            else:
                print(f"位置{position_id}({pos_name}): 漏检")
        print("-" * 50)

        # 6. 显示标记后的图像
        if show_result:
            self.img_global = img
            cv2.namedWindow('Detected Blocks', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Detected Blocks', 800, 600)
            cv2.setMouseCallback('Detected Blocks', self.on_mouse_click)
            cv2.imshow('Detected Blocks', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return self.position_blocks

# 示例用法
if __name__ == "__main__":
    # 定义颜色范围（根据你的实际需求调整）
    color_ranges = [
        {'name': 'purple', 'lower': np.array([100, 50, 50]), 'upper': np.array([150, 255, 255])},
        {'name': 'dark_brown', 'lower': np.array([0, 50, 50]), 'upper': np.array([20, 255, 200])},
        {'name': 'light_orange', 'lower': np.array([10, 50, 150]), 'upper': np.array([25, 255, 255])},
        {'name': 'orange', 'lower': np.array([15, 50, 150]), 'upper': np.array([25, 255, 255])},
        {'name': 'light_yellow', 'lower': np.array([20, 50, 150]), 'upper': np.array([35, 255, 255])},
    ]

    # 创建检测器并执行检测
    detector = Vision(distance_threshold=15, min_contour_area=50)
    try:
        # 执行检测，返回按位置1-5排列的结果（None=漏检）
        position_results = detector.detect(
            image_path='./media/welcome/home_img.jpg',  # 替换为你的图像路径
            color_ranges=color_ranges,
            show_result=True
        )
                
    except Exception as e:
        print(f"检测失败: {e}")
