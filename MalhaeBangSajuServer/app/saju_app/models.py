from django.db import models
import json
class House(models.Model):
    house_id = models.AutoField(primary_key=True)
    house_num = models.BigIntegerField()
    address = models.CharField(max_length=255, default='정보없음')
    agent_comm = models.CharField(max_length=255, null=True, blank=True)
    agent_info = models.CharField(max_length=255, default='정보없음')
    area_size = models.CharField(max_length=255, default='정보없음')
    availabe_from = models.CharField(max_length=255, default='정보없음')
    building_type = models.CharField(max_length=255, default='정보없음')
    built_date = models.CharField(max_length=255, null=True, blank=True)
    deposit_type = models.CharField(max_length=255, default='정보없음')
    direction = models.CharField(max_length=255, default='정보없음')
    dong = models.CharField(max_length=255, default='정보없음')
    floor = models.CharField(max_length=255, default='정보없음')
    gu = models.CharField(max_length=255, default='정보없음')
    house_explanations = models.TextField(null=True, blank=True)
    house_feature = models.TextField(null=True, blank=True)
    img_url = models.TextField(null=True, blank=True)  # JSON 문자열 저장
    management_fee = models.CharField(max_length=255, null=True, blank=True)
    options = models.TextField(null=True, blank=True)
    parking = models.CharField(max_length=255, default='정보없음')
    posted_at = models.CharField(max_length=255, default='정보없음')
    price = models.CharField(max_length=255, default='정보없음')
    rooms_count = models.CharField(max_length=255, default='정보없음')
    title = models.CharField(max_length=255, default='정보없음')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
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