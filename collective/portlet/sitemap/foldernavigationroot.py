# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContainer
from plone.autoform import directives
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from zope.interface import alsoProvides, noLongerProvides
from zope import schema
from zope.schema._bootstrapinterfaces import IFromBytes
from zope.schema._bootstrapinterfaces import IFromUnicode
from zope.interface import Interface
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from plone.app.dexterity import _


@provider(IFormFieldProvider)
class IRootNavigationPortlet(model.Schema):
    
    model.fieldset(
        'settings',
        label=_(u"Settings"),
        fields=['portlet_nav_root', 'portlet_nav_root_title']
    )
    
    portlet_nav_root = schema.Bool(
        title=_(
            u'label_portlet_nav_root',
            default=u'Navigation root'
        ),
        description=_(
            u"help_portlet_nav_root",
            default=u"Use as root of the navigation tree"
        ),
        required=False,
    )
    directives.omitted('portlet_nav_root')
    directives.no_omit(IEditForm, 'portlet_nav_root')
    directives.no_omit(IAddForm, 'portlet_nav_root')
    
    portlet_nav_root_title = schema.TextLine(
        title=_(
            u'label_portlet_nav_root_title',
            default=u'Navigation root title'
        ),
        description=_(
            u"help_portlet_nav_root_title",
            default=u"if selected, use this as title "
                     "of the navigation root, instead of content title"
        ),
        required=False,
    )
    directives.omitted('portlet_nav_root_title')
    directives.no_omit(IEditForm, 'portlet_nav_root_title')
    directives.no_omit(IAddForm, 'portlet_nav_root_title')

