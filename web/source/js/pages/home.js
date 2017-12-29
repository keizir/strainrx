'use strict';

W.ns('W.pages');

W.pages.HomePage = Class.extend({

    init: function init(options) {
        this.location = options && options.location;
        this.authenticated = options && options.authenticated;
        this.userId = options && options.userId;

        this.initStrainLookupField();
        this.enterSearchWizard();
    },

    initStrainLookupField: function initStrainLookupField() {
        var lookupTemplate = _.template($('#strain-lookup-field').html());
        $('.strain-name-field').html(lookupTemplate({
            'lookup_placeholder': 'Example: Blue Dream, Maiu Wowie, Pineapple express'
        }));
        new W.pages.strain.StrainLookup({ onSelect: this.navigateToStrainDetailPage });
    },

    navigateToStrainDetailPage: function navigateToStrainDetailPage(selected) {
        if (selected.variety && selected.slug) {
            window.location.href = '/strains/{0}/{1}/'.format(selected.variety, selected.slug);
        }
    },

    enterSearchWizard: function enterSearchWizard() {
        if (AUTHENTICATED && !EMAIL_VERIFIED) {
            $('.btn-lets-go').on('click', function (e) {
                e.preventDefault();
                W.common.VerifyEmailDialog();
            });
        }
    }
});
