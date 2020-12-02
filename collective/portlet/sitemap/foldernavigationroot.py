# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform import directives
from plone.supermodel import model
from zope.interface import provider
from zope import schema
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from plone.app.dexterity import _
from plone.app.portlets import PloneMessageFactory as _navigation


@provider(IFormFieldProvider)
class IRootNavigationPortlet(model.Schema):
    
    model.fieldset(
        'navigation',
        label=_(u"Navigation"),
        fields=['portlet_nav_root', 'portlet_nav_root_title',
                'portlet_nav_topLevel',
        ]
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
    
    portlet_nav_topLevel = schema.Int(
        title=_navigation(u"label_navigation_startlevel", default=u"Start level"),
        description=_navigation(u"help_navigation_start_level",
            default=u"An integer value that specifies the number of folder "
                     "levels below the site root that must be exceeded "
                     "before the navigation tree will display. 0 means "
                     "that the navigation tree should be displayed "
                     "everywhere including pages in the root of the site. "
                     "1 means the tree only shows up inside folders "
                     "located in the root and downwards, never showing "
                     "at the top level."),
        required=False,
    )
    
    directives.omitted(
        'portlet_nav_root', 'portlet_nav_root_title', 'portlet_nav_topLevel'
    )
    directives.no_omit(
        IEditForm, 'portlet_nav_root', 'portlet_nav_root_title',
        'portlet_nav_topLevel'
    )
    directives.no_omit(
        IEditForm, 'portlet_nav_root', 'portlet_nav_root_title',
        'portlet_nav_topLevel'
    )
