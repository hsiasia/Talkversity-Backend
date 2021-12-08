from django.db import models


# 目標
class Target(models.Model):
    category = models.CharField(max_length=200)
    last_modify_date = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category

    class Meta:
        db_table = "target"


# 情境
class Scenario(models.Model):
    target = models.ForeignKey(Target,
                               related_name='scenarios',
                               on_delete=models.CASCADE, null=True)
    content = models.CharField(max_length=200)
    intro = models.CharField(max_length=200,null=True)
    last_modify_date = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = "scenario"
