from zope.interface import Interface
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool
from zope.schema import Choice
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.controlpanel import PloneMessageFactory as _
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.utils import SchemaAdapterBase
from plone.app.controlpanel.widgets import DropdownChoiceWidget


ICON_VISIBILITY_CHOICES = {
    _(u"Only for users who are logged in"): 'authenticated',
    _(u"Never show icons"): 'disabled',
    _(u"Always show icons"): 'enabled',
}

ICON_VISIBILITY_VOCABULARY = SimpleVocabulary(
    [SimpleTerm(v, v, k) for k, v in ICON_VISIBILITY_CHOICES.items()]
    )


class ISkinsSchema(Interface):

    theme = Choice(title=_(u'Default theme'),
                  description=_(u'''Select the default theme for the site.'''),
                  required=True,
                  missing_value=tuple(),
                  vocabulary="plone.app.vocabularies.Skins")

    mark_special_links = Bool(title=_(u'Mark external links'),
                              description=_(u"If enabled all external links "
                                             "will be marked with link type "
                                             "specific icons. If disabled "
                                             "the 'external links open in new "
                                             "window' setting has no effect."),
                              default=True)

    ext_links_open_new_window = Bool(title=_(u"External links open in new "
                                              "window"),
                                     description=_(u"If enabled all external "
                                                    "links in the content "
                                                    "region open in a new "
                                                    "window."),
                                     default=False)

    icon_visibility = Choice(title=_(u'Show content type icons'),
                             description=_(u"If disabled the content icons "
                                            "in folder listings and portlets "
                                            "won't be visible."),
                             vocabulary=ICON_VISIBILITY_VOCABULARY)


class SkinsControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ISkinsSchema)

    def __init__(self, context):
        super(SkinsControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'portal_skins')
        self.jstool = getToolByName(context, 'portal_javascripts')
        ptool = getToolByName(context, 'portal_properties')
        self.props = ptool.site_properties

    def get_theme(self):
        return self.context.getDefaultSkin()

    def set_theme(self, value):
        self.context.default_skin = value

    theme = property(get_theme, set_theme)

    def get_mark_special_links(self):
        return self.jstool.getResource('mark_special_links.js').getEnabled()

    def set_mark_special_links(self, value):
        if value:
            self.jstool.getResource('mark_special_links.js').setEnabled(True)
        else:
            self.jstool.getResource('mark_special_links.js').setEnabled(False)
        self.jstool.cookResources()

    mark_special_links = property(get_mark_special_links,
                                  set_mark_special_links)

    def get_ext_links_open_new_window(self):
        elonw = self.props.external_links_open_new_window
        if elonw == 'true':
            return True
        return False

    def set_ext_links_open_new_window(self, value):
        if value:
            self.props.manage_changeProperties(external_links_open_new_window='true')
        else:
            self.props.manage_changeProperties(external_links_open_new_window='false')
        self.jstool.cookResources()

    ext_links_open_new_window = property(get_ext_links_open_new_window,
                                         set_ext_links_open_new_window)

    def get_icon_visibility(self):
        return self.props.icon_visibility

    def set_icon_visibility(self, value):
        self.props.manage_changeProperties(icon_visibility=value)

    icon_visibility = property(get_icon_visibility,set_icon_visibility)


class SkinsControlPanel(ControlPanelForm):

    form_fields = FormFields(ISkinsSchema)
    form_fields['theme'].custom_widget = DropdownChoiceWidget

    label = _("Theme settings")
    description = _("Settings that affect the site's look and feel.")
    form_name = _("Theme settings")
