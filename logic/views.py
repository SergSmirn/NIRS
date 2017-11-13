from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import ExpForm
from .models import Experiment
from django.views.generic.edit import FormView


@login_required(login_url='/auth/')
def index(request):
    return render(request, 'hello.html')


class ExpFormView(FormView):
    form_class = ExpForm
    success_url = "/"
    template_name = "exp_create.html"

    def form_valid(self, form):
        exp = form.save(commit=False)
        exp.user = self.request.user
        exp.calc()
        exp.save()
        return super(ExpFormView, self).form_valid(form)


def checkExp(request):
    user = request.user
    exp = user.experiments.all()
    return render(request, "check_exp.html", {'exp': exp})

