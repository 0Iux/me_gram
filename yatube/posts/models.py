from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слоган')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    group = models.ForeignKey(
        Group,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Укажите группу, к которой будет относиться пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:settings.QUANTITY_LETERS_FOR_STR]


class Comment(models.Model):
    text = models.TextField(verbose_name='Коментарий')
    created = models.DateTimeField(
        verbose_name='Дата коментария',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    post = models.ForeignKey(
        Post,
        verbose_name='К какому посту',
        on_delete=models.CASCADE,
        related_name='comments',
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий',
        verbose_name_plural = 'Коментарии'

    def __str__(self):
        return self.text[:settings.QUANTITY_LETERS_FOR_STR]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Юзер'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                check=models.Q('user' != 'author'),
                name='user_not_author'
            ),
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_user_author'
            ),
        ]
