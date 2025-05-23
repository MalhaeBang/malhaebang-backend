from django.db import models
import json
class House(models.Model):
    house_id = models.AutoField(primary_key=True)
    house_num = models.BigIntegerField()
    address = models.CharField(max_length=255)
    agent_comm = models.IntegerField(null=True, blank=True)
    agent_info = models.CharField(max_length=255)
    area_size = models.CharField(max_length=255)
    available_from = models.CharField(max_length=255)
    building_type = models.CharField(max_length=255)
    built_date = models.CharField(max_length=255, null=True, blank=True)
    deposit_type = models.CharField(max_length=255)
    direction = models.CharField(max_length=255)
    dong = models.CharField(max_length=255)
    gpt_description = models.TextField(null=True, blank=True)
    gu = models.CharField(max_length=255)
    house_explanations = models.TextField(null=True, blank=True)
    house_feature = models.TextField(null=True, blank=True)
    img_url = models.TextField(null=True, blank=True)
    options = models.TextField(null=True, blank=True)
    posted_at = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    safety_grade = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255)
    bath_count = models.IntegerField(null=True, blank=True)
    deposit = models.IntegerField(null=True, blank=True)
    floor = models.IntegerField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    management_fee = models.IntegerField(null=True, blank=True)
    monthly_rent = models.IntegerField(null=True, blank=True)
    parking = models.IntegerField()
    rooms_count = models.IntegerField()
    space = models.IntegerField(null=True, blank=True)
    total_floor = models.IntegerField(null=True, blank=True)
    apt_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'house'       # 실제 DB 테이블 이름
        managed = False          # 기존 테이블 사용 시 Django가 관리하지 않도록

    def __str__(self):
        return f"[{self.title}] {self.address}"

    def get_img_list(self):
        if not self.img_url:
            return []
        try:
            return json.loads(self.img_url)
        except json.JSONDecodeError:
            return []