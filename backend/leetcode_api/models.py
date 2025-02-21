from django.db import models

# Create your models here.
from django.db import models


class LeetCodeProblem(models.Model):
    problem_number = models.IntegerField(unique=True)
    problem_title = models.CharField(max_length=255)
    last_viewed = models.DateField(auto_now=True)
    tags = models.CharField(max_length=255, blank=True)
    problem_pattern = models.TextField()
    solution_approach = models.TextField()

    def __str__(self):
        return f"LeetCode {self.problem_number}: {self.problem_title}"
