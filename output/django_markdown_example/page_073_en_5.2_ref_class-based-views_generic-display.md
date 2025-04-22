# Generic Display Views

The two following generic class-based views are designed to display data. On many projects they are typically the most commonly used views.

## `DetailView`

*class* `django.views.generic.detail.DetailView`

While this view is executing, `self.object` will contain the object that the view is operating upon.

**Ancestors (MRO)**

This view inherits methods and attributes from the following views:

*   [`django.views.generic.detail.SingleObjectTemplateResponseMixin`](https://docs.djangoproject.com/en/5.2/mixins-single-object/#django.views.generic.detail.SingleObjectTemplateResponseMixin)
*   [`django.views.generic.base.TemplateResponseMixin`](https://docs.djangoproject.com/en/5.2/mixins-simple/#django.views.generic.base.TemplateResponseMixin)
*   [`django.views.generic.detail.BaseDetailView`](#django.views.generic.detail.BaseDetailView)
*   [`django.views.generic.detail.SingleObjectMixin`](https://docs.djangoproject.com/en/5.2/mixins-single-object/#django.views.generic.detail.SingleObjectMixin)
*   [`django.views.generic.base.View`](https://docs.djangoproject.com/en/5.2/base/#django.views.generic.base.View)

**Method Flowchart**

1.  [`setup()`](https://docs.djangoproject.com/en/5.2/base/#django.views.generic.base.View.setup)
2.  [`dispatch()`](https://docs.djangoproject.com/en/5.2/base/#django.views.generic.base.View.dispatch)
3.  [`http_method_not_allowed()`](https://docs.djangoproject.com/en/5.2/base/#django.views.generic.base.View.http_method_not_allowed)
4.  [`get_template_names()`](https://docs.djangoproject.com/en/5.2/mixins-simple/#django.views.generic.base.TemplateResponseMixin.get_template_names)
5.  [`get_slug_field()`](https://docs.djangoproject.com/en/5.2/mixins-single-object/#django.views.generic.detail.SingleObjectMixin.get_slug_field)
6.  [`get_queryset()`](https://docs.djangoproject.com/en/5.2/mixins-single-object/#django.views.generic.detail.SingleObjectMixin.get_queryset)
7.  [`get_object()`](https://docs.djangoproject.com/en/5.2/mixins-single-object/#django.views.generic.detail.SingleObjectMixin.get_object)
8.  [`get_context_object_name()`](https://docs.djangoproject.com/en/5.2/mixins-single-object/#django.views.generic.detail.SingleObjectMixin.get_context_object_name)
9.  [`get_context_data()`](https://docs.djangoproject.com/en/5.2/mixins-single-object/#django.views.generic.detail.SingleObjectMixin.get_context_data)
10. [`get()`](#django.views.generic.detail.BaseDetailView.get)
11. [`render_to_response()`](https://docs.djangoproject.com/en/5.2/mixins-simple/#django.views.generic.base.TemplateResponseMixin.render_to_response)

**Example myapp/views.py**:

```python
from django.utils import timezone
from django.views.generic.detail import DetailView
from articles.models import Article

class ArticleDetailView(DetailView):
    model = Article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context
```

**Example myapp/urls.py**:

```python
from django.urls import path
from article.views import ArticleDetailView

urlpatterns = [
    path("<slug:slug>/", ArticleDetailView.as_view(), name="article-detail"),
]
```

**Example myapp/article\_detail.html**:

```html
<h1>{{ object.headline }}</h1>
<p>{{ object.content }}</p>
<p>Reporter: {{ object.reporter }}</p>
<p>Published: {{ object.pub_date|date }}</p>
<p>Date: {{ now|date }}</p>
```

*class* `django.views.generic.detail.BaseDetailView`

A base view for displaying a single object. It is not intended to be used directly, but rather as a parent class of the [`django.views.generic.detail.DetailView`](#django.views.generic.detail.DetailView) or other views representing details of a single object.

**Ancestors (MRO)**

This view inherits methods and attributes from the following views:

*   [`django.views.generic.detail.SingleObjectMixin`](https://docs.djangoproject.com/en/5.2/mixins-single-object/#django.views.generic.detail.SingleObjectMixin)
*   [`django.views.generic.base.View`](https://docs.djangoproject.com/en/5.2/base/#django.views.generic.base.View)

**Methods**

`get`(request, *args, **kwargs)

Adds `object` to the context.

## `ListView`

*class* `django.views.generic.list.ListView`

A page representing a list of objects.

While this view is executing, `self.object_list` will contain the list of objects (usually, but not necessarily a queryset) that the view is operating upon.

**Ancestors (MRO)**

This view inherits methods and attributes from the following views:

*   [`django.views.generic.list.MultipleObjectTemplateResponseMixin`](https://docs.djangoproject.com/en/5.2/mixins-multiple-object/#django.views.generic.list.MultipleObjectTemplateResponseMixin)
*   [`django.views.generic.base.TemplateResponseMixin`](https://docs.djangoproject.com/en/5.2/mixins-simple/#django.views.generic.base.TemplateResponseMixin)
*   [`django.views.generic.list.BaseListView`](#django.views.generic.list.BaseListView)
*   [`django.views.generic.list.MultipleObjectMixin`](https://docs.djangoproject.com/en/5.2/mixins-multiple-object/#django.views.generic.list.MultipleObjectMixin)
*   [`django.views.generic.base.View`](https://docs.djangoproject.com/en/5.2/base/#django.views.generic.base.View)

**Method Flowchart**

1.  [`setup()`](https://docs.djangoproject.com/en/5.2/base/#django.views.generic.base.View.setup)
2.  [`dispatch()`](https://docs.djangoproject.com/en/5.2/base/#django.views.generic.base.View.dispatch)
3.  [`http_method_not_allowed()`](https://docs.djangoproject.com/en/5.2/base/#django.views.generic.base.View.http_method_not_allowed)
4.  [`get_template_names()`](https://docs.djangoproject.com/en/5.2/mixins-simple/#django.views.generic.base.TemplateResponseMixin.get_template_names)
5.  [`get_queryset()`](https://docs.djangoproject.com/en/5.2/mixins-multiple-object/#django.views.generic.list.MultipleObjectMixin.get_queryset)
6.  [`get_context_object_name()`](https://docs.djangoproject.com/en/5.2/mixins-multiple-object/#django.views.generic.list.MultipleObjectMixin.get_context_object_name)
7.  [`get_context_data()`](https://docs.djangoproject.com/en/5.2/mixins-multiple-object/#django.views.generic.list.MultipleObjectMixin.get_context_data)
8.  [`get()`](#django.views.generic.list.BaseListView.get)
9.  [`render_to_response()`](https://docs.djangoproject.com/en/5.2/mixins-simple/#django.views.generic.base.TemplateResponseMixin.render_to_response)

**Example views.py**:

```python
from django.utils import timezone
from django.views.generic.list import ListView
from articles.models import Article

class ArticleListView(ListView):
    model = Article
    paginate_by = 100  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context
```

**Example myapp/urls.py**:

```python
from django.urls import path
from article.views import ArticleListView

urlpatterns = [
    path("", ArticleListView.as_view(), name="article-list"),
]
```

**Example myapp/article\_list.html**:

```html
<h1>Articles</h1>
<ul>
{% for article in object_list %}
    <li>{{ article.pub_date|date }} - {{ article.headline }}</li>
{% empty %}
    <li>No articles yet.</li>
{% endfor %}
</ul>
```

If you’re using pagination, you can adapt the [example template from the pagination docs](https://docs.djangoproject.com/en/5.2/topics/pagination/#paginating-a-list-view).

*class* `django.views.generic.list.BaseListView`

A base view for displaying a list of objects. It is not intended to be used directly, but rather as a parent class of the [`django.views.generic.list.ListView`](#django.views.generic.list.ListView) or other views representing lists of objects.

**Ancestors (MRO)**

This view inherits methods and attributes from the following views:

*   [`django.views.generic.list.MultipleObjectMixin`](https://docs.djangoproject.com/en/5.2/mixins-multiple-object/#django.views.generic.list.MultipleObjectMixin)
*   [`django.views.generic.base.View`](https://docs.djangoproject.com/en/5.2/base/#django.views.generic.base.View)

**Methods**

`get`(request, *args, **kwargs)

Adds `object_list` to the context. If [`allow_empty`](https://docs.djangoproject.com/en/5.2/mixins-multiple-object/#django.views.generic.list.MultipleObjectMixin.allow_empty) is True then display an empty list. If [`allow_empty`](https://docs.djangoproject.com/en/5.2/mixins-multiple-object/#django.views.generic.list.MultipleObjectMixin.allow_empty) is False then raise a 404 error.