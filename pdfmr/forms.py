from django import forms
from django.conf import settings
from django.core.files.storage import default_storage
import os, random, string
from upload_validator import FileTypeValidator


class UploadForm(forms.Form):
    """PDFアップロード用フォームの定義
       saveメソッドはアップロードしたPDFを一時フォルダに保存する。
    """
    document = forms.FileField(label="PDFアップロード",
                               widget=forms.ClearableFileInput(attrs={'multiple': True}),
                               validators=[FileTypeValidator(allowed_types=['application/pdf'])])

    def save(self):
        upload_files = self.files.getlist('document')
        temp_dir = os.path.join(settings.MEDIA_ROOT, self.create_dir(10))
        for pdf in upload_files:
            default_storage.save(os.path.join(temp_dir, pdf.name), pdf)
        return temp_dir

    def create_dir(self, n):
        """一時フォルダ名生成関数"""
        return 'pdf\\' + ''.join(random.choices(string.ascii_letters + string.digits, k=n))
