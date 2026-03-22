import os
import hashlib
import numpy as np
from django.conf import settings

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from api.serializers import GoodsSerializer
from goods.models import Goods, Welcome
from .detector import ColorBlockDetector

@api_view(['GET', 'POST'])
def goods_list(request):
    if request.method == 'GET':
        goods = Goods.objects.all()
        serializer = GoodsSerializer(goods, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = GoodsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def goods_detail(request, id):
    try:
        goods = Goods.objects.get(id=id)
    except Goods.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = GoodsSerializer(goods)
        return Response(serializer.data)
    if request.method == 'PUT':
        serializer = GoodsSerializer(goods, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        goods.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def welcome(request):
    # 1 查出order最大的一张图片，返回给前端
    res = Welcome.objects.all().order_by('-order').first()
    img = 'http://127.0.0.1:8000/media/' + str(res.img)
    return Response({'code': 100, 'msg': '成功', 'result': img})

@api_view(['POST'])
def sweat_detect(request):
    try:
        # 1. 接收上传的图片和MD5值
        if 'file' not in request.FILES:
            return Response({'code': 400, 'msg': '未上传图片'}, status=400)
        
        uploaded_file = request.FILES['file']
        wx_md5 = request.POST.get('image_md5', '')  # 小程序端计算的MD5
        print(f"小程序MD5: {wx_md5}")

        # 2. 计算后端接收的文件MD5并对比哈希值
        file_hash = hashlib.md5()
        for chunk in uploaded_file.chunks():
            file_hash.update(chunk)
        backend_md5 = file_hash.hexdigest()
        print(f"后端计算的MD5: {backend_md5}")

        if wx_md5 and wx_md5 != backend_md5:
            print(f"⚠️ 哈希值不一致！小程序: {wx_md5} | 后端: {backend_md5}")
            return Response({
                'code': 400,
                'msg': '图片传输过程中被修改（哈希值不一致）',
                'data': {
                    'wx_md5': wx_md5,
                    'backend_md5': backend_md5
                }
            }, status=400)        
        uploaded_file.seek(0)  # 重置文件指针，准备保存
        
        # 3. 保存到临时目录
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        
        with open(temp_file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # 4. 调用ColorBlockDetector类进行检测
        detector = ColorBlockDetector()
        color_blocks = detector.process_image(
            image_path=temp_file_path,
            show_result=False  # 后端运行时不显示图像窗口
        )

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"临时文件已删除：{temp_file_path}")

        count = len(color_blocks)
        if count>5:
            print(f"检测到{count}个色块")
            return Response({
            'code': 400,
            'msg': f'检测失败：识别到{count}个色块，超出最大允许数量',
            'data': None
        }, status=400)
        
        # 5. 处理结果：将np.uint8转为Python原生类型，方便JSON序列化
        def serialize_block(block):
            if block['color'] is None:
                return None
            return {
                'position_id': block['position_id'],                
                'center_x': block['center_x'],
                'center_y': block['center_y'],
                'area': block['area'],
                'rgb': tuple(int(c) for c in block['mean_rgb'])  # 转换uint8为int
            }
        
        serialized_result = [serialize_block(b) for b in color_blocks]

        output_array = []
        for block in serialized_result:
            if block is None:
                # 漏检位置：[0, 0, 0, 0]
                output_array.append([None, None, None, None])
            else:
                r, g, b = block['rgb']
                # 格式：[R, G, B, 0]
                output_array.append([r, g, b, 0])
        
        # 6. 返回JSON结果
        return Response({
            'code': 200,
            'msg': '检测成功',
            'data': output_array
        })
    
    except Exception as e:
        return Response({
            'code': 500,
            'msg': f'检测失败: {str(e)}',
            'data': None
        }, status=500)
    