from django.db import models

# Create your models here.
class Goods(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)

    #通讯函数
    def __str__(self):
        return self.name
    
class Welcome(models.Model):
    img = models.ImageField(upload_to='welcome',default='/welcome/slash.png')
    order = models.IntegerField()
    create_time = models.DateTimeField(auto_now=True)
    is_delete = models.BooleanField(default=False)
    class Meta:
        verbose_name = '欢迎表',
        verbose_name_plural = '欢迎表'
