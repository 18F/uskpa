# Generated by Django 2.0.5 on 2018-05-31 14:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kpc', '0002_editrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificateconfig',
            name='reviewer_emails',
            field=models.TextField(blank=True, help_text='Comma delimited list of email addresses to be notified upon submission of a request to edit a certificate.'),
        ),
        migrations.AddField(
            model_name='historicalcertificateconfig',
            name='reviewer_emails',
            field=models.TextField(blank=True, help_text='Comma delimited list of email addresses to be notified upon submission of a request to edit a certificate.'),
        ),
        migrations.AlterField(
            model_name='editrequest',
            name='certificate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='edit_requests', to='kpc.Certificate'),
        ),
    ]
