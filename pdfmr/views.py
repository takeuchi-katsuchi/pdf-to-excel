from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from .forms import UploadForm
from django.core.files.storage import default_storage
import shutil, os
from .utils import create_excel
from django.contrib.auth.decorators import login_required #追加


def top(request):
    return render(request, 'pdfmr/top.html')


class UploadView(LoginRequiredMixin, generic.FormView):
    form_class = UploadForm
    template_name = 'pdfmr/upload_form.html'


    def form_valid(self, form):
        user_name = self.request.user.username
        user_dir = os.path.join(settings.MEDIA_ROOT, "excel", user_name)
        if not os.path.isdir(user_dir):
            os.makedirs(user_dir)
        temp_dir = form.save()
        err = create_excel(temp_dir, user_name)  # PDF->Excelデータ生成
        if err:
            shutil.rmtree(temp_dir)  # upload一時フォルダの削除
            context = {
                'err': err,
            }
            return render(self.request, 'pdfmr/complete.html', context)
        # pdf -> PDF⇒excel変換処理の実行（あとで実装）
        # shutil.rmtree(temp_dir)
        _, file_list = default_storage.listdir(os.path.join(settings.MEDIA_ROOT, "excel", user_name))
        message = "正常終了しました。"
        context = {
            'file_list': file_list,
            'user_name':user_name,
            'message': message,
        }
        return render(self.request, 'pdfmr/complete.html', context)


    def form_invalid(self, form):
        return render(self.request, 'pdfmr/upload_form.html', {'form': form})


class ListView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'pdfmr/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        """自分が作成したExcelファイルだけを一覧表示"""
        login_user_name = self.request.user.username

        if not default_storage.exists(os.path.join(settings.MEDIA_ROOT, "excel", login_user_name)):
            warning_message = "このユーザでは一度もファイル作成が行われていません。"
            context = {
                'warning_message': warning_message,
            }
            return context

        file_list = default_storage.listdir(os.path.join(settings.MEDIA_ROOT, "excel", login_user_name))[1]
        context = {
            'file_list': file_list,
            'login_user_name': login_user_name,
        }
        return context


@login_required
def dell_file(request):
    checks_value = request.POST.getlist('checks')  # CheckBox＝Onのファイル名を取得
    login_user_name = request.user.username  # ログオンユーザ名を取得

    # Excelファイルの格納パスを取得
    if checks_value:
        for file in checks_value:
            path = os.path.join(settings.MEDIA_ROOT, "excel", login_user_name, file)
            default_storage.delete(path)  # CheckBox=ONのファイルをサーバから削除
        return render(request, 'pdfmr/delete.html', {'checks_value': checks_value})
    else:
        login_user_name = request.user.username
        file_list = default_storage.listdir(os.path.join(settings.MEDIA_ROOT, "excel", login_user_name))[1]
        warning_message = "削除対象ファイルが選択されていません。"

        context = {
            'file_list': file_list,
            'login_user_name': login_user_name,
            'warning_message': warning_message,
        }
        return render(request, 'pdfmr/list.html', context)

