from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='DetectionRecord',
            fields=[
                ('id',                 models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detection_type',     models.CharField(choices=[('pothole', 'Pothole Detection'), ('lane', 'Lane Detection')], max_length=20)),
                ('media_type',         models.CharField(choices=[('image', 'Image'), ('video', 'Video')], max_length=10)),
                ('input_file',         models.FileField(upload_to='uploads/%Y/%m/%d/')),
                ('result_file',        models.FileField(blank=True, null=True, upload_to='results/%Y/%m/%d/')),
                ('status',             models.CharField(choices=[('pending','Pending'),('processing','Processing'),('completed','Completed'),('failed','Failed')], default='pending', max_length=20)),
                ('pothole_count',      models.IntegerField(default=0)),
                ('pothole_detected',   models.BooleanField(default=False)),
                ('alert_sent',         models.BooleanField(default=False)),
                ('alert_sent_at',      models.DateTimeField(blank=True, null=True)),
                ('processing_time_ms', models.FloatField(blank=True, null=True)),
                ('error_message',      models.TextField(blank=True)),
                ('created_at',         models.DateTimeField(auto_now_add=True)),
                ('updated_at',         models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'Detection Record', 'verbose_name_plural': 'Detection Records', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='AlertLog',
            fields=[
                ('id',            models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detection',     models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='detection.detectionrecord')),
                ('phone_number',  models.CharField(max_length=20)),
                ('message_sid',   models.CharField(blank=True, max_length=100)),
                ('message_body',  models.TextField()),
                ('success',       models.BooleanField(default=False)),
                ('error_message', models.TextField(blank=True)),
                ('sent_at',       models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-sent_at']},
        ),
    ]
