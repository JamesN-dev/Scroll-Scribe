# Built-In Class-Based Views Api

Class-based views API reference. For introductory material, see the [Class-based views](https://docs.djangoproject.com/en/5.2/topics/class-based-views/) topic guide.

*   [Base views](base/)
    *   [`View`](base/#view)
    *   [`TemplateView`](base/#templateview)
    *   [`RedirectView`](base/#redirectview)
*   [Generic display views](generic-display/)
    *   [`DetailView`](generic-display/#detailview)
    *   [`ListView`](generic-display/#listview)
*   [Generic editing views](generic-editing/)
    *   [`FormView`](generic-editing/#formview)
    *   [`CreateView`](generic-editing/#createview)
    *   [`UpdateView`](generic-editing/#updateview)
    *   [`DeleteView`](generic-editing/#deleteview)
*   [Generic date views](generic-date-based/)
    *   [`ArchiveIndexView`](generic-date-based/#archiveindexview)
    *   [`YearArchiveView`](generic-date-based/#yeararchiveview)
    *   [`MonthArchiveView`](generic-date-based/#montharchiveview)
    *   [`WeekArchiveView`](generic-date-based/#weekarchiveview)
    *   [`DayArchiveView`](generic-date-based/#dayarchiveview)
    *   [`TodayArchiveView`](generic-date-based/#todayarchiveview)
    *   [`DateDetailView`](generic-date-based/#datedetailview)
*   [Class-based views mixins](mixins/)
    *   [Simple mixins](mixins-simple/)
        *   [`ContextMixin`](mixins-simple/#contextmixin)
        *   [`TemplateResponseMixin`](mixins-simple/#templateresponsemixin)
    *   [Single object mixins](mixins-single-object/)
        *   [`SingleObjectMixin`](mixins-single-object/#singleobjectmixin)
        *   [`SingleObjectTemplateResponseMixin`](mixins-single-object/#singleobjecttemplateresponsemixin)
    *   [Multiple object mixins](mixins-multiple-object/)
        *   [`MultipleObjectMixin`](mixins-multiple-object/#multipleobjectmixin)
        *   [`MultipleObjectTemplateResponseMixin`](mixins-multiple-object/#multipleobjecttemplateresponsemixin)
    *   [Editing mixins](mixins-editing/)
        *   [`FormMixin`](mixins-editing/#formmixin)
        *   [`ModelFormMixin`](mixins-editing/#modelformmixin)
        *   [`ProcessFormView`](mixins-editing/#processformview)
        *   [`DeletionMixin`](mixins-editing/#deletionmixin)
    *   [Date-based mixins](mixins-date-based/)
        *   [`YearMixin`](mixins-date-based/#yearmixin)
        *   [`MonthMixin`](mixins-date-based/#monthmixin)
        *   [`DayMixin`](mixins-date-based/#daymixin)
        *   [`WeekMixin`](mixins-date-based/#weekmixin)
        *   [`DateMixin`](mixins-date-based/#datemixin)
        *   [`BaseDateListView`](mixins-date-based/#basedatelistview)
*   [Class-based generic views - flattened index](flattened-index/)
    *   [Simple generic views](flattened-index/#simple-generic-views)
        *   [`View`](flattened-index/#view)
        *   [`TemplateView`](flattened-index/#templateview)
        *   [`RedirectView`](flattened-index/#redirectview)
    *   [Detail Views](flattened-index/#detail-views)
        *   [`DetailView`](flattened-index/#detailview)
    *   [List Views](flattened-index/#list-views)
        *   [`ListView`](flattened-index/#listview)
    *   [Editing views](flattened-index/#editing-views)
        *   [`FormView`](flattened-index/#formview)
        *   [`CreateView`](flattened-index/#createview)
        *   [`UpdateView`](flattened-index/#updateview)
        *   [`DeleteView`](flattened-index/#deleteview)
    *   [Date-based views](flattened-index/#date-based-views)
        *   [`ArchiveIndexView`](flattened-index/#archiveindexview)
        *   [`YearArchiveView`](flattened-index/#yeararchiveview)
        *   [`MonthArchiveView`](flattened-index/#montharchiveview)
        *   [`WeekArchiveView`](flattened-index/#weekarchiveview)
        *   [`DayArchiveView`](flattened-index/#dayarchiveview)
        *   [`TodayArchiveView`](flattened-index/#todayarchiveview)
        *   [`DateDetailView`](flattened-index/#datedetailview)

## Specification

Each request served by a class-based view has an independent state; therefore, it is safe to store state variables on the instance (i.e., `self.foo = 3` is a thread-safe operation).

A class-based view is deployed into a URL pattern using the [`as_view()`](base/#django.views.generic.base.View.as_view) classmethod:

```
urlpatterns = [
    path("view/", MyView.as_view(size=42)),
]
```

> Thread safety with view arguments
>
> Arguments passed to a view are shared between every instance of a view. This means that you shouldn’t use a list, dictionary, or any other mutable object as an argument to a view. If you do and the shared object is modified, the actions of one user visiting your view could have an effect on subsequent users visiting the same view.

Arguments passed into [`as_view()`](base/#django.views.generic.base.View.as_view) will be assigned onto the instance that is used to service a request. Using the previous example, this means that every request on `MyView` is able to use `self.size`. Arguments must correspond to attributes that already exist on the class (return `True` on a `hasattr` check).

## Base Vs Generic Views

Base class-based views can be thought of as *parent* views, which can be used by themselves or inherited from. They may not provide all the capabilities required for projects, in which case there are Mixins which extend what base views can do.

Django’s generic views are built off of those base views, and were developed as a shortcut for common usage patterns such as displaying the details of an object. They take certain common idioms and patterns found in view development and abstract them so that you can quickly write common views of data without having to repeat yourself.

Most generic views require the `queryset` key, which is a `QuerySet` instance; see [Making queries](https://docs.djangoproject.com/en/5.2/topics/db/queries/) for more information about `QuerySet` objects.