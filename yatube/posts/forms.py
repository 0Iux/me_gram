from django import forms
from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        labels = {
            'text': 'Текст',
            'group': 'Группа',
            'image': 'Изображение'
        }
        help_texts = {
            'text': 'Текст вашего поста',
            'group': 'Название группы поста',
            'image': 'Прикрепите свое изображение'
        }
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        labels = {
            'text': 'Комментарий'
        }
        fields = ('text',)
