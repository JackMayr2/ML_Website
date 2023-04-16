from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.conf import settings


class Article(models.Model):
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2, "Title must be greater than 2 characters")]
    )
    # price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    text = models.TextField()
    gist_link = models.TextField()

    # https://django-taggit.readthedocs.io/en/latest/api.html#TaggableManager
    tags = TaggableManager(blank=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       through='ArticleFav', related_name='favorite_articles')
    comments = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                      through='ArticleComment', related_name='article_comments_owned')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        return self.title


class ArticleFav(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # https://docs.djangoproject.com/en/4.0/ref/models/options/#unique-together
    class Meta:
        unique_together = ('article', 'user')

    def __str__(self):
        return '%s likes %s' % (self.user.username, self.article.title[:10])


class ArticleComment(models.Model):
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        if len(self.text) < 15: return self.text
        return self.text[:11] + ' ...'


######################################################
from django.db import models

# Create your models here.
