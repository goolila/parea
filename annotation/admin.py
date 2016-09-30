from django.contrib import admin

from annotation.models import Annotation, Range

class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'user_id', 'uri', 'quote', 'created')

class RangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'paper_id', 'start', 'end', 'startOffset', 'endOffset', 'annotation_text', 'annotation_quote')

    def annotation_text(self, obj):
        return obj.annotation.text[:100]

    def annotation_quote(self, obj):
        return obj.annotation.quote[:100]

    def paper_id(self, obj):
        uri = obj.annotation.uri
        paper_id = uri[29:]
        return paper_id

admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Range, RangeAdmin)
