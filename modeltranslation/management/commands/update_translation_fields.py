# -*- coding: utf-8 -*-
from django.db.models import F, Q
from django.core.management.base import NoArgsCommand

from modeltranslation.settings import DEFAULT_LANGUAGE
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname


class Command(NoArgsCommand):
    help = ('Updates empty values of default translation fields using'
            ' values from original fields (in all translated models).')

    def handle_noargs(self, **options):
        verbosity = int(options['verbosity'])
        if verbosity > 0:
            self.stdout.write("Using default language: %s\n" % DEFAULT_LANGUAGE)
        models = translator.get_registered_models(abstract=False)
        for model in models:
            if verbosity > 0:
                self.stdout.write("Updating data of model '%s'\n" % model)
            opts = translator.get_options_for_model(model)
            for field_name in opts.fields.iterkeys():
                def_lang_fieldname = build_localized_fieldname(field_name, DEFAULT_LANGUAGE)
                q = Q()
                field = model._meta.get_field(field_name)
                for x in model.objects.filter(q).rewrite(False):
                  current_foreign_value = getattr(x, field_name)
                  if current_foreign_value == None or  (field.empty_strings_allowed and current_foreign_value == ""):
                    setattr(x, def_lang_fieldname, getattr(x, field_name))
                    x.save()
