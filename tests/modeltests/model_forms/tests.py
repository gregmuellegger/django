import datetime
from django.test import TestCase
from django import forms
from django.forms.models import ModelForm, model_to_dict
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms
from models import Category, Writer, Book, DerivedBook, Post, FlexibleDatePost, Article
from mforms import (ProductForm, PriceForm, BookForm, DerivedBookForm,
                   ExplicitPKForm, PostForm, DerivedPostForm, CustomWriterForm,
                   FlexDatePostForm)


class BaseCategoryForm(ModelForm):
    class Meta:
        model = Category


class ExtraFields(BaseCategoryForm):
    some_extra_field = forms.BooleanField()


class ReplaceField(BaseCategoryForm):
    url = forms.BooleanField()


class LimitFields(ModelForm):
    class Meta:
        model = Category
        fields = ['url']


class ExcludeFields(ModelForm):
    class Meta:
        model = Category
        exclude = ['url']


class ConfusedForm(ModelForm):
    """ Using 'fields' *and* 'exclude'. Not sure why you'd want to do
    this, but uh, "be liberal in what you accept" and all.
    """
    class Meta:
        model = Category
        fields = ['name', 'url']
        exclude = ['url']


class MixModelForm(BaseCategoryForm):
    """ Don't allow more than one 'model' definition in the
    inheritance hierarchy.  Technically, it would generate a valid
    form, but the fact that the resulting save method won't deal with
    multiple objects is likely to trip up people not familiar with the
    mechanics.
    """
    class Meta:
        model = Article
    # MixModelForm is now an Article-related thing, because MixModelForm.Meta
    # overrides BaseCategoryForm.Meta.


class ArticleForm(ModelForm):
    class Meta:
        model = Article

#First class with a Meta class wins...
class BadForm(ArticleForm, BaseCategoryForm):
    pass


class WriterForm(ModelForm):
    book = forms.CharField(required=False)

    class Meta:
        model = Writer


class SubCategoryForm(BaseCategoryForm):
    """ Subclassing without specifying a Meta on the class will use
    the parent's Meta (or the first parent in the MRO if there are
    multiple parent classes).
    """
    pass

class SomeCategoryForm(ModelForm):
     checkbox = forms.BooleanField()

     class Meta:
         model = Category


class SubclassMeta(SomeCategoryForm):
    """ We can also subclass the Meta inner class to change the fields
    list.
    """
    class Meta(SomeCategoryForm.Meta):
        exclude = ['url']


class OrderFields(ModelForm):
    class Meta:
        model = Category
        fields = ['url', 'name']

class OrderFields2(ModelForm):
    class Meta:
        model = Category
        fields = ['slug', 'url', 'name']
        exclude = ['url']



class ModelFormBaseTest(TestCase):
    def test_base_form(self):
        self.assertEqual(BaseCategoryForm.base_fields.keys(),
                         ['name', 'slug', 'url'])

    def test_extra_fields(self):
        self.assertEqual(ExtraFields.base_fields.keys(),
                         ['name', 'slug', 'url', 'some_extra_field'])

    def test_replace_field(self):
        self.assertTrue(isinstance(ReplaceField.base_fields['url'],
                                     forms.fields.BooleanField))

    def test_override_field(self):
        wf = WriterForm({'name': 'Richard Lockridge'})
        self.assertTrue(wf.is_valid())

    def test_limit_fields(self):
        self.assertEqual(LimitFields.base_fields.keys(),
                         ['url'])

    def test_exclude_fields(self):
        self.assertEqual(ExcludeFields.base_fields.keys(),
                         ['name', 'slug'])

    def test_confused_form(self):
        self.assertEqual(ConfusedForm.base_fields.keys(),
                         ['name'])

    def test_mixmodel_form(self):
        self.assertEqual(
            MixModelForm.base_fields.keys(),
            ['headline', 'slug', 'pub_date', 'writer', 'article', 'categories', 'status']
            )

    def test_article_form(self):
        self.assertEqual(
            ArticleForm.base_fields.keys(),
            ['headline', 'slug', 'pub_date', 'writer', 'article', 'categories', 'status']
            )

    def test_bad_form(self):
        self.assertEqual(
            BadForm.base_fields.keys(),
            ['headline', 'slug', 'pub_date', 'writer', 'article', 'categories', 'status']
            )

    def test_subcategory_form(self):
        self.assertEqual(SubCategoryForm.base_fields.keys(),
                         ['name', 'slug', 'url'])

    def test_subclassmeta_form(self):
        self.assertEqual(
            str(SubclassMeta()),
            """<tr><th><label for="id_name">Name:</label></th><td><input id="id_name" type="text" name="name" maxlength="20" /></td></tr>
<tr><th><label for="id_slug">Slug:</label></th><td><input id="id_slug" type="text" name="slug" maxlength="20" /></td></tr>
<tr><th><label for="id_checkbox">Checkbox:</label></th><td><input type="checkbox" name="checkbox" id="id_checkbox" /></td></tr>"""
            )

    def test_orderfields_form(self):
        self.assertEqual(OrderFields.base_fields.keys(),
                         ['url', 'name'])
        self.assertEqual(
            str(OrderFields()),
            """<tr><th><label for="id_url">The URL:</label></th><td><input id="id_url" type="text" name="url" maxlength="40" /></td></tr>
<tr><th><label for="id_name">Name:</label></th><td><input id="id_name" type="text" name="name" maxlength="20" /></td></tr>"""
            )

    def test_orderfields2_form(self):
        self.assertEqual(OrderFields2.base_fields.keys(),
                         ['slug', 'name'])


class TestWidgetForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'url', 'slug']
        widgets = {
            'name': forms.Textarea,
            'url': forms.TextInput(attrs={'class': 'url'})
            }



class TestWidgets(TestCase):
    def test_base_widgets(self):
        frm = TestWidgetForm()
        self.assertEqual(
            str(frm['name']),
            '<textarea id="id_name" rows="10" cols="40" name="name"></textarea>'
            )
        self.assertEqual(
            str(frm['url']),
            '<input id="id_url" type="text" class="url" name="url" maxlength="40" />'
            )
        self.assertEqual(
            str(frm['slug']),
            '<input id="id_slug" type="text" name="slug" maxlength="20" />'
            )

    def test_x(self):
        pass


class IncompleteCategoryFormWithFields(forms.ModelForm):
    """
    A form that replaces the model's url field with a custom one. This should
    prevent the model field's validation from being called.
    """
    url = forms.CharField(required=False)

    class Meta:
        fields = ('name', 'slug')
        model = Category

class IncompleteCategoryFormWithExclude(forms.ModelForm):
    """
    A form that replaces the model's url field with a custom one. This should
    prevent the model field's validation from being called.
    """
    url = forms.CharField(required=False)

    class Meta:
        exclude = ['url']
        model = Category


class ValidationTest(TestCase):
    def test_validates_with_replaced_field_not_specified(self):
        form = IncompleteCategoryFormWithFields(data={'name': 'some name', 'slug': 'some-slug'})
        assert form.is_valid()

    def test_validates_with_replaced_field_excluded(self):
        form = IncompleteCategoryFormWithExclude(data={'name': 'some name', 'slug': 'some-slug'})
        assert form.is_valid()

    def test_notrequired_overrides_notblank(self):
        form = CustomWriterForm({})
        assert form.is_valid()




# unique/unique_together validation
class UniqueTest(TestCase):
    def setUp(self):
        self.writer = Writer.objects.create(name='Mike Royko')

    def test_simple_unique(self):
        form = ProductForm({'slug': 'teddy-bear-blue'})
        self.assertTrue(form.is_valid())
        obj = form.save()
        form = ProductForm({'slug': 'teddy-bear-blue'})
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['slug'], [u'Product with this Slug already exists.'])
        form = ProductForm({'slug': 'teddy-bear-blue'}, instance=obj)
        self.assertTrue(form.is_valid())

    def test_unique_together(self):
        """ModelForm test of unique_together constraint"""
        form = PriceForm({'price': '6.00', 'quantity': '1'})
        self.assertTrue(form.is_valid())
        form.save()
        form = PriceForm({'price': '6.00', 'quantity': '1'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['__all__'], [u'Price with this Price and Quantity already exists.'])

    def test_unique_null(self):
        title = 'I May Be Wrong But I Doubt It'
        form = BookForm({'title': title, 'author': self.writer.pk})
        self.assertTrue(form.is_valid())
        form.save()
        form = BookForm({'title': title, 'author': self.writer.pk})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['__all__'], [u'Book with this Title and Author already exists.'])
        form = BookForm({'title': title})
        self.assertTrue(form.is_valid())
        form.save()
        form = BookForm({'title': title})
        self.assertTrue(form.is_valid())

    def test_inherited_unique(self):
        title = 'Boss'
        Book.objects.create(title=title, author=self.writer, special_id=1)
        form = DerivedBookForm({'title': 'Other', 'author': self.writer.pk, 'special_id': u'1', 'isbn': '12345'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['special_id'], [u'Book with this Special id already exists.'])

    def test_inherited_unique_together(self):
        title = 'Boss'
        form = BookForm({'title': title, 'author': self.writer.pk})
        self.assertTrue(form.is_valid())
        form.save()
        form = DerivedBookForm({'title': title, 'author': self.writer.pk, 'isbn': '12345'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['__all__'], [u'Book with this Title and Author already exists.'])

    def test_abstract_inherited_unique(self):
        title = 'Boss'
        isbn = '12345'
        dbook = DerivedBook.objects.create(title=title, author=self.writer, isbn=isbn)
        form = DerivedBookForm({'title': 'Other', 'author': self.writer.pk, 'isbn': isbn})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['isbn'], [u'Derived book with this Isbn already exists.'])

    def test_abstract_inherited_unique_together(self):
        title = 'Boss'
        isbn = '12345'
        dbook = DerivedBook.objects.create(title=title, author=self.writer, isbn=isbn)
        form = DerivedBookForm({'title': 'Other', 'author': self.writer.pk, 'isbn': '9876', 'suffix1': u'0', 'suffix2': u'0'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['__all__'], [u'Derived book with this Suffix1 and Suffix2 already exists.'])

    def test_explicitpk_unspecified(self):
        """Test for primary_key being in the form and failing validation."""
        form = ExplicitPKForm({'key': u'', 'desc': u'' })
        self.assertFalse(form.is_valid())

    def test_explicitpk_unique(self):
        """Ensure keys and blank character strings are tested for uniqueness."""
        form = ExplicitPKForm({'key': u'key1', 'desc': u''})
        self.assertTrue(form.is_valid())
        form.save()
        form = ExplicitPKForm({'key': u'key1', 'desc': u''})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)
        self.assertEqual(form.errors['__all__'], [u'Explicit pk with this Key and Desc already exists.'])
        self.assertEqual(form.errors['desc'], [u'Explicit pk with this Desc already exists.'])
        self.assertEqual(form.errors['key'], [u'Explicit pk with this Key already exists.'])

    def test_unique_for_date(self):
        p = Post.objects.create(title="Django 1.0 is released",
            slug="Django 1.0", subtitle="Finally", posted=datetime.date(2008, 9, 3))
        form = PostForm({'title': "Django 1.0 is released", 'posted': '2008-09-03'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['title'], [u'Title must be unique for Posted date.'])
        form = PostForm({'title': "Work on Django 1.1 begins", 'posted': '2008-09-03'})
        self.assertTrue(form.is_valid())
        form = PostForm({'title': "Django 1.0 is released", 'posted': '2008-09-04'})
        self.assertTrue(form.is_valid())
        form = PostForm({'slug': "Django 1.0", 'posted': '2008-01-01'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['slug'], [u'Slug must be unique for Posted year.'])
        form = PostForm({'subtitle': "Finally", 'posted': '2008-09-30'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subtitle'], [u'Subtitle must be unique for Posted month.'])
        form = PostForm({'subtitle': "Finally", "title": "Django 1.0 is released",
            "slug": "Django 1.0", 'posted': '2008-09-03'}, instance=p)
        self.assertTrue(form.is_valid())
        form = PostForm({'title': "Django 1.0 is released"})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['posted'], [u'This field is required.'])

    def test_inherited_unique_for_date(self):
        p = Post.objects.create(title="Django 1.0 is released",
            slug="Django 1.0", subtitle="Finally", posted=datetime.date(2008, 9, 3))
        form = DerivedPostForm({'title': "Django 1.0 is released", 'posted': '2008-09-03'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['title'], [u'Title must be unique for Posted date.'])
        form = DerivedPostForm({'title': "Work on Django 1.1 begins", 'posted': '2008-09-03'})
        self.assertTrue(form.is_valid())
        form = DerivedPostForm({'title': "Django 1.0 is released", 'posted': '2008-09-04'})
        self.assertTrue(form.is_valid())
        form = DerivedPostForm({'slug': "Django 1.0", 'posted': '2008-01-01'})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors['slug'], [u'Slug must be unique for Posted year.'])
        form = DerivedPostForm({'subtitle': "Finally", 'posted': '2008-09-30'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['subtitle'], [u'Subtitle must be unique for Posted month.'])
        form = DerivedPostForm({'subtitle': "Finally", "title": "Django 1.0 is released",
            "slug": "Django 1.0", 'posted': '2008-09-03'}, instance=p)
        self.assertTrue(form.is_valid())

    def test_unique_for_date_with_nullable_date(self):
        p = FlexibleDatePost.objects.create(title="Django 1.0 is released",
            slug="Django 1.0", subtitle="Finally", posted=datetime.date(2008, 9, 3))

        form = FlexDatePostForm({'title': "Django 1.0 is released"})
        self.assertTrue(form.is_valid())
        form = FlexDatePostForm({'slug': "Django 1.0"})
        self.assertTrue(form.is_valid())
        form = FlexDatePostForm({'subtitle': "Finally"})
        self.assertTrue(form.is_valid())
        form = FlexDatePostForm({'subtitle': "Finally", "title": "Django 1.0 is released",
            "slug": "Django 1.0"}, instance=p)
        self.assertTrue(form.is_valid())

class OldFormForXTests(TestCase):
    def test_base_form(self):
        self.assertEqual(Category.objects.count(), 0)
        f = BaseCategoryForm()
        self.assertEqual(
            str(f),
            """<tr><th><label for="id_name">Name:</label></th><td><input id="id_name" type="text" name="name" maxlength="20" /></td></tr>
<tr><th><label for="id_slug">Slug:</label></th><td><input id="id_slug" type="text" name="slug" maxlength="20" /></td></tr>
<tr><th><label for="id_url">The URL:</label></th><td><input id="id_url" type="text" name="url" maxlength="40" /></td></tr>"""
            )
        self.assertEqual(
            str(f.as_ul()),
            """<li><label for="id_name">Name:</label> <input id="id_name" type="text" name="name" maxlength="20" /></li>
<li><label for="id_slug">Slug:</label> <input id="id_slug" type="text" name="slug" maxlength="20" /></li>
<li><label for="id_url">The URL:</label> <input id="id_url" type="text" name="url" maxlength="40" /></li>"""
            )
        self.assertEqual(
            str(f["name"]),
            """<input id="id_name" type="text" name="name" maxlength="20" />""")

    def test_auto_id(self):
        f = BaseCategoryForm(auto_id=False)
        self.assertEqual(
            str(f.as_ul()),
            """<li>Name: <input type="text" name="name" maxlength="20" /></li>
<li>Slug: <input type="text" name="slug" maxlength="20" /></li>
<li>The URL: <input type="text" name="url" maxlength="40" /></li>"""
            )

    def test_with_data(self):
        self.assertEqual(Category.objects.count(), 0)
        f = BaseCategoryForm({'name': 'Entertainment',
                              'slug': 'entertainment',
                              'url': 'entertainment'})
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data['name'], 'Entertainment')
        self.assertEqual(f.cleaned_data['slug'], 'entertainment')
        self.assertEqual(f.cleaned_data['url'], 'entertainment')
        c1 = f.save()
        # Testing wether the same object is returned from the
        # ORM... not the fastest way...

        self.assertEqual(c1, Category.objects.all()[0])
        self.assertEqual(c1.name, "Entertainment")
        self.assertEqual(Category.objects.count(), 1)

        f = BaseCategoryForm({'name': "It's a test",
                              'slug': 'its-test',
                              'url': 'test'})
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data['name'], "It's a test")
        self.assertEqual(f.cleaned_data['slug'], 'its-test')
        self.assertEqual(f.cleaned_data['url'], 'test')
        c2 = f.save()
        # Testing wether the same object is returned from the
        # ORM... not the fastest way...
        self.assertEqual(c2, Category.objects.get(pk=c2.pk))
        self.assertEqual(c2.name, "It's a test")
        self.assertEqual(Category.objects.count(), 2)
