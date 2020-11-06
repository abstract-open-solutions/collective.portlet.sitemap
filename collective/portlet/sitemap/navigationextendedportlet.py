from Acquisition import aq_base, aq_parent
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts, getMultiAdapter
from plone.memoize.instance import memoize
from plone.app.portlets.portlets import navigation
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.uuid.utils import uuidToObject
from zope import schema
from zope.formlib import form
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import utils
from collective.portlet.sitemap import NavigationExtendedPortletMessageFactory as _
from plone.app.uuid.utils import uuidToObject
from zope.component.hooks import getSite
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
from zope.interface import implementer


class INavigationExtendedPortlet(navigation.INavigationPortlet) :
    """A portlet

    It inherits from INavigationPortlet
    """
    displayAsSiteMap = schema.Bool(
            title=_(u"label_display_as_site_map", default=u"Display as Site Map"),
            description=_(u"help_display_as_site_map",
                          default=u"If checked display all folders as a site map"),
            default=True,
            required=False)
            
    siteMapDepth = schema.Int(
            title=_(u"label_site_map_depth",
                    default=u"Site map depth"),
            description=_(u"help_site_map_depth",
                          default=u"If previous field is checked set the site map depth"),
            default=2,
            required=False)  
    
    css_class = schema.TextLine(title=_(
            u"Classe CSS"),
            description=_(u"Se indicata, viene aggiunta al markup, allo stesso livello della classe: portlet."),
            required=False)

class Assignment(navigation.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(INavigationExtendedPortlet)
    
    name = u''
    root = None
    root_uid = None
    currentFolderOnly = False
    includeTop = False
    topLevel = 1
    bottomLevel = 0
    no_icons = False
    thumb_scale = None
    no_thumbs = False
    displayAsSiteMap = True
    siteMapDepth = 2
    css_class = u''
    
    
    def __init__(
            self,
            name="",
            root_uid=None,
            currentFolderOnly=False,
            includeTop=False,
            topLevel=1,
            bottomLevel=0,
            no_icons=False,
            thumb_scale=None,
            no_thumbs=False,
            displayAsSiteMap=True,
            siteMapDepth = 2,
            css_class = u'',
    ):
        super(Assignment, self).__init__(
            name,
            root_uid,
            currentFolderOnly,
            includeTop,
            topLevel,
            bottomLevel,
            no_icons,
            thumb_scale,
            no_thumbs
        )
        self.displayAsSiteMap = displayAsSiteMap    
        self.siteMapDepth = siteMapDepth
        self.css_class = css_class
    
    @property
    def title(self):
        """
        Display the name in portlet mngmt interface
        """
        if self.name:
            return self.name
        return _(u'Navigation Extended')



class Renderer(navigation.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    
    @memoize
    def getNavRootPath(self):
        if self.data.root_uid:
            if uuidToObject(self.data.root_uid):
                return navigation.getRootPath(
                   self.context,
                   self.data.currentFolderOnly,
                   self.data.topLevel,
                   self.data.root_uid
                )
            return None
        
        root_uid = self.data.root_uid
        root = getNavigationFolderObject(self.context, getSite())
        if root:
            root_uid = root.UID()
        
        return navigation.getRootPath(
                   self.context,
                   self.data.currentFolderOnly,
                   self.data.topLevel,
                   root_uid
                )
    
    def heading_link_target(self):
        root = getNavigationFolderObject(self.context, getSite())
        if not self.data.root_uid and root:
            return root.absolute_url()
        return super(Renderer, self).heading_link_target()
    
    def title(self):
        root = getNavigationFolderObject(self.context, getSite())
        title = self.data.name
        if not self.data.root_uid and getattr(root, 'portlet_nav_root', False):
            return getattr(root, 'portlet_nav_root_title', title)
        return title
    
    def root_title(self):
        root = self.getNavRoot()
        title = root.Title()
        if getattr(root, 'portlet_nav_root', False):
            return getattr(root, 'portlet_nav_root_title', title)
        return title
    
    
    def hasName(self):
        title = self.title()
        if self.include_top():
            return False
        return title
        
    @memoize
    def getNavTree(self, _marker=[]):
        if _marker is None:
            _marker = []
            
        context = aq_inner(self.context)
        
        # Special case - if the root is supposed to be pruned, we need to
        # abort here
        queryBuilder = getMultiAdapter((context, self.data), INavigationExtendedQueryBuilder)
        strategy = getMultiAdapter((context, self.data), INavtreeExtendedStrategy)
        return buildFolderTree(context, obj=context, query=queryBuilder(), strategy=strategy)
    
    _template = ViewPageTemplateFile('navigation_extended.pt')
    recurse = ViewPageTemplateFile('navigation_extended_recurse.pt')


class AddForm(navigation.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    schema = INavigationExtendedPortlet

    def create(self, data):
        return Assignment(name=data.get('name', u""),
                          root_uid=data.get('root_uid', ""),
                          currentFolderOnly=data.get('currentFolderOnly', False),
                          includeTop=data.get('includeTop', False),
                          topLevel=data.get('topLevel', 0),
                          bottomLevel=data.get('bottomLevel', 0),
                          displayAsSiteMap=data.get('displayAsSiteMap', True),
                          siteMapDepth=data.get('siteMapDepth', 2),
                          css_class=data.get('css_class', u''))



class EditForm(navigation.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    schema = INavigationExtendedPortlet


class INavigationExtendedQueryBuilder(INavigationQueryBuilder):
    """An object which returns a catalog query when called, used to 
    construct a navigation tree.
    """
    
    def __call__():
        """Returns a mapping describing a catalog query used to build a
           navigation structure.
        """    


class NavigationExtendedQueryBuilder(object):
    """Build a navtree query based on the settings in navtree_properties
    and those set on the portlet.
    """
    implements(INavigationExtendedQueryBuilder)
    adapts(Interface, INavigationExtendedPortlet)

    def __init__(self, context, portlet):
        self.context = context
        self.portlet = portlet
        
        portal_properties = utils.getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        
        portal_url = utils.getToolByName(context, 'portal_url')
        
        # Acquire a custom nav query if available
        customQuery = getattr(context, 'getCustomNavQuery', None)
        if customQuery is not None and utils.safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}
        
        # Construct the path query
        root_uid = portlet.root_uid
        if not root_uid:
            folderRoot = getNavigationFolderObject(context, getSite())
            if folderRoot:
                root_uid = folderRoot.UID()
        
        root = uuidToObject(root_uid)
        if root is not None:
            rootPath = '/'.join(root.getPhysicalPath())
        else:
            rootPath = getNavigationRoot(context)
        currentPath = '/'.join(context.getPhysicalPath())

        # If we are above the navigation root, a navtree query would return
        # nothing (since we explicitly start from the root always). Hence,
        # use a regular depth-1 query in this case.

        if portlet.displayAsSiteMap :
            if not currentPath.startswith(rootPath) or portlet.root_uid:
                query['path'] = {'query' : rootPath, 'depth' : portlet.siteMapDepth}
            else:
                query['path'] = {'query' : currentPath, 'navtree' : portlet.siteMapDepth}  
        else :
            if not currentPath.startswith(rootPath):
                query['path'] = {'query' : rootPath, 'depth' : 1}
            else:
                query['path'] = {'query' : currentPath, 'navtree' : 1}
                
        topLevel = portlet.topLevel or navtree_properties.getProperty('topLevel', 0)
        if topLevel and topLevel > 0:
             query['path']['navtree_start'] = topLevel + 1
        # XXX: It'd make sense to use 'depth' for bottomLevel, but it doesn't
        # seem to work with EPI.

        # Only list the applicable types
        query['portal_type'] = utils.typesToList(context)

        # Apply the desired sort
        sortAttribute = navtree_properties.getProperty('sortAttribute', None)
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute
            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                query['sort_order'] = sortOrder

        # Filter on workflow states, if enabled
        if navtree_properties.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = navtree_properties.getProperty('wf_states_to_show', ())

        self.query = query

    def __call__(self):
        return self.query


class INavtreeExtendedStrategy(INavtreeStrategy):
    """An object that is used by buildFolderTree() to determine how to
    construct a navigation tree.
    """
    

@implementer(INavtreeExtendedStrategy)
class NavtreeExtendedStrategy(navigation.NavtreeStrategy):
    """The navtree strategy used for the default navigation portlet
    """
    adapts(Interface, INavigationExtendedPortlet)

    def __init__(self, context, portlet):
        SitemapNavtreeStrategy.__init__(self, context, portlet)

        # XXX: We can't do this with a 'depth' query to EPI...
        self.bottomLevel = portlet.bottomLevel or 0
        
        root_uid = portlet.root_uid
        if not root_uid:
            root = getNavigationFolderObject(self.context, getSite())
            if root:
                root_uid = root.UID()
            
        self.rootPath = navigation.getRootPath(context,
                                    portlet.currentFolderOnly,
                                    portlet.topLevel,
                                    root_uid)
            
            
def getNavigationFolderObject(context, portal):
        obj = context
        while (not getattr(obj, 'portlet_nav_root', False) and
                aq_base(obj) is not aq_base(portal)):
            parent = aq_parent(aq_inner(obj))
            if parent is None:
                return None
            obj = parent
        if aq_base(obj) is aq_base(portal):
            return None
        return obj

