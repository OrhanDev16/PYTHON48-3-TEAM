from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class UserProfile(AbstractUser):


    STATUS_BEGINNER = "beginner"
    STATUS_ACTIVE = "active"
    STATUS_PRO = "pro"
    STATUS_CHOICES = [
        (STATUS_BEGINNER, "Beginner"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_PRO, "Pro"),
    ]

    age = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(14), MaxValueValidator(70)],
    )
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_BEGINNER
    )
    date_register = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    category_img = models.ImageField(upload_to="categories/", blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["category_name"]

    def __str__(self):
        return self.category_name


class Project(models.Model):
    project_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, related_name="projects", on_delete=models.CASCADE
    )
    owner = models.ForeignKey(
        UserProfile, related_name="projects", on_delete=models.CASCADE
    )
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.project_name

    def get_tasks_count(self):
        return self.tasks.count()

    def get_completed_percent(self):
        total = self.get_tasks_count()
        if total == 0:
            return 0
        completed = self.tasks.filter(completed=True).count()
        return round(completed / total * 100)


# 2.6 Tag
class Tag(models.Model):
    tag_name = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ["tag_name"]

    def __str__(self):
        return self.tag_name


# 2.4 Task
class Task(models.Model):
    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM
    )
    deadline = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(
        Project, related_name="tasks", on_delete=models.CASCADE
    )
    assignee = models.ForeignKey(
        UserProfile,
        related_name="assigned_tasks",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="tasks")

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.title

    def get_progress(self):
        """Percentage of completed subtasks (0 if there are none)."""
        total = self.subtasks.count()
        if total == 0:
            return 0
        done = self.subtasks.filter(completed=True).count()
        return round(done / total * 100)

    def get_comments_count(self):
        return self.comments.count()

    def is_overdue(self):
        if self.deadline is None:
            return False
        return (not self.completed) and self.deadline < timezone.now()


class Subtask(models.Model):
    task = models.ForeignKey(Task, related_name="subtasks", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title


class TaskFile(models.Model):
    task = models.ForeignKey(Task, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to="task_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} ({self.task.title})"


class Comment(models.Model):
    task = models.ForeignKey(Task, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_date"]

    def __str__(self):
        return f"Comment by {self.user} on {self.task}"


class Favorite(models.Model):
    user = models.OneToOneField(
        UserProfile, related_name="favorite", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Favorites of {self.user}"


class FavoriteItem(models.Model):
    favorite = models.ForeignKey(
        Favorite, related_name="items", on_delete=models.CASCADE
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("favorite", "task")  # a task can't be favorited twice

    def __str__(self):
        return f"{self.task} in favorites of {self.favorite.user}"

