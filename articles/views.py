from articles.models import Article, ArticleComment, ArticleFav
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from articles.forms import CommentForm
from articles.owner import OwnerListView, OwnerDeleteView
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Q


class PostListView(View):
    model = Article
    template_name = "articles/article_list.html"

    def get(self, request):
        strval = request.GET.get("search", False)
        if strval:
            # Simple title-only search
            # objects = Post.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            # __icontains for case-insensitive search
            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            article_list = Article.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else:
            article_list = Article.objects.all().order_by('-updated_at')[:10]

        # Augment the post_list
        for obj in article_list:
            obj.natural_updated = naturaltime(obj.updated_at)

        ctx = {'article_list': article_list, 'search': strval}
        return render(request, self.template_name, ctx)


###################################################

class ArticleListView(OwnerListView):
    model = Article
    # By convention:
    template_name = "articles/article_list.html"

    def get(self, request):
        strval = request.GET.get("search", False)
        if strval:

            query = Q(title__icontains=strval)
            query.add(Q(text__icontains=strval), Q.OR)
            article_list = Article.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else:
            article_list = Article.objects.all().order_by('-updated_at')[:10]

        favorite_articles = list()
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_articles.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [row['id'] for row in rows]
        ctx = {'article_list': article_list, 'search': strval, 'favorite articles': favorite_articles}
        return render(request, self.template_name, ctx)


class ArticleDetailView(OwnerListView):
    model = Article
    template_name = "articles/article_detail.html"

    def get(self, request, pk):
        x = Article.objects.get(id=pk)
        article_comments = ArticleComment.objects.filter(article=x).order_by('-updated_at')
        comment_form = CommentForm()
        context = {'article': x, 'comments': article_comments, 'comment_form': comment_form}
        return render(request, self.template_name, context)


class ArticleCommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        a = get_object_or_404(Article, id=pk)
        article_comment = ArticleComment(text=request.POST['comment'], owner=request.user, article=a)
        article_comment.save()
        return redirect(reverse('articles:article_detail', args=[pk]))

class ArticleCommentDeleteView(OwnerDeleteView):
    model = ArticleComment
    template_name = "articles/articlecomment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        article = self.object.article
        return reverse('articles:article_detail', args=[article.id])


def stream_file(request, pk):
    article = get_object_or_404(Article, id=pk)
    response = HttpResponse()
    response['Content-Type'] = article.content_type
    response['Content-Length'] = len(article.picture)
    response.write(article.picture)
    return response


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError


@method_decorator(csrf_exempt, name='dispatch')
class ArticleAddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        print("Add PK", pk)
        t = get_object_or_404(Article, id=pk)
        articlefav = ArticleFav(user=request.user, article=t)
        try:
            articlefav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class ArticleDeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        print("Delete PK", pk)
        t = get_object_or_404(Article, id=pk)
        try:
            articlefav = ArticleFav.objects.get(user=request.user, article=t).delete()
        except ArticleFav.DoesNotExist as e:
            pass

        return HttpResponse()
