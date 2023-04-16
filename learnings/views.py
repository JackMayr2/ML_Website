from learnings.models import Learning, Comment, Fav
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from learnings.forms import CreateForm, CommentForm
from learnings.owner import OwnerListView, OwnerDeleteView
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Q


####################################
class PostListView(View):
    model = Learning
    template_name = "learnings/learning_list.html"

    def get(self, request):
        strval = request.GET.get("search", False)
        if strval:
            # Simple title-only search
            # objects = Post.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            # __icontains for case-insensitive search
            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            learning_list = Learning.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else:
            learning_list = Learning.objects.all().order_by('-updated_at')[:10]

        # Augment the post_list
        for obj in learning_list:
            obj.natural_updated = naturaltime(obj.updated_at)

        ctx = {'learning_list': learning_list, 'search': strval}
        return render(request, self.template_name, ctx)


###################################################

class LearningListView(OwnerListView):
    model = Learning
    # By convention:
    template_name = "learnings/learning_list.html"

    def get(self, request):
        strval = request.GET.get("search", False)
        if strval:

            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            learning_list = Learning.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else:
            learning_list = Learning.objects.all().order_by('-updated_at')[:10]

        favorites = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_learnings.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [row['id'] for row in rows]
        ctx = {'learning_list': learning_list, 'search': strval, 'favorites': favorites}
        return render(request, self.template_name, ctx)


class LearningDetailView(OwnerListView):
    model = Learning
    template_name = "learnings/learning_detail.html"

    def get(self, request, pk):
        x = Learning.objects.get(id=pk)
        comments = Comment.objects.filter(learning=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = {'learning': x, 'comments': comments, 'comment_form': comment_form}
        return render(request, self.template_name, context)


class LearningCreateView(LoginRequiredMixin, View):
    template_name = 'learnings/learning_form.html'
    success_url = reverse_lazy('learnings:all')
    fields = ['title', 'price', 'text', 'picture']

    def get(self, request, pk=None):
        form = CreateForm()
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        learning = form.save(commit=False)
        learning.owner = self.request.user
        learning.save()

        # Adjust the model owner before saving
        inst = form.save(commit=False)
        inst.owner = self.request.user
        inst.save()

        # https://django-taggit.readthedocs.io/en/latest/forms.html#commit-false
        form.save_m2m()  # Add this

        return redirect(self.success_url)


class LearningUpdateView(LoginRequiredMixin, View):
    template_name = 'learnings/learning_form.html'
    success_url = reverse_lazy('learnings:all')
    fields = ['title', 'price', 'text', 'picture']

    def get(self, request, pk):
        pic = get_object_or_404(Learning, id=pk, owner=self.request.user)
        form = CreateForm(instance=pic)
        ctx = {'form': form}
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None):
        learning = get_object_or_404(Learning, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=learning)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)

        learning = form.save(commit=False)
        learning.save()

        # Adjust the model owner before saving
        inst = form.save(commit=False)
        inst.owner = self.request.user
        inst.save()

        # https://django-taggit.readthedocs.io/en/latest/forms.html#commit-false
        form.save_m2m()  # Add this

        return redirect(self.success_url)


class LearningDeleteView(OwnerDeleteView):
    model = Learning
    template_name = "learnings/learning_confirm_delete.html"


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        la = get_object_or_404(Learning, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, learning=la)
        comment.save()
        return redirect(reverse('learnings:learning_detail', args=[pk]))


class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "learnings/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        learning = self.object.learning
        return reverse('learnings:learning_detail', args=[learning.id])


def stream_file(request, pk):
    learning = get_object_or_404(Learning, id=pk)
    response = HttpResponse()
    response['Content-Type'] = learning.content_type
    response['Content-Length'] = len(learning.picture)
    response.write(learning.picture)
    return response


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError


@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        print("Add PK", pk)
        t = get_object_or_404(Learning, id=pk)
        fav = Fav(user=request.user, learning=t)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        print("Delete PK", pk)
        t = get_object_or_404(Learning, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, learning=t).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()
