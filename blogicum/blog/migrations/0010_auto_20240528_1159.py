# Generated by Django 3.2.16 on 2024-05-28 06:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_alter_comment_post_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='post_id',
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to='blog.post', verbose_name='К публикации'),
        ),
    ]